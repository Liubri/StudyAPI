from pydantic import BaseModel
from typing import Optional

class ReviewCreate(BaseModel):
    studySpotId: str
    userId: str
    overallRating: float
    outletAccessibility: str
    wifiQuality: str
    atmosphere: Optional[str] = None
    energyLevel: Optional[str] = None
    studyFriendly: Optional[str] = None