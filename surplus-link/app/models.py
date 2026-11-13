from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Site(BaseModel):
    id: int
    name: str
    kind: Literal["dining", "restaurant", "event"]
    lat: float
    lon: float
    avg_lbs: float


class Pantry(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    capacity_lbs: float
    needs: list[str] = []


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
