from pydantic import BaseModel, Field, ConfigDict, conint, constr, confloat
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: constr(min_length=1, max_length=100) = Field(..., example="Alice Coffee", description="Unique username")
    cafes_visited: conint(ge=0) = Field(default=0, example=5, description="Number of cafes visited")
    average_rating: confloat(ge=0.0, le=5.0) = Field(default=0.0, example=4.2, description="User's average rating")

class UserCreate(UserBase):
    password: constr(min_length=1) = Field(..., example="mypassword123", description="Plain text password")

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = Field(None, example="Alice New Name")
    cafes_visited: Optional[conint(ge=0)] = Field(None, example=8)
    average_rating: Optional[confloat(ge=0.0, le=5.0)] = Field(None, example=4.5)
    password: Optional[constr(min_length=1)] = Field(None, example="newpassword456")

class UserResponse(UserBase):
    id: str = Field(..., alias="_id", example="60d5ec49e9af8b2c24e8a1b2")
    profile_picture: Optional[str] = Field(None, example="https://madstudycafe.nyc3.digitaloceanspaces.com/profile-pictures/user_1_profile.jpg", description="Profile picture URL or filename")
    created_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")
    updated_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")

    model_config = ConfigDict(
        populate_by_name=True,
        allow_population_by_field_name=True,
        ser_by_alias=False,  # This ensures serialization uses field names, not aliases
        json_schema_extra={
            "example": {
                "id": "60d5ec49e9af8b2c24e8a1b2",
                "name": "Alice Coffee",
                "cafes_visited": 5,
                "average_rating": 4.2,
                "profile_picture": "user_1_profile.jpg",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )

class User(UserBase):
    id: str = Field(..., alias="_id", example="60d5ec49e9af8b2c24e8a1b2")
    password: str = Field(..., description="Plain text password (hidden in response)")
    profile_picture: Optional[str] = Field(None, example="https://madstudycafe.nyc3.digitaloceanspaces.com/profile-pictures/user_1_profile.jpg")
    created_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")
    updated_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z")

    model_config = ConfigDict(
        populate_by_name=True,
        allow_population_by_field_name=True,
        ser_by_alias=False  # This ensures serialization uses field names, not aliases
    )

class UserLogin(BaseModel):
    name: str = Field(..., example="Alice Coffee", description="Username")
    password: str = Field(..., example="mypassword123", description="Plain text password")

class LoginResponse(BaseModel):
    message: str = Field(..., example="Login successful")
    user_id: str = Field(..., example="60d5ec49e9af8b2c24e8a1b2")
    user_name: str = Field(..., example="Alice Coffee")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Login successful",
                "user_id": "60d5ec49e9af8b2c24e8a1b2", 
                "user_name": "Alice Coffee"
            }
        }
    ) 