from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth.password import (  # Importation depuis password.py
    verify_password,
)
from app.config import get_settings
from app.database import get_session
from app.models import User, UserRole

# Configuration des outils de sécurité
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Modèles pour l'authentification
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# Fonctions d'authentification
def authenticate_user(session: Session, email: str, password: str):
    """Authentifie un utilisateur par son email et mot de passe."""
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user:
        print(f"Utilisateur non trouvé: {email}")
        return False
    if not verify_password(password, user.password):
        print(f"Mot de passe incorrect pour l'utilisateur: {email}")
        return False
    return user


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
):
    """Crée un token JWT."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """Récupère l'utilisateur actuel à partir du token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    statement = select(User).where(User.email == token_data.email)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
    """Vérifie que l'utilisateur courant est actif."""
    return current_user


# Dépendances pour les vérifications de rôle
def get_admin_user(current_user: User = Depends(get_current_active_user)):
    """Vérifie que l'utilisateur est un administrateur."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilèges insuffisants",
        )
    return current_user


def get_employee_or_admin_user(
    current_user: User = Depends(get_current_active_user),
):
    """Vérifie que l'utilisateur est un employé ou un administrateur."""
    if current_user.role not in [UserRole.EMPLOYEE, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilèges insuffisants",
        )
    return current_user
