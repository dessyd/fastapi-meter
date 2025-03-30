from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.jwt import (
    get_admin_user,
    get_current_active_user,
    get_employee_or_admin_user,
)
from app.database import get_session
from app.models import (
    Location,
    Meter,
    MeterCreate,
    MeterRead,
    MeterType,
    MeterUpdate,
    User,
    UserRole,
)

router = APIRouter(
    prefix="/meter",
    tags=["meters"],
)


@router.get("/", response_model=List[MeterRead])
async def get_meters(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Liste tous les compteurs (filtré selon le rôle de l'utilisateur)."""
    # Admin et employés voient tous les compteurs
    if current_user.role in [UserRole.ADMIN, UserRole.EMPLOYEE]:
        statement = select(Meter)
    # Les consommateurs ne voient que les compteurs de leurs emplacements
    else:
        # Récupérer les emplacements de l'utilisateur
        location_statement = select(Location).where(
            Location.user_id == current_user.id
        )
        user_locations = session.exec(location_statement).all()
        location_ids = [loc.id for loc in user_locations]

        # Récupérer les compteurs pour ces emplacements
        if location_ids:
            statement = select(Meter).where(
                Meter.location_id.in_(location_ids)
            )
        else:
            return []  # Aucun emplacement, donc aucun compteur

    meters = session.exec(statement).all()
    return meters


@router.put("/", response_model=MeterRead, status_code=status.HTTP_201_CREATED)
async def create_meter(
    meter: MeterCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        get_employee_or_admin_user
    ),  # Employés et admin peuvent créer
):
    """Crée un nouveau compteur."""
    # Vérifier si l'emplacement associé existe
    statement = select(Location).where(Location.id == meter.location_id)
    location = session.exec(statement).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emplacement avec l'ID {meter.location_id} non trouvé",
        )

    # Vérifier si l'EAN existe déjà
    existing_statement = select(Meter).where(Meter.ean == meter.ean)
    existing_meter = session.exec(existing_statement).first()
    if existing_meter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un compteur avec l'EAN {meter.ean} existe déjà",
        )

    # Déterminer l'unité en fonction du type
    unit = ""
    if meter.type == MeterType.GAS:
        unit = "m³"
    elif meter.type == MeterType.WATER:
        unit = "m³"
    elif meter.type == MeterType.ELECTRICITY:
        unit = "kWh"

    # Créer le nouveau compteur
    new_meter = Meter(
        ean=meter.ean,
        status=meter.status,
        type=meter.type,
        reading=meter.reading,
        unit=unit,
        location_id=meter.location_id,
        last_update=datetime.utcnow(),
    )

    session.add(new_meter)
    session.commit()
    session.refresh(new_meter)
    return new_meter


@router.get("/{ean}", response_model=MeterRead)
async def get_meter(
    ean: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Récupère les détails d'un compteur par son EAN."""
    # Récupérer le compteur
    statement = select(Meter).where(Meter.ean == ean)
    meter = session.exec(statement).first()
    if not meter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compteur avec l'EAN {ean} non trouvé",
        )

    # Vérifier les permissions pour les consommateurs
    if current_user.role == UserRole.CONSUMER:
        # Vérifier si le compteur est associé à un emplacement de l'utilisateur
        location_statement = select(Location).where(
            (Location.id == meter.location_id)
            & (Location.user_id == current_user.id)
        )
        location = session.exec(location_statement).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce compteur",
            )

    return meter


@router.patch("/{ean}", response_model=MeterRead)
async def update_meter(
    ean: str,
    meter_update: MeterUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        get_employee_or_admin_user
    ),  # Employés et admin peuvent modifier
):
    """Met à jour la valeur ou le statut d'un compteur."""
    # Récupérer le compteur
    statement = select(Meter).where(Meter.ean == ean)
    meter = session.exec(statement).first()
    if not meter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compteur avec l'EAN {ean} non trouvé",
        )

    # Mettre à jour la valeur ou le statut
    if meter_update.reading is not None:
        # Vérifier que la nouvelle valeur est supérieure à l'ancienne
        if meter_update.reading <= meter.reading:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nouvelle valeur doit être supérieure à l'ancienne",
            )
        meter.reading = meter_update.reading

    if meter_update.status is not None:
        meter.status = meter_update.status

    # Mettre à jour la date de dernière mise à jour
    meter.last_update = datetime.utcnow()

    session.add(meter)
    session.commit()
    session.refresh(meter)
    return meter


@router.delete("/{ean}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meter(
    ean: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        get_admin_user
    ),  # Seul l'admin peut supprimer
):
    """Supprime un compteur."""
    # Récupérer le compteur
    statement = select(Meter).where(Meter.ean == ean)
    meter = session.exec(statement).first()
    if not meter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compteur avec l'EAN {ean} non trouvé",
        )

    session.delete(meter)
    session.commit()
    return None  # Router pour les compteurs
