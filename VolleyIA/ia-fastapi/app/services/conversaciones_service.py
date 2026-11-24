from app.memory.memory import guardar_mensaje
from app.services.ollama_services import preguntar_a_llama
from app.context.contexto import construir_contexto
from app.brain.decision_engine import detectar_intencion


def procesar_conversacion(usuario_id, mensaje):

    guardar_mensaje(
        usuario_id,
        "usuario",
        mensaje
    )

    contexto = construir_contexto(
        usuario_id,
        mensaje
    )

    respuesta = preguntar_a_llama(contexto)

    guardar_mensaje(
        usuario_id,
        "asistente",
        respuesta
    )

    return respuesta