from fastapi import APIRouter, Path, status
from typing import List
from app.models.bookmark import Bookmark, BookmarkCreate, BookmarkWithCafe
from app.controllers.bookmark_controller import BookmarkController

router = APIRouter()
bookmark_controller = BookmarkController()

@router.post(
    "/bookmarks/",
    response_model=Bookmark,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bookmark",
    description="Create a new bookmark for a user and cafe. The bookmark will be timestamped automatically.",
    response_description="The created bookmark object with all details",
    responses={
        201: {
            "description": "Bookmark created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "60d5ec49e9af8b2c24e8a1b4",
                        "user_id": "60d5ec49e9af8b2c24e8a1b2",
                        "cafe_id": "60d5ec49e9af8b2c24e8a1b3",
                        "bookmarked_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        404: {
            "description": "User or cafe not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        409: {
            "description": "Bookmark already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Bookmark already exists"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to create bookmark"}
                }
            }
        }
    }
)
async def create_bookmark(bookmark: BookmarkCreate):
    """
    Create a new bookmark.

    - **user_id**: The unique identifier of the user creating the bookmark
    - **cafe_id**: The unique identifier of the cafe being bookmarked
    
    The bookmark will be automatically timestamped with the current date and time.
    """
    return await bookmark_controller.create_bookmark(bookmark)

@router.get(
    "/bookmarks/{bookmark_id}",
    response_model=Bookmark,
    summary="Get a bookmark by ID",
    description="Retrieve a specific bookmark by its unique ID",
    response_description="The bookmark object",
    responses={
        200: {
            "description": "Bookmark retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "60d5ec49e9af8b2c24e8a1b4",
                        "user_id": "60d5ec49e9af8b2c24e8a1b2",
                        "cafe_id": "60d5ec49e9af8b2c24e8a1b3",
                        "bookmarked_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        404: {"description": "Bookmark not found"}
    }
)
async def get_bookmark(
    bookmark_id: str = Path(..., description="The unique identifier of the bookmark")
):
    """
    Get a bookmark by its unique ID.

    - **bookmark_id**: The unique identifier of the bookmark
    """
    return await bookmark_controller.get_bookmark(bookmark_id)

@router.get(
    "/users/{user_id}/bookmarks",
    response_model=List[BookmarkWithCafe],
    summary="Get all bookmarks for a user",
    description="Retrieve all bookmarks for a specific user, ordered by bookmark time (newest first), with cafe information included",
    response_description="A list of bookmarks with cafe details",
    responses={
        200: {
            "description": "Bookmarks retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "60d5ec49e9af8b2c24e8a1b4",
                            "user_id": "60d5ec49e9af8b2c24e8a1b2",
                            "cafe_id": "60d5ec49e9af8b2c24e8a1b3",
                            "bookmarked_at": "2024-01-15T10:30:00Z",
                            "cafe": {
                                "id": "60d5ec49e9af8b2c24e8a1b3",
                                "name": "The Coffee Corner",
                                "address": {
                                    "street": "123 Main St",
                                    "city": "San Francisco",
                                    "state": "CA"
                                },
                                "average_rating": 4
                            }
                        }
                    ]
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
async def get_user_bookmarks(
    user_id: str = Path(..., description="The unique identifier of the user")
):
    """
    Get all bookmarks for a specific user.

    - **user_id**: The unique identifier of the user
    
    Returns bookmarks ordered by bookmark time (newest first) with full cafe information.
    """
    return await bookmark_controller.get_bookmarks_by_user(user_id)

@router.delete(
    "/bookmarks/{bookmark_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a bookmark",
    description="Delete a bookmark by its unique ID. This action is irreversible.",
    response_description="Confirmation message of successful deletion",
    responses={
        200: {
            "description": "Bookmark deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Bookmark deleted successfully"}
                }
            }
        },
        404: {"description": "Bookmark not found"}
    }
)
async def delete_bookmark(
    bookmark_id: str = Path(..., description="The unique identifier of the bookmark")
):
    """
    Delete a bookmark by its unique ID.

    - **bookmark_id**: The unique identifier of the bookmark
    """
    return await bookmark_controller.delete_bookmark(bookmark_id)

@router.delete(
    "/users/{user_id}/bookmarks/{cafe_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a bookmark by user and cafe",
    description="Delete a bookmark for a specific user and cafe. This action is irreversible.",
    response_description="Confirmation message of successful deletion",
    responses={
        200: {
            "description": "Bookmark deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Bookmark deleted successfully"}
                }
            }
        },
        404: {"description": "Bookmark not found"}
    }
)
async def delete_user_cafe_bookmark(
    user_id: str = Path(..., description="The unique identifier of the user"),
    cafe_id: str = Path(..., description="The unique identifier of the cafe")
):
    """
    Delete a bookmark for a specific user and cafe.

    - **user_id**: The unique identifier of the user
    - **cafe_id**: The unique identifier of the cafe
    """
    return await bookmark_controller.delete_bookmark_by_user_and_cafe(user_id, cafe_id)

@router.get(
    "/users/{user_id}/bookmarks/{cafe_id}/exists",
    summary="Check if bookmark exists",
    description="Check if a bookmark exists for a specific user and cafe",
    response_description="Boolean indicating if the bookmark exists",
    responses={
        200: {
            "description": "Check completed successfully",
            "content": {
                "application/json": {
                    "example": {"exists": True}
                }
            }
        }
    }
)
async def check_bookmark_exists(
    user_id: str = Path(..., description="The unique identifier of the user"),
    cafe_id: str = Path(..., description="The unique identifier of the cafe")
):
    """
    Check if a bookmark exists for a specific user and cafe.

    - **user_id**: The unique identifier of the user
    - **cafe_id**: The unique identifier of the cafe
    
    Returns a boolean indicating whether the bookmark exists.
    """
    return await bookmark_controller.check_bookmark_exists(user_id, cafe_id) 