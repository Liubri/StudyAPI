from typing import List
from fastapi import HTTPException
from app.models.review import Review, ReviewCreate, ReviewUpdate, Photo, PhotoCreate
from app.services.review_service import ReviewService

class ReviewController:
    def __init__(self):
        self.service = ReviewService()

    async def create_review(self, review_data: ReviewCreate) -> Review:
        try:
            review = Review(**review_data.dict())
            return await self.service.create_review(review)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")

    async def get_review(self, review_id: str) -> Review:
        review = await self.service.get_review(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review

    async def get_reviews_by_study_spot(self, study_spot_id: str) -> List[Review]:
        return await self.service.get_reviews_by_study_spot(study_spot_id)

    async def update_review(self, review_id: str, review_data: ReviewUpdate) -> Review:
        # Validate the review exists
        existing_review = await self.service.get_review(review_id)
        if not existing_review:
            raise HTTPException(status_code=404, detail="Review not found")

        # Update the review with validated data
        updated_review = await self.service.update_review(review_id, review_data.dict(exclude_unset=True))
        if not updated_review:
            raise HTTPException(status_code=500, detail="Failed to update review")
        return updated_review

    async def delete_review(self, review_id: str) -> bool:
        # Validate the review exists
        existing_review = await self.service.get_review(review_id)
        if not existing_review:
            raise HTTPException(status_code=404, detail="Review not found")

        success = await self.service.delete_review(review_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete review")
        return success

    async def add_photo(self, review_id: str, photo_data: PhotoCreate) -> Review:
        # Validate the review exists
        existing_review = await self.service.get_review(review_id)
        if not existing_review:
            raise HTTPException(status_code=404, detail="Review not found")

        # Create Photo model instance
        photo = Photo(**photo_data.dict())
        updated_review = await self.service.add_photo(review_id, photo)
        if not updated_review:
            raise HTTPException(status_code=500, detail="Failed to add photo")
        return updated_review 