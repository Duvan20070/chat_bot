"""
Servicio de Ollama (asíncrono, con streaming).

Mejoras frente a la versión anterior:
- Cliente async único y reutilizado (no se abre una conexión por mensaje).
- Streaming token a token: la primera palabra aparece en menos de un segundo.
- Recibe una lista de mensajes con roles (system / user / assistant).
- keep_alive para que el modelo no se descargue de memoria.
- Semáforo para no saturar el hardware con muchas generaciones a la vez.
- Errores controlados con OllamaError.
"""

import asyncio
import logging
from typing import AsyncIterator, Optional

import httpx
from ollama import AsyncClient, ResponseError

from app.config import settings

logger = logging.getLogger("volleyscan.ollama")


class OllamaError(Exception):
    """Error al comunicarse con Ollama (apagado, modelo no existe, timeout...)."""


_cliente: Optional[AsyncClient] = None
_semaforo = asyncio.Semaphore(settings.OLLAMA_MAX_CONCURRENTES)


def obtener_cliente() -> AsyncClient:
    """Devuelve el cliente compartido, creándolo la primera vez."""
    global _cliente
    if _cliente is None:
        _cliente = AsyncClient(
            host=settings.OLLAMA_HOST,
            timeout=settings.OLLAMA_TIMEOUT,
        )
    return _cliente


async def cerrar_cliente() -> None:
    """Se llama al apagar el servidor para liberar conexiones."""
    global _cliente
    if _cliente is not None:
        # AsyncClient guarda un httpx.AsyncClient interno en _client
        await _cliente._client.aclose()
        _cliente = None


def _opciones(extra: Optional[dict] = None) -> dict:
    opciones = {
        "num_ctx": settings.NUM_CTX,
        "num_predict": settings.NUM_PREDICT,
        "temperature": settings.TEMPERATURE,
        "top_p": settings.TOP_P,
        "repeat_penalty": settings.REPEAT_PENALTY,
    }
    if extra:
        opciones.update(extra)
    return opciones


def _traducir_error(error: Exception) -> OllamaError:
    if isinstance(error, (httpx.ConnectError, ConnectionError)):
        return OllamaError(
            "No se pudo conectar con Ollama. Verifica que esté en ejecución."
        )
    if isinstance(error, httpx.TimeoutException):
        return OllamaError("Ollama tardó demasiado en responder.")
    if isinstance(error, ResponseError):
        if getattr(error, "status_code", None) == 404:
            return OllamaError(
                f"El modelo '{settings.OLLAMA_MODELO}' no está descargado. "
                f"Ejecuta: ollama pull {settings.OLLAMA_MODELO}"
            )
        return OllamaError(f"Ollama devolvió un error: {error}")
    return OllamaError(f"Error inesperado con Ollama: {error}")


async def calentar_modelo() -> None:
    """
    Carga el modelo en memoria al arrancar el servidor.
    Así el primer mensaje del entrenador no paga el tiempo de carga.
    Si falla no es grave: se cargará en la primera petición.
    """
    try:
        await obtener_cliente().chat(
            model=settings.OLLAMA_MODELO,
            messages=[],
            keep_alive=settings.OLLAMA_KEEP_ALIVE,
        )
        logger.info("Modelo %s cargado en memoria", settings.OLLAMA_MODELO)
    except Exception as error:
        logger.warning("No se pudo precalentar el modelo: %s", error)


async def generar_stream(
    mensajes: list[dict],
    opciones: Optional[dict] = None,
) -> AsyncIterator[str]:
    """Genera la respuesta token a token."""
    async with _semaforo:
        try:
            stream = await obtener_cliente().chat(
                model=settings.OLLAMA_MODELO,
                messages=mensajes,
                stream=True,
                keep_alive=settings.OLLAMA_KEEP_ALIVE,
                options=_opciones(opciones),
            )
            async for parte in stream:
                token = parte.message.content
                if token:
                    yield token
        except OllamaError:
            raise
        except Exception as error:
            logger.exception("Fallo en generar_stream")
            raise _traducir_error(error) from error


async def generar(
    mensajes: list[dict],
    opciones: Optional[dict] = None,
    modelo: Optional[str] = None,
    reintentos: int = 1,
) -> str:
    """Genera la respuesta completa (sin streaming), con un reintento."""
    ultimo_error: Optional[OllamaError] = None

    for intento in range(reintentos + 1):
        async with _semaforo:
            try:
                respuesta = await obtener_cliente().chat(
                    model=modelo or settings.OLLAMA_MODELO,
                    messages=mensajes,
                    keep_alive=settings.OLLAMA_KEEP_ALIVE,
                    options=_opciones(opciones),
                )
                return respuesta.message.content
            except Exception as error:
                ultimo_error = _traducir_error(error)
                logger.warning(
                    "Intento %s/%s falló: %s", intento + 1, reintentos + 1, ultimo_error
                )
        await asyncio.sleep(0.5)

    raise ultimo_error  # type: ignore[misc]


async def modelos_disponibles() -> list[str]:
    """Lista los modelos instalados en Ollama (para el endpoint de salud)."""
    try:
        respuesta = await obtener_cliente().list()
        return [m.model for m in respuesta.models]
    except Exception as error:
        raise _traducir_error(error) from error