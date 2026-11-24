import re


def extraer_entidades(mensaje: str):

    texto = mensaje.lower()

    datos = {

        "posicion": None,
        "fundamento": None,
        "objetivo": None,

        # Nuevos campos
        "nivel": None,
        "categoria": None,
        "sexo": None,
        "rol": None

    }

    posiciones = {
        "armador",
        "central",
        "líbero",
        "libero",
        "opuesto",
        "punta"
    }

    fundamentos = {
        "saque",
        "recepción",
        "recepcion",
        "bloqueo",
        "ataque",
        "defensa",
        "armado",
        "salto"
    }

    objetivos = {
        "mejorar",
        "aprender",
        "corregir",
        "perfeccionar",
        "aumentar"
    }

    niveles = {
        "principiante",
        "intermedio",
        "avanzado"
    }

    for palabra in posiciones:
        if palabra in texto:
            datos["posicion"] = palabra

    for palabra in fundamentos:
        if palabra in texto:
            datos["fundamento"] = palabra

    for palabra in objetivos:
        if palabra in texto:
            datos["objetivo"] = palabra

    for palabra in niveles:
        if palabra in texto:
            datos["nivel"] = palabra

    if "entrenador" in texto:
        datos["rol"] = "entrenador"

    elif "jugador" in texto:
        datos["rol"] = "jugador"

    if "femenino" in texto:
        datos["sexo"] = "femenino"

    elif "masculino" in texto:
        datos["sexo"] = "masculino"

    categoria = re.search(r"sub[- ]?(\d+)", texto)

    if categoria:
        datos["categoria"] = f"Sub-{categoria.group(1)}"

    return datos