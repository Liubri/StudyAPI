from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class BookmarkBase(BaseModel):
    user_id: str = Field(..., example="60d5ec49e9af8b2c24e8a1b2", description="ID of the user who created the bookmark")
    cafe_id: str = Field(..., example="60d5ec49e9af8b2c24e8a1b3", description="ID of the cafe being bookmarked")

class BookmarkCreate(BookmarkBase):
    pass

class BookmarkUpdate(BaseModel):
    # Bookmarks are simple - only the timestamp might be updated, but that's automatic
    pass

class Bookmark(BookmarkBase):
    id: str = Field(..., alias="_id", example="60d5ec49e9af8b2c24e8a1b4")
    bookmarked_at: datetime = Field(default_factory=datetime.utcnow, example="2024-01-15T10:30:00Z", description="When the bookmark was created")
    
    model_config = ConfigDict(
        populate_by_name=True,
        allow_population_by_field_name=True,
        ser_by_alias=False,
        json_schema_extra={
            "example": {
                "id": "60d5ec49e9af8b2c24e8a1b4",
                "user_id": "60d5ec49e9af8b2c24e8a1b2",
                "cafe_id": "60d5ec49e9af8b2c24e8a1b3",
                "bookmarked_at": "2024-01-15T10:30:00Z"
            }
        }
    )

class BookmarkWithCafe(BaseModel):
    """Bookmark with populated cafe information"""
    id: str = Field(..., alias="_id", example="60d5ec49e9af8b2c24e8a1b4")
    user_id: str = Field(..., example="60d5ec49e9af8b2c24e8a1b2")
    cafe_id: str = Field(..., example="60d5ec49e9af8b2c24e8a1b3")
    bookmarked_at: datetime = Field(..., example="2024-01-15T10:30:00Z")
    cafe: Optional[dict] = Field(None, description="Populated cafe information")
    
    model_config = ConfigDict(
        populate_by_name=True,
        allow_population_by_field_name=True,
        ser_by_alias=False,
        json_schema_extra={
            "example": {
                "id": "60d5ec49e9af8b2c24e8a1b4",
                "user_id": "60d5ec49e9af8b2c24e8a1b2", 
                "cafe_id": "60d5ec49e9af8b2c24e8a1b3",
                "bookmarked_at": "2024-01-15T10:30:00Z",
                "cafe": {
                    "id": "60d5ec49e9af8b2c24e8a1b3",
                    "name": "The Coffee Corner",
                    "address": {
                        "street": "123 Main St",
                        "city": "San Francisco",
                        "state": "CA"
                    },
                    "average_rating": 4
                }
            }
        }
    ) 