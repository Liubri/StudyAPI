from typing import List, Optional
from bson import ObjectId
from app.models.review import Review, Photo, ReviewCreate, PhotoCreate
from app.config.database import Database
from datetime import datetime

class ReviewRepository:
    def __init__(self):
        # Remove the immediate database access
        pass

    @property
    def collection(self):
        # Lazy loading - only get the collection when needed
        return Database.get_db().reviews

    async def create_review(self, review_data: ReviewCreate) -> Review:
        review_dict = review_data.model_dump(by_alias=True)
        review_dict["study_spot_id"] = ObjectId(review_dict["study_spot_id"])
        
        now = datetime.utcnow()
        review_dict['created_at'] = now
        review_dict['updated_at'] = now
        review_dict['photos'] = []

        result = await self.collection.insert_one(review_dict)
        created_review = await self.collection.find_one({"_id": result.inserted_id})
        
        created_review["_id"] = str(created_review["_id"])
        created_review["study_spot_id"] = str(created_review["study_spot_id"])
        
        return Review.model_validate(created_review)

    async def get_review(self, review_id: str) -> Optional[Review]:
        review = await self.collection.find_one({"_id": ObjectId(review_id)})
        if review:
            review["_id"] = str(review["_id"])
            review["study_spot_id"] = str(review["study_spot_id"])
            for photo in review.get("photos", []):
                photo["_id"] = str(photo["_id"])
            return Review.model_validate(review)
        return None

    async def get_reviews_by_study_spot(self, study_spot_id: str) -> List[Review]:
        cursor = self.collection.find({"study_spot_id": ObjectId(study_spot_id)})
        reviews = await cursor.to_list(length=None)
        for review in reviews:
            review["_id"] = str(review["_id"])
            review["study_spot_id"] = str(review["study_spot_id"])
            for photo in review.get("photos", []):
                photo["_id"] = str(photo["_id"])
        return [Review.model_validate(review) for review in reviews]

    async def update_review(self, review_id: str, review_data: dict) -> Optional[Review]:
        review_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": review_data}
        )
        if result.modified_count:
            updated_review = await self.collection.find_one({"_id": ObjectId(review_id)})
            if updated_review:
                updated_review["_id"] = str(updated_review["_id"])
                updated_review["study_spot_id"] = str(updated_review["study_spot_id"])
                for photo in updated_review.get("photos", []):
                    photo["_id"] = str(photo["_id"])
                return Review.model_validate(updated_review)
        return None

    async def delete_review(self, review_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(review_id)})
        return result.deleted_count > 0

    async def add_photo(self, review_id: str, photo_data: PhotoCreate) -> Optional[Review]:
        photo_dict = photo_data.model_dump(by_alias=True)
        photo_dict["_id"] = ObjectId()

        result = await self.collection.update_one(
            {"_id": ObjectId(review_id)},
            {"$push": {"photos": photo_dict}}
        )
        if result.modified_count:
            return await self.get_review(review_id)
        return None 