def detectar_intencion(mensaje: str):

    mensaje = mensaje.lower()

    if "rutina" in mensaje:
        return "rutina"

    if "entrenamiento" in mensaje:
        return "entrenamiento"

    if "plan" in mensaje:
        return "planificacion"

    if "dieta" in mensaje:
        return "nutricion"

    if "analiza" in mensaje:
        return "analisis"

    return "general"


def obtener_instrucciones(intencion):

    instrucciones = {

        "rutina":

            """
            Construye una rutina completa.

            Incluye:
            Objetivo
            Series
            Repeticiones
            Descansos
            Progresión
            """,

        "entrenamiento":

            """
            Construye una sesión completa de voleibol.
            """,

        "planificacion":

            """
            Construye una planificación deportiva.
            """,

        "nutricion":

            """
            Construye una guía nutricional.
            """,

        "analisis":

            """
            Analiza técnica, táctica y aspectos físicos.
            """,

        "general":

            """
            Responde normalmente.
            """

    }

    return instrucciones[intencion]