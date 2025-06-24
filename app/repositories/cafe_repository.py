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

    async def get_cafe_photos(self, cafe_id: str) -> List[dict]:
        """Get all photos for a specific cafe from all reviews"""
        # Access the reviews collection to find reviews for this cafe
        reviews_collection = Database.get_db().reviews
        
        # Aggregate photos from all reviews for this cafe
        pipeline = [
            # Match reviews for this specific cafe
            {"$match": {"study_spot_id": ObjectId(cafe_id)}},
            # Unwind the photos array to get individual photos
            {"$unwind": "$photos"},
            # Project the desired fields
            {"$project": {
                "photo_id": "$photos._id",
                "url": "$photos.url", 
                "caption": "$photos.caption",
                "review_id": "$_id",
                "user_id": "$user_id",
                "created_at": "$created_at"
            }}
        ]
        
        cursor = reviews_collection.aggregate(pipeline)
        photos = await cursor.to_list(length=None)
        
        # Format the response
        formatted_photos = []
        for photo in photos:
            formatted_photos.append({
                "id": str(photo["photo_id"]),
                "url": photo["url"],
                "caption": photo.get("caption", ""),
                "review_id": str(photo["review_id"]),
                "user_id": photo["user_id"],
                "created_at": photo["created_at"]
            })
        
        return formatted_photos

    async def update_all_cafes_with_array_fields(self):
        """Update all existing cafes to have array-based tag fields with 4-5 entries each"""
        import random
        
        # Define the new field options
        atmosphere_options = ["Cozy", "Rustic", "Traditional", "Warm", "Clean", "Industrial", "Basic", "Modern", "Elegant", "Casual"]
        energy_level_options = ["quiet", "low-key", "tranquil", "moderate", "average", "Loud", "energetic", "vibrant", "bustling", "peaceful"]
        study_friendly_levels = ["study heaven", "good", "decent", "mixed", "fair", "excellent", "poor", "perfect", "okay", "great", "Mixed"]
        
        # Get all cafes (both with and without the fields, to convert singles to arrays)
        all_cafes = await self.collection.find({}).to_list(length=None)
        
        updated_count = 0
        for cafe in all_cafes:
            update_data = {}
            
            # Handle atmosphere field
            current_atmosphere = cafe.get("atmosphere")
            if not current_atmosphere or not isinstance(current_atmosphere, list):
                # Generate 4-5 unique atmosphere tags
                num_tags = random.randint(4, min(5, len(atmosphere_options)))
                update_data["atmosphere"] = random.sample(atmosphere_options, num_tags)
            
            # Handle energy_level field
            current_energy = cafe.get("energy_level")
            if not current_energy or not isinstance(current_energy, list):
                # Generate 4-5 unique energy level tags
                num_tags = random.randint(4, min(5, len(energy_level_options)))
                update_data["energy_level"] = random.sample(energy_level_options, num_tags)
            
            # Handle study_friendly field
            current_study = cafe.get("study_friendly")
            if not current_study or not isinstance(current_study, list):
                # Generate 4-5 unique study friendly tags
                num_tags = random.randint(4, min(5, len(study_friendly_levels)))
                update_data["study_friendly"] = random.sample(study_friendly_levels, num_tags)
            
            # Only update if we have changes to make
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.collection.update_one(
                    {"_id": cafe["_id"]},
                    {"$set": update_data}
                )
                
                if result.modified_count:
                    updated_count += 1
        
        return updated_count

    async def calculate_average_rating_from_reviews(self, cafe_id: str) -> Optional[float]:
        """Calculate the average overall_rating from all reviews for a specific cafe"""
        from bson import ObjectId
        
        # Access the reviews collection
        reviews_collection = Database.get_db().reviews
        
        # Aggregate to calculate average rating
        pipeline = [
            # Match reviews for this specific cafe
            {"$match": {"study_spot_id": ObjectId(cafe_id)}},
            # Group and calculate average
            {"$group": {
                "_id": None,
                "average_rating": {"$avg": "$overall_rating"},
                "review_count": {"$sum": 1}
            }}
        ]
        
        cursor = reviews_collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        if result and result[0]["review_count"] > 0:
            return result[0]["average_rating"]
        
        return None 