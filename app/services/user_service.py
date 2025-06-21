from typing import List, Optional
from app.models.user import User, UserCreate, UserUpdate, UserResponse
from app.repositories.user_repository import UserRepository
from app.services.s3_service import S3Service
import os

class UserService:
    def __init__(self):
        self.repository = UserRepository()
        self.s3_service = S3Service()

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        user = await self.repository.create_user(user_data)
        return self._to_user_response(user)

    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """Get a user by ID"""
        user = await self.repository.get_user(user_id)
        if user:
            return self._to_user_response(user)
        return None

    async def get_user_by_name(self, name: str) -> Optional[User]:
        """Get a user by name (includes password for authentication)"""
        return await self.repository.get_user_by_name(name)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users with pagination"""
        users = await self.repository.get_all_users(skip, limit)
        return [self._to_user_response(user) for user in users]

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update a user"""
        # Convert to dict, excluding None values
        update_dict = {k: v for k, v in user_data.model_dump().items() if v is not None}
        
        if update_dict:
            user = await self.repository.update_user(user_id, update_dict)
            if user:
                return self._to_user_response(user)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        # Get user first to check if they have a profile picture
        user = await self.repository.get_user(user_id)
        if user and user.profile_picture:
            # Handle both URL-based (Digital Ocean Spaces) and filename-based (local) profile pictures
            if user.profile_picture.startswith('https://'):
                # Delete from Digital Ocean Spaces
                try:
                    await self.s3_service.delete_file(user.profile_picture)
                except Exception:
                    pass  # Continue with user deletion even if file deletion fails
            else:
                # Delete local profile picture file if it exists
                profile_pic_path = os.path.join("profile_pictures", user.profile_picture)
                if os.path.exists(profile_pic_path):
                    try:
                        os.remove(profile_pic_path)
                    except Exception:
                        pass  # Continue with user deletion even if file deletion fails
        
        return await self.repository.delete_user(user_id)

    async def update_profile_picture(self, user_id: str, filename: str) -> Optional[UserResponse]:
        """Update user's profile picture"""
        user = await self.repository.update_profile_picture(user_id, filename)
        if user:
            return self._to_user_response(user)
        return None

    async def search_users(self, query: str) -> List[UserResponse]:
        """Search users by name"""
        users = await self.repository.search_users(query)
        return [self._to_user_response(user) for user in users]

    async def authenticate_user(self, name: str, password: str) -> Optional[User]:
        """Authenticate a user with plain text password"""
        user = await self.repository.get_user_by_name(name)
        if user and user.password == password:
            return user
        return None

    def _to_user_response(self, user: User) -> UserResponse:
        """Convert User model to UserResponse (excludes password)"""
        # Use model_dump to get the data with proper field names, excluding password
        user_dict = user.model_dump(exclude={'password'}, by_alias=False)
        return UserResponse(**user_dict) 