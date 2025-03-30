# Point d'entrée principal de l'application FastAPI
from fastapi import FastAPI
from sqlmodel import Session

from app.config import get_settings
from app.core.init_db import init_db
from app.database import create_db_and_tables, get_session
from app.routers import auth, location, meter, user

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestion des compteurs pour un service public",
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


@app.on_event("startup")
def on_startup():
    """Actions à effectuer au démarrage de l'application."""
    create_db_and_tables()
    # Initialiser la base de données avec un utilisateur admin
    with Session(get_session().__next__().session.bind) as session:
        init_db(session)
