from app.prompts.system_prompt import SYSTEM_PROMPT
from app.memory.memory import obtener_historial
from app.profiles.coach_profile import obtener_perfil


def construir_contexto(usuario_id: str, mensaje: str):

    historial = obtener_historial(usuario_id)
    perfil = obtener_perfil(usuario_id)

    contexto = SYSTEM_PROMPT

    contexto += "\n\n==============================\n"
    contexto += "PERFIL DEL ENTRENADOR\n"
    contexto += "==============================\n\n"

    for clave, valor in perfil.items():
        contexto += f"{clave}: {valor}\n"

    contexto += "\n\n==============================\n"
    contexto += "HISTORIAL DE LA CONVERSACIÓN\n"
    contexto += "==============================\n\n"

    for item in historial:
        contexto += f"{item['rol']}: {item['contenido']}\n"

    contexto += "\n\n==============================\n"
    contexto += "MENSAJE ACTUAL\n"
    contexto += "==============================\n\n"

    contexto += mensaje

    return contexto