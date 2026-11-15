from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Role = Literal["donor", "recipient"]
ResourceKind = Literal["food_bank", "shelter", "volunteer", "donation"]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Site(BaseModel):
    id: int
    name: str
    kind: Literal["dining", "restaurant", "event"]
    lat: float
    lon: float
    avg_lbs: float
    address: str = ""


class Pantry(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    capacity_lbs: float
    needs: list[str] = []
    address: str = ""


class ListingIn(BaseModel):
    site_id: int
    food: str = Field(min_length=1)
    quantity_lbs: float = Field(gt=0)
    pickup_deadline: datetime
    dietary_tags: list[str] = []

    @field_validator("pickup_deadline")
    @classmethod
    def _aware(cls, v: datetime) -> datetime:
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)


class Listing(ListingIn):
    id: int
    donor_id: int | None = None
    status: Literal["open", "matched", "expired"] = "open"
    pantry_id: int | None = None
    score: float | None = None
    created_at: datetime = Field(default_factory=utcnow)


class Notification(BaseModel):
    id: int
    listing_id: int
    pantry_id: int
    message: str
    sent_at: datetime = Field(default_factory=utcnow)


class UserIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)
    role: Role
    site_id: int | None = None


class LoginIn(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    site_id: int | None = None
    password_hash: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    site_id: int | None = None


class Resource(BaseModel):
    id: int
    name: str
    kind: ResourceKind
    address: str
    lat: float
    lon: float
    description: str
    how_to_help: str = ""
    contact: str = ""
    url: str = ""
    nav_address: str = ""
