from typing import List, Optional
from bson import ObjectId
from app.models.bookmark import Bookmark, BookmarkCreate, BookmarkWithCafe
from app.config.database import Database
from datetime import datetime

class BookmarkRepository:
    def __init__(self):
        # Remove the immediate database access
        pass

    @property
    def collection(self):
        # Lazy loading - only get the collection when needed
        return Database.get_db().bookmarks

    async def create_bookmark(self, bookmark_data: BookmarkCreate) -> Bookmark:
        """Create a new bookmark"""
        bookmark_dict = bookmark_data.model_dump(by_alias=True)
        bookmark_dict["user_id"] = ObjectId(bookmark_dict["user_id"])
        bookmark_dict["cafe_id"] = ObjectId(bookmark_dict["cafe_id"])
        bookmark_dict["bookmarked_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(bookmark_dict)
        created_bookmark = await self.collection.find_one({"_id": result.inserted_id})
        
        created_bookmark["_id"] = str(created_bookmark["_id"])
        created_bookmark["user_id"] = str(created_bookmark["user_id"])
        created_bookmark["cafe_id"] = str(created_bookmark["cafe_id"])
        
        return Bookmark.model_validate(created_bookmark)

    async def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
        """Get a bookmark by ID"""
        bookmark = await self.collection.find_one({"_id": ObjectId(bookmark_id)})
        if bookmark:
            bookmark["_id"] = str(bookmark["_id"])
            bookmark["user_id"] = str(bookmark["user_id"])
            bookmark["cafe_id"] = str(bookmark["cafe_id"])
            return Bookmark.model_validate(bookmark)
        return None

    async def get_bookmarks_by_user(self, user_id: str) -> List[BookmarkWithCafe]:
        """Get all bookmarks for a user, ordered by time (newest first), with cafe info"""
        # Use aggregation to join with cafes collection
        pipeline = [
            # Match bookmarks for this user
            {"$match": {"user_id": ObjectId(user_id)}},
            # Sort by bookmarked_at descending (newest first)
            {"$sort": {"bookmarked_at": -1}},
            # Join with cafes collection
            {
                "$lookup": {
                    "from": "cafes",
                    "localField": "cafe_id",
                    "foreignField": "_id",
                    "as": "cafe_info"
                }
            },
            # Unwind the cafe_info array (should be single item or empty)
            {
                "$unwind": {
                    "path": "$cafe_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            # Project the desired fields
            {
                "$project": {
                    "_id": 1,
                    "user_id": 1,
                    "cafe_id": 1,
                    "bookmarked_at": 1,
                    "cafe": {
                        "$cond": {
                            "if": {"$ne": ["$cafe_info", None]},
                            "then": {
                                "id": {"$toString": "$cafe_info._id"},
                                "name": "$cafe_info.name",
                                "address": "$cafe_info.address",
                                "location": "$cafe_info.location",
                                "average_rating": "$cafe_info.average_rating",
                                "thumbnail_url": "$cafe_info.thumbnail_url",
                                "amenities": "$cafe_info.amenities"
                            },
                            "else": None
                        }
                    }
                }
            }
        ]
        
        cursor = self.collection.aggregate(pipeline)
        bookmarks = await cursor.to_list(length=None)
        
        # Format the response
        formatted_bookmarks = []
        for bookmark in bookmarks:
            bookmark["_id"] = str(bookmark["_id"])
            bookmark["user_id"] = str(bookmark["user_id"])
            bookmark["cafe_id"] = str(bookmark["cafe_id"])
            formatted_bookmarks.append(BookmarkWithCafe.model_validate(bookmark))
        
        return formatted_bookmarks

    async def delete_bookmark(self, bookmark_id: str) -> bool:
        """Delete a bookmark by ID"""
        result = await self.collection.delete_one({"_id": ObjectId(bookmark_id)})
        return result.deleted_count > 0

    async def delete_bookmark_by_user_and_cafe(self, user_id: str, cafe_id: str) -> bool:
        """Delete a bookmark by user ID and cafe ID"""
        result = await self.collection.delete_one({
            "user_id": ObjectId(user_id),
            "cafe_id": ObjectId(cafe_id)
        })
        return result.deleted_count > 0

    async def get_bookmark_by_user_and_cafe(self, user_id: str, cafe_id: str) -> Optional[Bookmark]:
        """Get a bookmark by user ID and cafe ID"""
        bookmark = await self.collection.find_one({
            "user_id": ObjectId(user_id),
            "cafe_id": ObjectId(cafe_id)
        })
        if bookmark:
            bookmark["_id"] = str(bookmark["_id"])
            bookmark["user_id"] = str(bookmark["user_id"])
            bookmark["cafe_id"] = str(bookmark["cafe_id"])
            return Bookmark.model_validate(bookmark)
        return None

    async def bookmark_exists(self, user_id: str, cafe_id: str) -> bool:
        """Check if a bookmark already exists for a user and cafe"""
        count = await self.collection.count_documents({
            "user_id": ObjectId(user_id),
            "cafe_id": ObjectId(cafe_id)
        })
        return count > 0 