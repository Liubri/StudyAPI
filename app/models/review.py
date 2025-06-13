from pydantic import BaseModel, Field, validator, confloat
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class PhotoBase(BaseModel):
    filename: str

class PhotoCreate(PhotoBase):
    pass

class Photo(PhotoBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class ReviewBase(BaseModel):
    study_spot_id: str
    user_id: str
    overall_rating: confloat(ge=0, le=5)
    outlet_accessibility: str
    wifi_quality: str
    atmosphere: Optional[str] = None
    energy_level: Optional[str] = None
    study_friendly: Optional[str] = None

    @validator('outlet_accessibility', 'wifi_quality')
    def validate_rating_fields(cls, v):
        valid_ratings = ['Poor', 'Fair', 'Good', 'Excellent']
        if v not in valid_ratings:
            raise ValueError(f"Rating must be one of: {', '.join(valid_ratings)}")
        return v

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    overall_rating: Optional[confloat(ge=0, le=5)] = None
    outlet_accessibility: Optional[str] = None
    wifi_quality: Optional[str] = None
    atmosphere: Optional[str] = None
    energy_level: Optional[str] = None
    study_friendly: Optional[str] = None

    @validator('outlet_accessibility', 'wifi_quality')
    def validate_rating_fields(cls, v):
        if v is not None:
            valid_ratings = ['Poor', 'Fair', 'Good', 'Excellent']
            if v not in valid_ratings:
                raise ValueError(f"Rating must be one of: {', '.join(valid_ratings)}")
        return v

class Review(ReviewBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    photos: List[Photo] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "study_spot_id": "spot123",
                "user_id": "user456",
                "overall_rating": 4.5,
                "outlet_accessibility": "Good",
                "wifi_quality": "Excellent",
                "atmosphere": "Quiet",
                "energy_level": "Calm",
                "study_friendly": "Very"
            }
        } 