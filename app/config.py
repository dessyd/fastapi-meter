import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()


class Settings(BaseSettings):
    """Configuration de l'application."""

    APP_NAME: str = os.getenv("APP_NAME", "fastapi-meter")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

    # Configuration de la base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./meter.db")

    # Configuration JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your_super_secret_key_here")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    # Utilisateur admin initial
    INITIAL_ADMIN_EMAIL: str = os.getenv(
        "INITIAL_ADMIN_EMAIL", "admin@example.com"
    )
    INITIAL_ADMIN_PASSWORD: str = os.getenv(
        "INITIAL_ADMIN_PASSWORD", "admin_secure_password"
    )
    INITIAL_ADMIN_NAME: str = os.getenv("INITIAL_ADMIN_NAME", "Administrator")


@lru_cache()
def get_settings():
    """Retourne les paramètres de l'application (singleton)."""
    return Settings()
