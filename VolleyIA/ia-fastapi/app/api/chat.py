"""
Rutas del chat.

POST   /chat              -> respuesta completa (JSON)      [mismo contrato de antes]
POST   /chat/stream       -> respuesta en streaming (SSE)   [nuevo]
DELETE /chat/{usuario_id} -> borra la memoria de esa conversación

Compatibilidad: el body sigue siendo {"mensaje": "..."} y la respuesta
{"respuesta": "..."}. El campo "usuario_id" es OPCIONAL y vale "coach_demo"
si no se envía, igual que antes. Cuando NestJS esté listo, solo tiene que
mandar el id real del entrenador y cada uno tendrá su propia memoria.

Formato de los eventos SSE (cada línea "data: {...}\\n\\n"):
    {"token": "hola"}     -> un fragmento de texto
    {"done": true}        -> terminó bien
    {"error": "mensaje"}  -> falló
"""

import json
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from app.context.contexto import construir_mensajes
from app.memory.memory import guardar_mensaje, limpiar_conversacion
from app.services.ollama_service import OllamaError, generar, generar_stream
from app.services.resumen_service import comprimir_si_hace_falta

logger = logging.getLogger("volleyscan.chat")

router = APIRouter(prefix="/chat", tags=["chat"])

USUARIO_POR_DEFECTO = "coach_demo"


class Mensaje(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=4000)
    usuario_id: str = Field(default=USUARIO_POR_DEFECTO, min_length=1)


def _sse(datos: dict) -> str:
    return f"data: {json.dumps(datos, ensure_ascii=False)}\n\n"


@router.post("")
async def chat(datos: Mensaje, segundo_plano: BackgroundTasks):
    mensajes = construir_mensajes(datos.usuario_id, datos.mensaje)

    try:
        respuesta = await generar(mensajes)
    except OllamaError as error:
        raise HTTPException(status_code=503, detail=str(error))

    # Se guarda solo si la respuesta salió bien: el historial nunca queda a medias.
    guardar_mensaje(datos.usuario_id, "user", datos.mensaje)
    guardar_mensaje(datos.usuario_id, "assistant", respuesta)

    segundo_plano.add_task(comprimir_si_hace_falta, datos.usuario_id)

    return {"respuesta": respuesta}


@router.post("/stream")
async def chat_stream(datos: Mensaje):
    mensajes = construir_mensajes(datos.usuario_id, datos.mensaje)

    async def eventos():
        partes: list[str] = []

        try:
            async for token in generar_stream(mensajes):
                partes.append(token)
                yield _sse({"token": token})
        except OllamaError as error:
            yield _sse({"error": str(error)})
            return

        respuesta = "".join(partes).strip()
        if respuesta:
            guardar_mensaje(datos.usuario_id, "user", datos.mensaje)
            guardar_mensaje(datos.usuario_id, "assistant", respuesta)

        yield _sse({"done": True})

    return StreamingResponse(
        eventos(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # evita que proxies (nginx) acumulen el stream
        },
        # Se ejecuta después de enviar toda la respuesta
        background=BackgroundTask(comprimir_si_hace_falta, datos.usuario_id),
    )


@router.delete("/{usuario_id}")
async def borrar_conversacion(usuario_id: str):
    limpiar_conversacion(usuario_id)
    return {"mensaje": "Conversación eliminada"}