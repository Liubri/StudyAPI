from pydantic import BaseModel, Field, conint, ConfigDict
from typing import Optional, List, Tuple
from datetime import datetime
from enum import IntEnum, Enum

class AccessLevel(IntEnum):
    NONE = 0
    POOR = 1
    FAIR = 2
    EXCELLENT = 3

class AtmosphereType(str, Enum):
    COZY = "Cozy"
    RUSTIC = "Rustic"
    TRADITIONAL = "Traditional"
    WARM = "Warm"
    CLEAN = "Clean"

class EnergyLevel(str, Enum):
    QUIET = "quiet"
    LOW_KEY = "low-key"
    TRANQUIL = "tranquil"
    MODERATE = "moderate"
    AVERAGE = "average"

class StudyFriendlyLevel(str, Enum):
    STUDY_HEAVEN = "study heaven"
    GOOD = "good"
    DECENT = "decent"
    MIXED = "mixed"
    FAIR = "fair"

class Address(BaseModel):
    street: str = Field(..., example="123 Main St")
    city: str = Field(..., example="San Francisco")
    state: str = Field(..., example="CA")
    zip_code: str = Field(..., example="94102")
    country: str = Field("USA", example="USA")

class Location(BaseModel):
    type: str = Field("Point", example="Point")
    coordinates: Tuple[float, float] = Field(..., example=[-122.4194, 37.7749])  # [longitude, latitude]

class CafeBase(BaseModel):
    name: str = Field(..., example="The Coffee Corner")
    address: Address
    location: Location
    phone: Optional[str] = Field(None, example="415-123-4567")
    website: Optional[str] = Field(None, example="https://thecoffeecorner.com")
    opening_hours: Optional[dict] = Field(None, example={"Mon-Fri": "7am-7pm", "Sat-Sun": "8am-6pm"})
    amenities: Optional[List[str]] = Field(None, example=["Free WiFi", "Power outlets", "Outdoor seating"])
    thumbnail_url: Optional[str] = Field(None, example="https://example.com/thumbnail.jpg")
    wifi_access: AccessLevel = Field(default=AccessLevel.NONE, example=3)
    outlet_accessibility: AccessLevel = Field(default=AccessLevel.NONE, example=2)
    average_rating: conint(ge=1, le=5) = Field(default=1, example=4)
    atmosphere: List[AtmosphereType] = Field(default_factory=lambda: [AtmosphereType.COZY, AtmosphereType.WARM], example=["Cozy", "Warm", "Traditional", "Clean"])
    energy_level: List[EnergyLevel] = Field(default_factory=lambda: [EnergyLevel.MODERATE, EnergyLevel.TRANQUIL], example=["moderate", "tranquil", "quiet", "low-key"])
    study_friendly: List[StudyFriendlyLevel] = Field(default_factory=lambda: [StudyFriendlyLevel.GOOD, StudyFriendlyLevel.DECENT], example=["good", "decent", "study heaven", "mixed"])

class CafeCreate(CafeBase):
    pass

class CafeUpdate(BaseModel):
    name: Optional[str] = Field(None, example="The New Coffee Corner")
    address: Optional[Address] = None
    location: Optional[Location] = None
    phone: Optional[str] = Field(None, example="415-987-6543")
    website: Optional[str] = Field(None, example="https://newcoffeecorner.com")
    opening_hours: Optional[dict] = Field(None, example={"Mon-Sun": "7am-8pm"})
    amenities: Optional[List[str]] = Field(None, example=["Free WiFi", "Power outlets", "Outdoor seating", "Pet friendly"])
    thumbnail_url: Optional[str] = Field(None, example="https://example.com/new_thumbnail.jpg")
    wifi_access: Optional[AccessLevel] = Field(None, example=3)
    outlet_accessibility: Optional[AccessLevel] = Field(None, example=3)
    average_rating: Optional[conint(ge=1, le=5)] = Field(None, example=5)
    atmosphere: Optional[List[AtmosphereType]] = Field(None, example=["Warm", "Cozy", "Clean", "Traditional"])
    energy_level: Optional[List[EnergyLevel]] = Field(None, example=["tranquil", "quiet", "low-key", "moderate"])
    study_friendly: Optional[List[StudyFriendlyLevel]] = Field(None, example=["study heaven", "good", "decent", "mixed"])

class Cafe(CafeBase):
    id: str = Field(..., alias="_id", example="60d5ec49e9af8b2c24e8a1b2")
    created_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")
    updated_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")

    model_config = ConfigDict(
        populate_by_name=True,
        allow_population_by_field_name=True,
        ser_by_alias=False  # This ensures serialization uses field names, not aliases
    ) 