def detectar_intencion(mensaje: str):

    mensaje = mensaje.lower()

    if any(palabra in mensaje for palabra in [
        "entrenamiento",
        "rutina",
        "ejercicios",
        "sesión",
        "plan de entrenamiento"
    ]):
        return "ENTRENAMIENTO"

    if any(palabra in mensaje for palabra in [
        "dieta",
        "alimentación",
        "nutrición",
        "comida",
        "calorías"
    ]):
        return "NUTRICION"

    if any(palabra in mensaje for palabra in [
        "pdf",
        "word",
        "excel",
        "archivo",
        "documento"
    ]):
        return "DOCUMENTO"

    if any(palabra in mensaje for palabra in [
        "estadísticas",
        "estadisticas",
        "análisis",
        "analisis",
        "rendimiento"
    ]):
        return "ESTADISTICAS"

    return "CONSULTA"