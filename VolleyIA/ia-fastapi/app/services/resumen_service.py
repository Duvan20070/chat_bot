"""
Resumen automático de conversaciones largas.

Cuando el historial supera el umbral, los mensajes antiguos se condensan
en un resumen corto. Así el modelo "recuerda" toda la conversación sin
llenar la ventana de contexto (que es lo que vuelve lento a un modelo local).

Se ejecuta en segundo plano DESPUÉS de responder, por lo que no añade
latencia al entrenador.
"""

import logging

from app.config import settings
from app.memory.memory import (
    aplicar_resumen,
    tomar_snapshot_para_resumir,
)
from app.services.ollama_service import OllamaError, generar

logger = logging.getLogger("volleyscan.resumen")

_INSTRUCCION = """Eres un asistente que resume conversaciones entre un entrenador de voleibol y su asistente de IA.

Escribe un resumen breve (máximo 150 palabras) en español, en viñetas cortas.
Conserva SOLO datos útiles para conversaciones futuras:
- Nombres de jugadores, equipos y categorías mencionados.
- Objetivos, lesiones, limitaciones y decisiones del entrenador.
- Planes, rutinas o recomendaciones ya entregadas.
No inventes nada. No incluyas saludos ni frases de cortesía."""


async def comprimir_si_hace_falta(usuario_id: str) -> None:
    snapshot = tomar_snapshot_para_resumir(usuario_id)
    if snapshot is None:
        return

    antiguos, cantidad, resumen_previo = snapshot

    transcripcion = "\n".join(
        f"{'Entrenador' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
        for m in antiguos
    )

    contenido = ""
    if resumen_previo:
        contenido += f"RESUMEN PREVIO:\n{resumen_previo}\n\n"
    contenido += f"CONVERSACIÓN NUEVA A INTEGRAR:\n{transcripcion}"

    try:
        resumen = await generar(
            [
                {"role": "system", "content": _INSTRUCCION},
                {"role": "user", "content": contenido},
            ],
            opciones={"temperature": 0.2, "num_predict": 300},
            modelo=settings.OLLAMA_MODELO_RAPIDO,
            reintentos=0,
        )
    except OllamaError as error:
        # Si falla, no se borra nada: se reintentará en el próximo mensaje.
        logger.warning("No se pudo resumir la conversación de %s: %s", usuario_id, error)
        return

    resumen = resumen.strip()
    if resumen:
        aplicar_resumen(usuario_id, cantidad, resumen)
        logger.info("Conversación de %s comprimida (%s mensajes)", usuario_id, cantidad)