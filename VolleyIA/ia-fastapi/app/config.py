"""
Configuración central del microservicio.

Todo se puede sobrescribir desde el archivo .env sin tocar código.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _entero(nombre: str, defecto: int) -> int:
    try:
        return int(os.getenv(nombre, defecto))
    except ValueError:
        return defecto


def _decimal(nombre: str, defecto: float) -> float:
    try:
        return float(os.getenv(nombre, defecto))
    except ValueError:
        return defecto


class Settings:
    # --- Ollama ---------------------------------------------------------
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    OLLAMA_MODELO: str = os.getenv("OLLAMA_MODELO", "llama3.2:3b")

    # Modelo para tareas cortas (resumir conversación). Por defecto el mismo.
    OLLAMA_MODELO_RAPIDO: str = os.getenv("OLLAMA_MODELO_RAPIDO", OLLAMA_MODELO)

    # Cuánto tiempo se queda el modelo cargado en memoria tras la última petición.
    # Evita la carga de varios segundos en cada mensaje.
    OLLAMA_KEEP_ALIVE: str = os.getenv("OLLAMA_KEEP_ALIVE", "30m")

    # Segundos máximos de espera por una respuesta.
    OLLAMA_TIMEOUT: float = _decimal("OLLAMA_TIMEOUT", 120.0)

    # Generaciones simultáneas. En hardware local, más de 2 suele empeorar todo.
    OLLAMA_MAX_CONCURRENTES: int = _entero("OLLAMA_MAX_CONCURRENTES", 2)

    # --- Parámetros de generación --------------------------------------
    # Tamaño de contexto: más grande = más lento y más RAM. 4096 es buen punto medio.
    NUM_CTX: int = _entero("NUM_CTX", 4096)
    # Tope de tokens por respuesta.
    NUM_PREDICT: int = _entero("NUM_PREDICT", 700)
    TEMPERATURE: float = _decimal("TEMPERATURE", 0.4)
    TOP_P: float = _decimal("TOP_P", 0.9)
    REPEAT_PENALTY: float = _decimal("REPEAT_PENALTY", 1.1)

    # --- Memoria de conversación ---------------------------------------
    # Cuando hay más de UMBRAL_RESUMEN mensajes, los antiguos se resumen
    # y solo se conservan los últimos MENSAJES_RECIENTES.
    UMBRAL_RESUMEN: int = _entero("UMBRAL_RESUMEN", 16)
    MENSAJES_RECIENTES: int = _entero("MENSAJES_RECIENTES", 6)


settings = Settings()