from typing import List, Optional
from app.models.review import Review, PhotoCreate, ReviewCreate
from app.repositories.review_repository import ReviewRepository
from app.services.cafe_service import CafeService
from app.config.logging_config import logger

class ReviewService:
    def __init__(self):
        self.repository = ReviewRepository()
        self.cafe_service = CafeService()

    async def create_review(self, review_data: ReviewCreate) -> Review:
        # Create the review
        created_review = await self.repository.create_review(review_data)
        
        # Automatically update the cafe's average rating
        try:
            logger.info(f"Updating average rating for cafe {review_data.study_spot_id} after new review")
            await self.cafe_service.update_cafe_average_rating(review_data.study_spot_id)
        except Exception as e:
            logger.error(f"Failed to update cafe average rating after review creation: {str(e)}")
            # Don't fail the review creation if rating update fails
        
        return created_review

    async def get_review(self, review_id: str) -> Optional[Review]:
        return await self.repository.get_review(review_id)

    async def get_reviews_by_study_spot(self, study_spot_id: str) -> List[Review]:
        return await self.repository.get_reviews_by_study_spot(study_spot_id)

    async def get_reviews_by_user(self, user_id: str) -> List[Review]:
        return await self.repository.get_reviews_by_user(user_id)

    async def update_review(self, review_id: str, review_data: dict) -> Optional[Review]:
        # Validate the review exists
        existing_review = await self.get_review(review_id)
        if not existing_review:
            return None
        
        # Update the review
        updated_review = await self.repository.update_review(review_id, review_data)
        
        # If the overall_rating was updated, recalculate cafe average
        if updated_review and "overall_rating" in review_data:
            try:
                logger.info(f"Updating average rating for cafe {existing_review.study_spot_id} after review update")
                await self.cafe_service.update_cafe_average_rating(existing_review.study_spot_id)
            except Exception as e:
                logger.error(f"Failed to update cafe average rating after review update: {str(e)}")
        
        return updated_review

    async def delete_review(self, review_id: str) -> bool:
        # Get the review before deleting to know which cafe to update
        review_to_delete = await self.get_review(review_id)
        if not review_to_delete:
            return False
        
        # Delete the review
        deleted = await self.repository.delete_review(review_id)
        
        # Update the cafe's average rating after deletion
        if deleted:
            try:
                logger.info(f"Updating average rating for cafe {review_to_delete.study_spot_id} after review deletion")
                await self.cafe_service.update_cafe_average_rating(review_to_delete.study_spot_id)
            except Exception as e:
                logger.error(f"Failed to update cafe average rating after review deletion: {str(e)}")
        
        return deleted

    async def add_photo(self, review_id: str, photo_data: PhotoCreate) -> Optional[Review]:
        # Validate the review exists
        existing_review = await self.get_review(review_id)
        if not existing_review:
            return None

        return await self.repository.add_photo(review_id, photo_data) 