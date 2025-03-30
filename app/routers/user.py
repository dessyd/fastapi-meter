# Router pour les utilisateurs
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.jwt import (
    get_admin_user,
    get_current_active_user,
)
from app.auth.password import get_password_hash
from app.database import get_session
from app.models import User, UserCreate, UserRead, UserRole, UserUpdate

router = APIRouter(
    prefix="/user",
    tags=["users"],
)


@router.get("/", response_model=List[UserRead])
async def get_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Liste tous les utilisateurs (accessible par tous les utilisateurs authentifiés)."""
    # Les admin peuvent voir tous les utilisateurs
    if current_user.role == UserRole.ADMIN:
        statement = select(User)
    # Les employés peuvent voir les consommateurs
    elif current_user.role == UserRole.EMPLOYEE:
        statement = select(User).where(User.role == UserRole.CONSUMER)
    # Les consommateurs ne peuvent voir qu'eux-mêmes
    else:
        statement = select(User).where(User.id == current_user.id)

    users = session.exec(statement).all()
    return users


@router.put("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        get_admin_user
    ),  # Seul l'admin peut créer des utilisateurs
):
    """Crée un nouvel utilisateur (accessible uniquement par les administrateurs)."""
    # Vérifier si l'email existe déjà
    statement = select(User).where(User.email == user.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà",
        )

    # Création du nouvel utilisateur avec mot de passe hashé
    new_user = User(
        name=user.name,
        email=user.email,
        password=get_password_hash(user.password),
        role=user.role,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Récupère les détails d'un utilisateur par son ID."""
    # Vérifier les permissions
    if current_user.role == UserRole.CONSUMER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé",
        )

    # Récupérer l'utilisateur
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'ID {user_id} non trouvé",
        )

    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Met à jour les détails d'un utilisateur."""
    # Vérifier les permissions (seul l'admin peut modifier les rôles)
    if user_update.role is not None and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un administrateur peut modifier les rôles",
        )

    # Un utilisateur normal ne peut modifier que son propre profil
    if current_user.role == UserRole.CONSUMER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que votre propre profil",
        )

    # Récupérer l'utilisateur
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'ID {user_id} non trouvé",
        )

    # Mettre à jour les champs fournis
    user_data = user_update.dict(exclude_unset=True)
    if "password" in user_data:
        user_data["password"] = get_password_hash(user_data["password"])

    for key, value in user_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        get_admin_user
    ),  # Seul l'admin peut supprimer des utilisateurs
):
    """Supprime un utilisateur (accessible uniquement par les administrateurs)."""
    # Récupérer l'utilisateur
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'ID {user_id} non trouvé",
        )

    # Empêcher l'administrateur de se supprimer lui-même
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas vous supprimer vous-même",
        )

    session.delete(user)
    session.commit()
    return None
