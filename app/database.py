# Configuration de la base de données avec SQLModel
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

settings = get_settings()

# Création du moteur de base de données
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def create_db_and_tables():
    """Crée les tables dans la base de données si elles n'existent pas déjà."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Génère une session de base de données pour une utilisation comme dépendance FastAPI."""
    with Session(engine) as session:
        yield session
