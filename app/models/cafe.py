from pydantic import BaseModel, Field, conint, ConfigDict, field_validator
from typing import Optional, List, Tuple, Union
from datetime import datetime
from enum import IntEnum

class AccessLevel(IntEnum):
    NONE = 0
    POOR = 1
    FAIR = 2
    EXCELLENT = 3

# Removed enum definitions - now using flexible List[str] for tag fields

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
    atmosphere: List[str] = Field(default_factory=lambda: ["Cozy", "Warm"], example=["Cozy", "Warm", "Traditional", "Clean", "Industrial", "Modern"])
    energy_level: List[str] = Field(default_factory=lambda: ["moderate", "tranquil"], example=["moderate", "tranquil", "quiet", "low-key", "energetic", "vibrant"])
    study_friendly: List[str] = Field(default_factory=lambda: ["good", "decent"], example=["good", "decent", "study heaven", "mixed", "excellent", "perfect"])

    @field_validator('atmosphere', mode='before')
    @classmethod
    def validate_atmosphere(cls, v):
        if isinstance(v, list):
            # Handle comma-separated strings within array elements
            result = []
            for item in v:
                if isinstance(item, str) and ',' in item:
                    # Split comma-separated values
                    result.extend([x.strip() for x in item.split(',')])
                else:
                    result.append(item)
            return result
        return v

    @field_validator('energy_level', mode='before')
    @classmethod
    def validate_energy_level(cls, v):
        if isinstance(v, list):
            # Handle comma-separated strings within array elements
            result = []
            for item in v:
                if isinstance(item, str) and ',' in item:
                    # Split comma-separated values
                    result.extend([x.strip() for x in item.split(',')])
                else:
                    result.append(item)
            return result
        return v

    @field_validator('study_friendly', mode='before')
    @classmethod
    def validate_study_friendly(cls, v):
        if isinstance(v, list):
            # Handle comma-separated strings within array elements
            result = []
            for item in v:
                if isinstance(item, str) and ',' in item:
                    # Split comma-separated values
                    result.extend([x.strip() for x in item.split(',')])
                else:
                    result.append(item)
            return result
        return v

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
    atmosphere: Optional[List[str]] = Field(None, example=["Warm", "Cozy", "Clean", "Traditional", "Industrial", "Modern"])
    energy_level: Optional[List[str]] = Field(None, example=["tranquil", "quiet", "low-key", "moderate", "energetic", "vibrant"])
    study_friendly: Optional[List[str]] = Field(None, example=["study heaven", "good", "decent", "mixed", "excellent", "perfect"])

class Cafe(CafeBase):
    id: str = Field(..., alias="_id", example="60d5ec49e9af8b2c24e8a1b2")
    created_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")
    updated_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")

    model_config = ConfigDict(
        populate_by_name=True,
        allow_population_by_field_name=True,
        ser_by_alias=False  # This ensures serialization uses field names, not aliases
    ) 