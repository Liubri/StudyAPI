from typing import List, Optional
from fastapi import HTTPException, UploadFile
from app.models.user import UserCreate, UserUpdate, UserResponse, UserLogin, LoginResponse
from app.services.user_service import UserService
from app.services.s3_service import S3Service
from app.config.logging_config import logger
import os
import shutil

class UserController:
    def __init__(self):
        self.service = UserService()
        self.s3_service = S3Service()
        # Keep profile_pics_dir for backwards compatibility with existing cleanup code
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
        """Upload profile picture for a user to Digital Ocean Spaces"""
        logger.info(f"Controller: Received request to upload profile picture for user ID: {user_id}")
        logger.info(f"Controller: File details - name: '{file.filename}', content_type: '{file.content_type}', size: {file.size if hasattr(file, 'size') else 'unknown'}")
        
        # Check if user exists
        user = await self.service.get_user(user_id)
        if not user:
            logger.warning(f"Controller: User not found for profile picture upload with ID: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Controller: User found - current profile picture: {user.profile_picture}")
        
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                logger.error(f"Controller: Invalid file type: {file.content_type}")
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Delete old profile picture from Digital Ocean Spaces if it exists
            if user.profile_picture and user.profile_picture.startswith('https://'):
                # If it's a URL (from Digital Ocean Spaces), delete it
                logger.info(f"Controller: Attempting to delete old profile picture from S3: {user.profile_picture}")
                try:
                    await self.s3_service.delete_file(user.profile_picture)
                    logger.info("Controller: Successfully deleted old profile picture from S3")
                except Exception as e:
                    logger.warning(f"Failed to delete old profile picture from S3: {str(e)}")
            elif user.profile_picture:
                # If it's a local filename (legacy), delete local file
                old_pic_path = os.path.join(self.profile_pics_dir, user.profile_picture)
                logger.info(f"Controller: Attempting to delete old local profile picture: {old_pic_path}")
                if os.path.exists(old_pic_path):
                    try:
                        os.remove(old_pic_path)
                        logger.info("Controller: Successfully deleted old local profile picture")
                    except Exception as e:
                        logger.warning(f"Failed to delete old local profile picture: {str(e)}")
            
            # Upload to Digital Ocean Spaces
            logger.info("Controller: Starting upload to Digital Ocean Spaces")
            file_url = await self.s3_service.upload_file(file, folder="profile-pictures")
            logger.info(f"Controller: Upload successful! File URL: {file_url}")
            print(f"🖼️  PROFILE PICTURE UPLOADED: {file_url}")  # Print to console for immediate visibility
            
            # Update user record with the full URL
            logger.info(f"Controller: Updating user record with new profile picture URL")
            updated_user = await self.service.update_profile_picture(user_id, file_url)
            if not updated_user:
                logger.error("Controller: Failed to update user record with new profile picture")
                # If update failed, try to delete the uploaded file
                try:
                    await self.s3_service.delete_file(file_url)
                    logger.info("Controller: Cleaned up uploaded file after database update failure")
                except Exception:
                    logger.warning("Controller: Failed to clean up uploaded file after database update failure")
                raise HTTPException(status_code=500, detail="Failed to update user profile picture")
            
            logger.info(f"Controller: Successfully uploaded profile picture for user ID: {user_id}")
            response = {
                "message": "Profile picture uploaded successfully", 
                "url": file_url,
                "filename": file_url.split('/')[-1]  # Extract filename from URL for backwards compatibility
            }
            logger.info(f"Controller: Returning response: {response}")
            return response
            
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