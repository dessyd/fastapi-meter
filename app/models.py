# Modèles SQLModel pour User, Location et Meter
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


# Énumérations
class MeterType(str, Enum):
    GAS = "gas"
    WATER = "water"
    ELECTRICITY = "electricity"


class MeterStatus(str, Enum):
    OPEN = "open"
    CLOSE = "close"


class UserRole(str, Enum):
    CONSUMER = "consumer"
    EMPLOYEE = "employee"
    ADMIN = "admin"


# Tables de liaison
class LocationUser(SQLModel, table=True):
    """Table de liaison entre Location et User."""

    __tablename__ = "location_user"

    location_id: Optional[int] = Field(
        default=None, foreign_key="location.id", primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )


# Modèles principaux
class User(SQLModel, table=True):
    """Modèle d'utilisateur."""

    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password: str  # Stockera le hash du mot de passe
    role: UserRole

    # Relations
    locations: List["Location"] = Relationship(
        back_populates="user",
        link_model=LocationUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Location(SQLModel, table=True):
    """Modèle d'emplacement."""

    __tablename__ = "location"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    lat: float
    lon: float

    # Relations
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(
        back_populates="locations",
        link_model=LocationUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    meters: List["Meter"] = Relationship(
        back_populates="location", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Meter(SQLModel, table=True):
    """Modèle de compteur."""

    __tablename__ = "meter"

    ean: str = Field(primary_key=True)
    status: MeterStatus = Field(default=MeterStatus.OPEN)
    type: MeterType
    reading: float = Field(default=0.0)
    unit: str  # Calculé automatiquement selon le type
    location_id: Optional[int] = Field(default=None, foreign_key="location.id")
    last_update: datetime = Field(default_factory=datetime.utcnow)

    # Relations
    location: Optional[Location] = Relationship(back_populates="meters")

    def get_unit(self):
        """Détermine l'unité en fonction du type de compteur."""
        if self.type == MeterType.GAS:
            return "m³"
        elif self.type == MeterType.WATER:
            return "m³"
        elif self.type == MeterType.ELECTRICITY:
            return "kWh"
        return ""


# Schémas pour les APIs (utilisant SQLModel comme schéma Pydantic)


# Schémas User
class UserBase(SQLModel):
    name: str
    email: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


# Schémas Location
class LocationBase(SQLModel):
    name: str
    lat: float
    lon: float


class LocationCreate(LocationBase):
    user_id: int


class LocationRead(LocationBase):
    id: int
    user_id: Optional[int] = None


class LocationUpdate(SQLModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    user_id: Optional[int] = None


# Schémas Meter
class MeterBase(SQLModel):
    ean: str
    type: MeterType
    reading: float
    status: MeterStatus = MeterStatus.OPEN


class MeterCreate(MeterBase):
    location_id: int


class MeterRead(MeterBase):
    unit: str
    location_id: int
    last_update: datetime


class MeterUpdate(SQLModel):
    reading: Optional[float] = None
    status: Optional[MeterStatus] = None
