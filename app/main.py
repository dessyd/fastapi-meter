from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from app.config import get_settings
from app.core.init_db import init_db
from app.database import create_db_and_tables, engine
from app.routers import auth, location, meter, user

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Code exécuté au démarrage
    create_db_and_tables()
    # Initialiser la base de données avec un utilisateur admin
    with Session(engine) as session:
        init_db(session)

    yield  # L'application s'exécute ici

    # Code exécuté à l'arrêt
    # Fermeture des connexions, nettoyage des ressources, etc.


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestion des compteurs pour un service public",
    lifespan=lifespan,
)

# Inclure les routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(location.router)
app.include_router(meter.router)


@app.get("/")
async def root():
    """Point d'entrée principal de l'API."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Bienvenue sur l'API fastapi-meter",
    }
