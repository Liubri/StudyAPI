from typing import List
from fastapi import HTTPException
from app.models.bookmark import Bookmark, BookmarkCreate, BookmarkWithCafe
from app.services.bookmark_service import BookmarkService
from app.config.logging_config import logger

class BookmarkController:
    def __init__(self):
        self.service = BookmarkService()

    async def create_bookmark(self, bookmark_data: BookmarkCreate) -> Bookmark:
        """Create a new bookmark"""
        try:
            logger.info(f"Controller: Received request to create bookmark for user {bookmark_data.user_id} and cafe {bookmark_data.cafe_id}")
            bookmark = await self.service.create_bookmark(bookmark_data)
            logger.info(f"Controller: Successfully created bookmark with ID: {bookmark.id}")
            return bookmark
        except HTTPException as e:
            logger.error(f"Controller: Error creating bookmark - {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Controller: Unexpected error creating bookmark: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    async def get_bookmark(self, bookmark_id: str) -> Bookmark:
        """Get a bookmark by ID"""
        logger.info(f"Controller: Received request to get bookmark with ID: {bookmark_id}")
        bookmark = await self.service.get_bookmark(bookmark_id)
        if not bookmark:
            logger.warning(f"Controller: Bookmark not found with ID: {bookmark_id}")
            raise HTTPException(status_code=404, detail="Bookmark not found")
        return bookmark

    async def get_bookmarks_by_user(self, user_id: str) -> List[BookmarkWithCafe]:
        """Get all bookmarks for a user, ordered by time"""
        logger.info(f"Controller: Received request to get bookmarks for user: {user_id}")
        try:
            bookmarks = await self.service.get_bookmarks_by_user(user_id)
            logger.info(f"Controller: Found {len(bookmarks)} bookmarks for user {user_id}")
            return bookmarks
        except HTTPException as e:
            logger.error(f"Controller: Error getting bookmarks for user {user_id} - {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Controller: Unexpected error getting bookmarks for user {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    async def delete_bookmark(self, bookmark_id: str) -> dict:
        """Delete a bookmark by ID"""
        logger.info(f"Controller: Received request to delete bookmark with ID: {bookmark_id}")
        try:
            success = await self.service.delete_bookmark(bookmark_id)
            if not success:
                logger.warning(f"Controller: Failed to delete bookmark with ID: {bookmark_id}")
                raise HTTPException(status_code=500, detail="Failed to delete bookmark")
            logger.info(f"Controller: Successfully deleted bookmark with ID: {bookmark_id}")
            return {"message": "Bookmark deleted successfully"}
        except HTTPException as e:
            logger.error(f"Controller: Error deleting bookmark {bookmark_id} - {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Controller: Unexpected error deleting bookmark {bookmark_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    async def delete_bookmark_by_user_and_cafe(self, user_id: str, cafe_id: str) -> dict:
        """Delete a bookmark by user ID and cafe ID"""
        logger.info(f"Controller: Received request to delete bookmark for user {user_id} and cafe {cafe_id}")
        try:
            success = await self.service.delete_bookmark_by_user_and_cafe(user_id, cafe_id)
            if not success:
                logger.warning(f"Controller: Failed to delete bookmark for user {user_id} and cafe {cafe_id}")
                raise HTTPException(status_code=500, detail="Failed to delete bookmark")
            logger.info(f"Controller: Successfully deleted bookmark for user {user_id} and cafe {cafe_id}")
            return {"message": "Bookmark deleted successfully"}
        except HTTPException as e:
            logger.error(f"Controller: Error deleting bookmark for user {user_id} and cafe {cafe_id} - {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Controller: Unexpected error deleting bookmark for user {user_id} and cafe {cafe_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    async def check_bookmark_exists(self, user_id: str, cafe_id: str) -> dict:
        """Check if a bookmark exists for a user and cafe"""
        logger.info(f"Controller: Received request to check if bookmark exists for user {user_id} and cafe {cafe_id}")
        try:
            exists = await self.service.check_bookmark_exists(user_id, cafe_id)
            return {"exists": exists}
        except Exception as e:
            logger.error(f"Controller: Unexpected error checking bookmark existence: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred.") 