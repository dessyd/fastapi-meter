# Router pour les emplacements
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.jwt import get_current_active_user, get_employee_or_admin_user
from app.database import get_session
from app.models import (
    Location,
    LocationCreate,
    LocationRead,
    LocationUpdate,
    Meter,
    User,
    UserRole,
)

router = APIRouter(
    prefix="/location",
    tags=["locations"],
)


@router.get("/", response_model=List[LocationRead])
async def get_locations(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Liste tous les emplacements (filtré selon le rôle de l'utilisateur)."""
    # Admin et employés voient tous les emplacements
    if current_user.role in [UserRole.ADMIN, UserRole.EMPLOYEE]:
        statement = select(Location)
    # Les consommateurs ne voient que leurs emplacements
    else:
        statement = select(Location).where(Location.user_id == current_user.id)

    locations = session.exec(statement).all()
    return locations


@router.put(
    "/", response_model=LocationRead, status_code=status.HTTP_201_CREATED
)
async def create_location(
    location: LocationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        get_employee_or_admin_user
    ),  # Employés et admin peuvent créer
):
    """Crée un nouvel emplacement."""
    # Vérifier si l'utilisateur associé existe
    statement = select(User).where(User.id == location.user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'ID {location.user_id} non trouvé",
        )

    # Vérifier que l'utilisateur est un consommateur
    if user.role != UserRole.CONSUMER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les consommateurs peuvent avoir des emplacements",
        )

    # Créer le nouvel emplacement
    new_location = Location(
        name=location.name,
        lat=location.lat,
        lon=location.lon,
        user_id=location.user_id,
    )

    session.add(new_location)
    session.commit()
    session.refresh(new_location)
    return new_location


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Récupère les détails d'un emplacement et ses compteurs associés."""
    # Récupérer l'emplacement
    statement = select(Location).where(Location.id == location_id)
    location = session.exec(statement).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emplacement avec l'ID {location_id} non trouvé",
        )

    # Vérifier les permissions
    if (
        current_user.role == UserRole.CONSUMER
        and location.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé à cet emplacement",
        )

    return location


@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: int,
    location_update: LocationUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        get_employee_or_admin_user
    ),  # Employés et admin peuvent modifier
):
    """Met à jour les détails d'un emplacement."""
    # Récupérer l'emplacement
    statement = select(Location).where(Location.id == location_id)
    location = session.exec(statement).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emplacement avec l'ID {location_id} non trouvé",
        )

    # Mise à jour de l'utilisateur associé
    if location_update.user_id is not None:
        user_statement = select(User).where(User.id == location_update.user_id)
        user = session.exec(user_statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Utilisateur avec l'ID {location_update.user_id} non"
                    " trouvé"
                ),
            )
        if user.role != UserRole.CONSUMER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Seuls les consommateurs peuvent avoir des emplacements"
                ),
            )

    # Mettre à jour les champs fournis
    location_data = location_update.dict(exclude_unset=True)
    for key, value in location_data.items():
        setattr(location, key, value)

    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        get_employee_or_admin_user
    ),  # Employés et admin peuvent supprimer
):
    """Supprime un emplacement s'il n'y a plus de compteurs associés."""
    # Récupérer l'emplacement
    statement = select(Location).where(Location.id == location_id)
    location = session.exec(statement).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emplacement avec l'ID {location_id} non trouvé",
        )

    # Vérifier s'il y a des compteurs associés
    meter_statement = select(Meter).where(Meter.location_id == location_id)
    meters = session.exec(meter_statement).all()
    if meters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Impossible de supprimer l'emplacement car il contient des"
                " compteurs"
            ),
        )

    session.delete(location)
    session.commit()
    return None
