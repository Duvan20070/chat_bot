def detectar_intencion(mensaje: str):

    mensaje = mensaje.lower()

    entrenamiento = [
        "entrenamiento",
        "rutina",
        "ejercicio",
        "salto",
        "remate",
        "bloqueo",
        "saque",
        "recepción",
        "defensa",
        "voleibol",
        "voleibol",
        "armador",
        "opuesto",
        "líbero",
        "central"
    ]

    nutricion = [
        "comida",
        "proteína",
        "alimentación",
        "nutrición",
        "calorías",
        "dieta"
    ]

    lesiones = [
        "dolor",
        "lesión",
        "rodilla",
        "hombro",
        "tobillo",
        "esguince"
    ]

    for palabra in entrenamiento:

        if palabra in mensaje:
            return "ENTRENAMIENTO"

    for palabra in nutricion:

        if palabra in mensaje:
            return "NUTRICION"

    for palabra in lesiones:

        if palabra in mensaje:
            return "LESIONES"

    return "GENERAL"