from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
import shutil
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a review
@app.post("/reviews")
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Check if a review already exists by the same user for the same spot
    existing_review = db.query(models.Review).filter(
        models.Review.study_spot_id == review.studySpotId,
        models.Review.user_id == review.userId
    ).first()
    
    if existing_review:
        existing_review.overall_rating = review.overallRating
        existing_review.outlet_accessibility = review.outletAccessibility
        existing_review.wifi_quality = review.wifiQuality
        existing_review.atmosphere = review.atmosphere
        existing_review.energy_level = review.energyLevel
        existing_review.study_friendly = review.studyFriendly
        db.commit()
        db.refresh(existing_review)
        return {"review_id": existing_review.id, "message": "Review updated!"}
    
    # Otherwise, create a new review
    db_review = models.Review(
        study_spot_id=review.studySpotId,
        user_id=review.userId,
        overall_rating=review.overallRating,
        outlet_accessibility=review.outletAccessibility,
        wifi_quality=review.wifiQuality,
        atmosphere=review.atmosphere,
        energy_level=review.energyLevel,
        study_friendly=review.studyFriendly,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return {"review_id": db_review.id, "message": "Review saved!"}

# Upload photos separately
@app.post("/reviews/{review_id}/photos")
def upload_photos(review_id: int, photos: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    saved_files = []
    for photo in photos:
        file_path = os.path.join(UPLOAD_DIR, photo.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        db_photo = models.Photo(filename=photo.filename, review_id=review_id)
        db.add(db_photo)
        saved_files.append(photo.filename)

    db.commit()
    return {"message": "Photos uploaded", "files": saved_files}