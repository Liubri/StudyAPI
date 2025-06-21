from typing import List, Optional
from fastapi import HTTPException, UploadFile
from app.models.user import UserCreate, UserUpdate, UserResponse, UserLogin, LoginResponse
from app.services.user_service import UserService
from app.config.logging_config import logger
import os
import shutil

class UserController:
    def __init__(self):
        self.service = UserService()
        self.profile_pics_dir = "profile_pictures"
        os.makedirs(self.profile_pics_dir, exist_ok=True)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        try:
            logger.info(f"Controller: Received request to create user: {user_data.name}")
            user = await self.service.create_user(user_data)
            logger.info(f"Controller: Successfully created user with ID: {user.id}")
            return user
        except ValueError as e:
            logger.error(f"Controller: Validation error creating user - {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Controller: Unexpected error creating user: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    async def get_user(self, user_id: str) -> UserResponse:
        """Get a user by ID"""
        logger.info(f"Controller: Received request to get user with ID: {user_id}")
        user = await self.service.get_user(user_id)
        if not user:
            logger.warning(f"Controller: User not found with ID: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users with pagination"""
        logger.info(f"Controller: Received request to get all users (skip={skip}, limit={limit})")
        return await self.service.get_all_users(skip, limit)

    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """Update a user"""
        logger.info(f"Controller: Received request to update user with ID: {user_id}")
        try:
            updated_user = await self.service.update_user(user_id, user_data)
            if not updated_user:
                logger.warning(f"Controller: User not found for update with ID: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
            logger.info(f"Controller: Successfully updated user with ID: {user_id}")
            return updated_user
        except ValueError as e:
            logger.error(f"Controller: Validation error updating user - {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Controller: Unexpected error updating user: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    async def delete_user(self, user_id: str) -> dict:
        """Delete a user"""
        logger.info(f"Controller: Received request to delete user with ID: {user_id}")
        success = await self.service.delete_user(user_id)
        if not success:
            logger.warning(f"Controller: User not found for deletion with ID: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Controller: Successfully deleted user with ID: {user_id}")
        return {"message": "User deleted successfully"}

    async def upload_profile_picture(self, user_id: str, file: UploadFile) -> dict:
        """Upload profile picture for a user"""
        logger.info(f"Controller: Received request to upload profile picture for user ID: {user_id}")
        
        # Check if user exists
        user = await self.service.get_user(user_id)
        if not user:
            logger.warning(f"Controller: User not found for profile picture upload with ID: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Delete old profile picture if it exists
            if user.profile_picture:
                old_pic_path = os.path.join(self.profile_pics_dir, user.profile_picture)
                if os.path.exists(old_pic_path):
                    os.remove(old_pic_path)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
            new_filename = f"user_{user_id}_profile{file_extension}"
            file_path = os.path.join(self.profile_pics_dir, new_filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Update user record
            updated_user = await self.service.update_profile_picture(user_id, new_filename)
            if not updated_user:
                # If update failed, remove the uploaded file
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(status_code=500, detail="Failed to update user profile picture")
            
            logger.info(f"Controller: Successfully uploaded profile picture for user ID: {user_id}")
            return {"message": "Profile picture uploaded successfully", "filename": new_filename}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Controller: Error uploading profile picture: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to upload profile picture")

    async def search_users(self, query: str) -> List[UserResponse]:
        """Search users by name"""
        logger.info(f"Controller: Received request to search users with query: '{query}'")
        return await self.service.search_users(query)

    async def login(self, login_data: UserLogin) -> LoginResponse:
        """Authenticate user login"""
        logger.info(f"Controller: Received login request for user: {login_data.name}")
        
        user = await self.service.authenticate_user(login_data.name, login_data.password)
        if not user:
            logger.warning(f"Controller: Invalid login attempt for user: {login_data.name}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        logger.info(f"Controller: Successful login for user: {login_data.name}")
        return LoginResponse(
            message="Login successful",
            user_id=user.id,
            user_name=user.name
        ) 