from pydantic import BaseModel, Field, confloat, ConfigDict
from typing import List, Optional
from datetime import datetime

class PhotoBase(BaseModel):
    url: str
    caption: Optional[str] = None

class PhotoCreate(PhotoBase):
    pass

class Photo(PhotoBase):
    id: str = Field(..., alias="_id")

    model_config = ConfigDict(populate_by_name=True)

class ReviewBase(BaseModel):
    study_spot_id: str
    user_id: str
    overall_rating: confloat(ge=0, le=5)
    outlet_accessibility: confloat(ge=0, le=5)
    wifi_quality: confloat(ge=0, le=5)
    atmosphere: Optional[str] = None
    energy_level: Optional[str] = None
    study_friendly: Optional[str] = None

    @classmethod
    def validate_rating_fields(cls, v):
        valid_ratings = ['Poor', 'Fair', 'Good', 'Excellent']
        if v not in valid_ratings:
            raise ValueError(f"Rating must be one of: {', '.join(valid_ratings)}")
        return v

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    overall_rating: Optional[confloat(ge=0, le=5)] = None
    outlet_accessibility: Optional[confloat(ge=0, le=5)] = None
    wifi_quality: Optional[confloat(ge=0, le=5)] = None
    atmosphere: Optional[str] = None
    energy_level: Optional[str] = None
    study_friendly: Optional[str] = None

    @classmethod
    def validate_rating_fields(cls, v):
        if v is not None:
            valid_ratings = ['Poor', 'Fair', 'Good', 'Excellent']
            if v not in valid_ratings:
                raise ValueError(f"Rating must be one of: {', '.join(valid_ratings)}")
        return v

class Review(ReviewBase):
    id: str = Field(..., alias="_id")
    photos: List[Photo] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "study_spot_id": "60d5ec49e9af8b2c24e8a1b2",
                "user_id": "user456",
                "overall_rating": 4.5,
                "outlet_accessibility": 4,
                "wifi_quality": 5,
                "atmosphere": "Quiet",
                "energy_level": "Calm",
                "study_friendly": "Very",
            }
        },
    ) 