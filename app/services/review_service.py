from typing import List, Optional
from app.models.review import Review, PhotoCreate, ReviewCreate
from app.repositories.review_repository import ReviewRepository

class ReviewService:
    def __init__(self):
        self.repository = ReviewRepository()

    async def create_review(self, review_data: ReviewCreate) -> Review:
        return await self.repository.create_review(review_data)

    async def get_review(self, review_id: str) -> Optional[Review]:
        return await self.repository.get_review(review_id)

    async def get_reviews_by_study_spot(self, study_spot_id: str) -> List[Review]:
        return await self.repository.get_reviews_by_study_spot(study_spot_id)

    async def update_review(self, review_id: str, review_data: dict) -> Optional[Review]:
        # Validate the review exists
        existing_review = await self.get_review(review_id)
        if not existing_review:
            return None
        
        return await self.repository.update_review(review_id, review_data)

    async def delete_review(self, review_id: str) -> bool:
        return await self.repository.delete_review(review_id)

    async def add_photo(self, review_id: str, photo_data: PhotoCreate) -> Optional[Review]:
        # Validate the review exists
        existing_review = await self.get_review(review_id)
        if not existing_review:
            return None

        return await self.repository.add_photo(review_id, photo_data) 