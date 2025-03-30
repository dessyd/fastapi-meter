# Initialisation de la base de données et création d'un admin par défaut
from sqlmodel import Session, select

from app.auth.jwt import get_password_hash
from app.config import get_settings
from app.models import User, UserRole

settings = get_settings()


def init_db(session: Session) -> None:
    """Initialise la base de données avec un utilisateur admin."""
    # Vérifier si un utilisateur admin existe déjà
    statement = select(User).where(User.role == UserRole.ADMIN)
    admin = session.exec(statement).first()

    # Si aucun administrateur n'existe, on en crée un
    if not admin:
        admin_user = User(
            name=settings.INITIAL_ADMIN_NAME,
            email=settings.INITIAL_ADMIN_EMAIL,
            password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
            role=UserRole.ADMIN,
        )
        session.add(admin_user)
        session.commit()
        print(f"Utilisateur admin créé: {settings.INITIAL_ADMIN_EMAIL}")
    else:
        print("Un utilisateur admin existe déjà")
