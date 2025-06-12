from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    study_spot_id = Column(String)
    user_id = Column(String)
    overall_rating = Column(Float)
    outlet_accessibility = Column(String)
    wifi_quality = Column(String)
    atmosphere = Column(String, nullable=True)
    energy_level = Column(String, nullable=True)
    study_friendly = Column(String, nullable=True)

    photos = relationship("Photo", back_populates="review")

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    review_id = Column(Integer, ForeignKey("reviews.id"))

    review = relationship("Review", back_populates="photos")