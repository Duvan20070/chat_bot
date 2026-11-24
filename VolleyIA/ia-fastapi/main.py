import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.config import settings
from app.services.ollama_service import (
    
    OllamaError,
    calentar_modelo,
    cerrar_cliente,
    modelos_disponibles,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # Al arrancar: cargar el modelo en memoria para que el primer mensaje sea rápido
    await calentar_modelo()
    yield
    # Al apagar: cerrar conexiones
    await cerrar_cliente()


app = FastAPI(
    title="VolleyScan IA",
    description="Asistente inteligente para entrenadores de voleibol",
    version="1.1.0",
    lifespan=ciclo_de_vida,
)

# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Rutas
# ==========================================

app.include_router(chat_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a VolleyScan IA",
        "estado": "Servidor funcionando correctamente",
    }


@app.get("/salud")
async def salud():
    """Verifica que Ollama responde y que el modelo está instalado."""
    try:
        modelos = await modelos_disponibles()
    except OllamaError as error:
        raise HTTPException(status_code=503, detail=str(error))

    instalado = any(
        m == settings.OLLAMA_MODELO or m.startswith(settings.OLLAMA_MODELO + ":")
        for m in modelos
    )
    return {
        "ollama": "ok",
        "modelo": settings.OLLAMA_MODELO,
        "modelo_instalado": instalado,
        "modelos": modelos,
    }