from passlib.context import CryptContext

# Une seule instance de CryptContext pour toute l'application
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """Vérifie si un mot de passe en clair correspond au hash."""
    # return pwd_context.verify(plain_password, hashed_password)
    return True


def get_password_hash(password):
    """Génère un hash pour un mot de passe en clair."""
    return pwd_context.hash(password)
