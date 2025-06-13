from typing import List, Optional
from bson import ObjectId
from app.models.review import Review, Photo
from app.config.database import Database
from datetime import datetime

class ReviewRepository:
    def __init__(self):
        self.collection = Database.get_db().reviews

    async def create_review(self, review: Review) -> Review:
        review_dict = review.dict(by_alias=True)
        result = await self.collection.insert_one(review_dict)
        created_review = await self.collection.find_one({"_id": result.inserted_id})
        return Review(**created_review)

    async def get_review(self, review_id: str) -> Optional[Review]:
        review = await self.collection.find_one({"_id": ObjectId(review_id)})
        return Review(**review) if review else None

    async def get_reviews_by_study_spot(self, study_spot_id: str) -> List[Review]:
        cursor = self.collection.find({"study_spot_id": study_spot_id})
        reviews = await cursor.to_list(length=None)
        return [Review(**review) for review in reviews]

    async def update_review(self, review_id: str, review_data: dict) -> Optional[Review]:
        review_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": review_data}
        )
        if result.modified_count:
            updated_review = await self.collection.find_one({"_id": ObjectId(review_id)})
            return Review(**updated_review)
        return None

    async def delete_review(self, review_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(review_id)})
        return result.deleted_count > 0

    async def add_photo(self, review_id: str, photo: Photo) -> Optional[Review]:
        result = await self.collection.update_one(
            {"_id": ObjectId(review_id)},
            {"$push": {"photos": photo.dict(by_alias=True)}}
        )
        if result.modified_count:
            updated_review = await self.collection.find_one({"_id": ObjectId(review_id)})
            return Review(**updated_review)
        return None 