from typing import List, Optional
from bson import ObjectId
from app.models.user import User, UserCreate
from app.config.database import Database
from datetime import datetime

class UserRepository:
    def __init__(self):
        # Remove the immediate database access
        pass

    @property
    def collection(self):
        # Lazy loading - only get the collection when needed
        return Database.get_db().users

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user with same name already exists
        existing_user = await self.collection.find_one({"name": user_data.name})
        if existing_user:
            raise ValueError("User with this name already exists")
        
        user_dict = user_data.model_dump(by_alias=True)
        now = datetime.utcnow()
        user_dict["created_at"] = now
        user_dict["updated_at"] = now
        user_dict["profile_picture"] = None  # Initialize as None
        
        result = await self.collection.insert_one(user_dict)
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        
        created_user["_id"] = str(created_user["_id"])
        return User.model_validate(created_user)

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
                return User.model_validate(user)
            return None
        except Exception:
            return None

    async def get_user_by_name(self, name: str) -> Optional[User]:
        """Get a user by name"""
        user = await self.collection.find_one({"name": name})
        if user:
            user["_id"] = str(user["_id"])
            return User.model_validate(user)
        return None

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        users = await cursor.to_list(length=None)
        for user in users:
            user["_id"] = str(user["_id"])
        return [User.model_validate(user) for user in users]

    async def update_user(self, user_id: str, user_data: dict) -> Optional[User]:
        """Update a user"""
        try:
            # If updating name, check for uniqueness
            if "name" in user_data:
                existing_user = await self.collection.find_one({
                    "name": user_data["name"],
                    "_id": {"$ne": ObjectId(user_id)}
                })
                if existing_user:
                    raise ValueError("User with this name already exists")
            
            user_data["updated_at"] = datetime.utcnow()
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": user_data}
            )
            if result.modified_count:
                updated_user = await self.collection.find_one({"_id": ObjectId(user_id)})
                if updated_user:
                    updated_user["_id"] = str(updated_user["_id"])
                    return User.model_validate(updated_user)
            return None
        except Exception:
            return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def update_profile_picture(self, user_id: str, filename: str) -> Optional[User]:
        """Update user's profile picture"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"profile_picture": filename, "updated_at": datetime.utcnow()}}
            )
            if result.modified_count:
                updated_user = await self.collection.find_one({"_id": ObjectId(user_id)})
                if updated_user:
                    updated_user["_id"] = str(updated_user["_id"])
                    return User.model_validate(updated_user)
            return None
        except Exception:
            return None

    async def search_users(self, query: str) -> List[User]:
        """Search users by name"""
        cursor = self.collection.find({
            "name": {"$regex": query, "$options": "i"}
        })
        users = await cursor.to_list(length=None)
        for user in users:
            user["_id"] = str(user["_id"])
        return [User.model_validate(user) for user in users] 