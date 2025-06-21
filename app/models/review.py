from pydantic import BaseModel, Field, confloat, ConfigDict
from typing import List, Optional
from datetime import datetime

class PhotoBase(BaseModel):
    url: str = Field(..., example="https://example.com/photo.jpg")
    caption: Optional[str] = Field(None, example="A photo of the study spot")

class PhotoCreate(PhotoBase):
    pass

class Photo(PhotoBase):
    id: str = Field(..., alias="_id", example="60d5ec49e9af8b2c24e8a1b2")

    model_config = ConfigDict(
        populate_by_name=True,
        allow_population_by_field_name=True,
        ser_by_alias=False
    )

class ReviewBase(BaseModel):
    study_spot_id: str = Field(..., example="cafe123")
    user_id: str = Field(..., example="user456")
    overall_rating: confloat(ge=0, le=5) = Field(..., example=4.5)
    outlet_accessibility: confloat(ge=0, le=5) = Field(..., example=4.0)
    wifi_quality: confloat(ge=0, le=5) = Field(..., example=5.0)
    atmosphere: Optional[str] = Field(None, example="Quiet and peaceful")
    energy_level: Optional[str] = Field(None, example="Calm")
    study_friendly: Optional[str] = Field(None, example="Very study-friendly")

    @classmethod
    def validate_rating_fields(cls, v):
        valid_ratings = ['Poor', 'Fair', 'Good', 'Excellent']
        if v not in valid_ratings:
            raise ValueError(f"Rating must be one of: {', '.join(valid_ratings)}")
        return v

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    overall_rating: Optional[confloat(ge=0, le=5)] = Field(None, example=4.8)
    outlet_accessibility: Optional[confloat(ge=0, le=5)] = Field(None, example=4.2)
    wifi_quality: Optional[confloat(ge=0, le=5)] = Field(None, example=4.9)
    atmosphere: Optional[str] = Field(None, example="A bit noisy in the afternoon")
    energy_level: Optional[str] = Field(None, example="Energetic")
    study_friendly: Optional[str] = Field(None, example="Good for group study")

    @classmethod
    def validate_rating_fields(cls, v):
        if v is not None:
            valid_ratings = ['Poor', 'Fair', 'Good', 'Excellent']
            if v not in valid_ratings:
                raise ValueError(f"Rating must be one of: {', '.join(valid_ratings)}")
        return v

class Review(ReviewBase):
    id: str = Field(..., alias="_id", example="60d5ec49e9af8b2c24e8a1b2")
    photos: List[Photo] = []
    created_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")
    updated_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")

    model_config = ConfigDict(
        populate_by_name=True,
        allow_population_by_field_name=True,
        ser_by_alias=False,
        json_schema_extra={
            "example": {
                "id": "60d5ec49e9af8b2c24e8a1b2",
                "study_spot_id": "cafe123",
                "user_id": "user456",
                "overall_rating": 4.5,
                "outlet_accessibility": 4.0,
                "wifi_quality": 5.0,
                "atmosphere": "Quiet and peaceful",
                "energy_level": "Calm",
                "study_friendly": "Very study-friendly",
                "photos": [
                    {
                        "id": "photo1",
                        "url": "https://example.com/photo1.jpg",
                        "caption": "View from the window"
                    }
                ],
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        },
    ) 