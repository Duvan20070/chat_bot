from app.profiles.coach_profile import obtener_perfil


perfil_usuario = obtener_perfil("coach_demo")


def obtener_perfil_actual():

    return perfil_usuario


def actualizar_perfil(entidades):

    global perfil_usuario

    for clave, valor in entidades.items():

        if valor is not None:

            perfil_usuario[clave] = valor