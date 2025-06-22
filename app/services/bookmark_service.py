from typing import List, Optional
from fastapi import HTTPException
from app.models.bookmark import Bookmark, BookmarkCreate, BookmarkWithCafe
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.user_repository import UserRepository
from app.repositories.cafe_repository import CafeRepository
from app.config.logging_config import logger

class BookmarkService:
    def __init__(self):
        self.repository = BookmarkRepository()
        self.user_repository = UserRepository()
        self.cafe_repository = CafeRepository()

    async def create_bookmark(self, bookmark_data: BookmarkCreate) -> Bookmark:
        """Create a new bookmark"""
        logger.info(f"Service: Creating bookmark for user {bookmark_data.user_id} and cafe {bookmark_data.cafe_id}")
        
        # Validate that user exists
        user = await self.user_repository.get_user(bookmark_data.user_id)
        if not user:
            logger.error(f"Service: User not found: {bookmark_data.user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate that cafe exists
        cafe = await self.cafe_repository.get_cafe(bookmark_data.cafe_id)
        if not cafe:
            logger.error(f"Service: Cafe not found: {bookmark_data.cafe_id}")
            raise HTTPException(status_code=404, detail="Cafe not found")
        
        # Check if bookmark already exists
        if await self.repository.bookmark_exists(bookmark_data.user_id, bookmark_data.cafe_id):
            logger.warning(f"Service: Bookmark already exists for user {bookmark_data.user_id} and cafe {bookmark_data.cafe_id}")
            raise HTTPException(status_code=409, detail="Bookmark already exists")
        
        try:
            created_bookmark = await self.repository.create_bookmark(bookmark_data)
            logger.info(f"Service: Successfully created bookmark with ID: {created_bookmark.id}")
            return created_bookmark
        except Exception as e:
            logger.error(f"Service: Failed to create bookmark: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create bookmark: {str(e)}")

    async def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
        """Get a bookmark by ID"""
        logger.info(f"Service: Fetching bookmark with ID: {bookmark_id}")
        return await self.repository.get_bookmark(bookmark_id)

    async def get_bookmarks_by_user(self, user_id: str) -> List[BookmarkWithCafe]:
        """Get all bookmarks for a user, ordered by time"""
        logger.info(f"Service: Fetching bookmarks for user: {user_id}")
        
        # Validate that user exists
        user = await self.user_repository.get_user(user_id)
        if not user:
            logger.error(f"Service: User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        bookmarks = await self.repository.get_bookmarks_by_user(user_id)
        logger.info(f"Service: Found {len(bookmarks)} bookmarks for user {user_id}")
        return bookmarks

    async def delete_bookmark(self, bookmark_id: str) -> bool:
        """Delete a bookmark by ID"""
        logger.info(f"Service: Deleting bookmark with ID: {bookmark_id}")
        
        # Check if bookmark exists
        bookmark = await self.get_bookmark(bookmark_id)
        if not bookmark:
            logger.warning(f"Service: Bookmark not found: {bookmark_id}")
            raise HTTPException(status_code=404, detail="Bookmark not found")
        
        success = await self.repository.delete_bookmark(bookmark_id)
        if success:
            logger.info(f"Service: Successfully deleted bookmark {bookmark_id}")
        else:
            logger.error(f"Service: Failed to delete bookmark {bookmark_id}")
        
        return success

    async def delete_bookmark_by_user_and_cafe(self, user_id: str, cafe_id: str) -> bool:
        """Delete a bookmark by user ID and cafe ID"""
        logger.info(f"Service: Deleting bookmark for user {user_id} and cafe {cafe_id}")
        
        # Check if bookmark exists
        bookmark = await self.repository.get_bookmark_by_user_and_cafe(user_id, cafe_id)
        if not bookmark:
            logger.warning(f"Service: Bookmark not found for user {user_id} and cafe {cafe_id}")
            raise HTTPException(status_code=404, detail="Bookmark not found")
        
        success = await self.repository.delete_bookmark_by_user_and_cafe(user_id, cafe_id)
        if success:
            logger.info(f"Service: Successfully deleted bookmark for user {user_id} and cafe {cafe_id}")
        else:
            logger.error(f"Service: Failed to delete bookmark for user {user_id} and cafe {cafe_id}")
        
        return success

    async def check_bookmark_exists(self, user_id: str, cafe_id: str) -> bool:
        """Check if a bookmark exists for a user and cafe"""
        logger.info(f"Service: Checking if bookmark exists for user {user_id} and cafe {cafe_id}")
        return await self.repository.bookmark_exists(user_id, cafe_id) 