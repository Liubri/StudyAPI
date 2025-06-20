from pydantic import BaseModel, Field, conint, ConfigDict
from typing import Optional, List, Tuple
from datetime import datetime
from enum import IntEnum

class AccessLevel(IntEnum):
    NONE = 0
    POOR = 1
    FAIR = 2
    EXCELLENT = 3

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"  # Default to USA

class Location(BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float]  # [longitude, latitude]

class CafeBase(BaseModel):
    name: str
    address: Address
    location: Location
    phone: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[dict] = None
    amenities: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    wifi_access: AccessLevel = Field(default=AccessLevel.NONE)
    outlet_accessibility: AccessLevel = Field(default=AccessLevel.NONE)
    average_rating: conint(ge=1, le=5) = Field(default=1)

class CafeCreate(CafeBase):
    pass

class CafeUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[Address] = None
    location: Optional[Location] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[dict] = None
    amenities: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    wifi_access: Optional[AccessLevel] = None
    outlet_accessibility: Optional[AccessLevel] = None
    average_rating: Optional[conint(ge=1, le=5)] = None

class Cafe(CafeBase):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True) 