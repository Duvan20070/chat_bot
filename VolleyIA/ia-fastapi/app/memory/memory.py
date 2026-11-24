"""
Memoria de conversación por entrenador.

Guarda dos cosas por usuario:
- mensajes: los últimos mensajes en formato {"role", "content"}
  (el mismo formato que usa Ollama, sin conversiones).
- resumen: un resumen automático de lo que ya salió de la ventana.

NOTA: por ahora vive en RAM, así que se pierde al reiniciar el servidor.
El siguiente paso es persistirla en MySQL (misma interfaz, otro almacenamiento).
"""

from threading import Lock
from typing import Optional

from app.config import settings

_conversaciones: dict[str, dict] = {}
_lock = Lock()


def _obtener(usuario_id: str) -> dict:
    if usuario_id not in _conversaciones:
        _conversaciones[usuario_id] = {"mensajes": [], "resumen": ""}
    return _conversaciones[usuario_id]


def obtener_historial(usuario_id: str) -> list[dict]:
    """Copia de los mensajes recientes (role/content)."""
    with _lock:
        return list(_obtener(usuario_id)["mensajes"])


def obtener_resumen(usuario_id: str) -> str:
    with _lock:
        return _obtener(usuario_id)["resumen"]


def guardar_mensaje(usuario_id: str, role: str, content: str) -> None:
    """role debe ser 'user' o 'assistant'."""
    with _lock:
        _obtener(usuario_id)["mensajes"].append({"role": role, "content": content})


def limpiar_conversacion(usuario_id: str) -> None:
    with _lock:
        _conversaciones.pop(usuario_id, None)


# ----------------------------------------------------------------------
# Compresión de historial
# ----------------------------------------------------------------------


def tomar_snapshot_para_resumir(
    usuario_id: str,
) -> Optional[tuple[list[dict], int, str]]:
    """
    Si el historial superó el umbral, devuelve
    (mensajes_antiguos, cantidad, resumen_previo). Si no, None.

    No borra nada todavía: solo se borra cuando el resumen se generó bien
    (ver aplicar_resumen), así nunca se pierde contexto si el modelo falla.
    """
    with _lock:
        datos = _obtener(usuario_id)
        mensajes = datos["mensajes"]

        if len(mensajes) <= settings.UMBRAL_RESUMEN:
            return None

        cantidad = len(mensajes) - settings.MENSAJES_RECIENTES
        return list(mensajes[:cantidad]), cantidad, datos["resumen"]


def aplicar_resumen(usuario_id: str, cantidad: int, resumen: str) -> None:
    """Elimina los primeros `cantidad` mensajes y guarda el nuevo resumen."""
    with _lock:
        datos = _obtener(usuario_id)
        datos["mensajes"] = datos["mensajes"][cantidad:]
        datos["resumen"] = resumen