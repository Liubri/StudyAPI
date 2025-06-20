from typing import List, Optional
from bson import ObjectId
from app.models.cafe import Cafe, CafeCreate
from app.config.database import Database
from datetime import datetime

class CafeRepository:
    def __init__(self):
        # Remove the immediate database access
        pass

    @property
    def collection(self):
        # Lazy loading - only get the collection when needed
        return Database.get_db().cafes

    async def create_cafe(self, cafe_data: CafeCreate) -> Cafe:
        cafe_dict = cafe_data.model_dump(by_alias=True)
        now = datetime.utcnow()
        cafe_dict["created_at"] = now
        cafe_dict["updated_at"] = now
        
        result = await self.collection.insert_one(cafe_dict)
        created_cafe = await self.collection.find_one({"_id": result.inserted_id})
        
        created_cafe["_id"] = str(created_cafe["_id"])
        return Cafe.model_validate(created_cafe)

    async def get_cafe(self, cafe_id: str) -> Optional[Cafe]:
        cafe = await self.collection.find_one({"_id": ObjectId(cafe_id)})
        if cafe:
            cafe["_id"] = str(cafe["_id"])
            return Cafe.model_validate(cafe)
        return None

    async def get_all_cafes(self) -> List[Cafe]:
        cursor = self.collection.find()
        cafes = await cursor.to_list(length=None)
        for cafe in cafes:
            cafe["_id"] = str(cafe["_id"])
        return [Cafe.model_validate(cafe) for cafe in cafes]

    async def update_cafe(self, cafe_id: str, cafe_data: dict) -> Optional[Cafe]:
        cafe_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(cafe_id)},
            {"$set": cafe_data}
        )
        if result.modified_count:
            updated_cafe = await self.collection.find_one({"_id": ObjectId(cafe_id)})
            if updated_cafe:
                updated_cafe["_id"] = str(updated_cafe["_id"])
                return Cafe.model_validate(updated_cafe)
        return None

    async def delete_cafe(self, cafe_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(cafe_id)})
        return result.deleted_count > 0

    async def search_cafes(self, query: str) -> List[Cafe]:
        cursor = self.collection.find({
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"address.city": {"$regex": query, "$options": "i"}},
                {"address.street": {"$regex": query, "$options": "i"}}
            ]
        })
        cafes = await cursor.to_list(length=None)
        for cafe in cafes:
            cafe["_id"] = str(cafe["_id"])
        return [Cafe.model_validate(cafe) for cafe in cafes]

    async def find_nearby_cafes(self, longitude: float, latitude: float, max_distance: float = 5000) -> List[Cafe]:
        """
        Find cafes within max_distance meters of the given coordinates
        """
        cursor = self.collection.find({
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": max_distance
                }
            }
        })
        cafes = await cursor.to_list(length=None)
        for cafe in cafes:
            cafe["_id"] = str(cafe["_id"])
        return [Cafe.model_validate(cafe) for cafe in cafes]

    async def find_cafes_by_amenities(self, amenities: List[str]) -> List[Cafe]:
        cursor = self.collection.find({
            "amenities": {"$all": amenities}
        })
        cafes = await cursor.to_list(length=None)
        for cafe in cafes:
            cafe["_id"] = str(cafe["_id"])
        return [Cafe.model_validate(cafe) for cafe in cafes]

    async def find_cafes_by_rating(self, min_rating: float) -> List[Cafe]:
        cursor = self.collection.find({
            "average_rating": {"$gte": min_rating}
        })
        cafes = await cursor.to_list(length=None)
        for cafe in cafes:
            cafe["_id"] = str(cafe["_id"])
        return [Cafe.model_validate(cafe) for cafe in cafes] 