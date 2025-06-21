from fastapi import APIRouter, Query, File, UploadFile, status
from typing import List
from app.models.user import UserCreate, UserUpdate, UserResponse, UserLogin, LoginResponse
from app.controllers.user_controller import UserController

router = APIRouter()
user_controller = UserController()

@router.post(
    "/users/", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with username, cafes visited count, average rating, and password.",
    response_description="The created user object (password excluded)."
)
async def create_user(user: UserCreate):
    """
    Create a new user.
    
    - **name**: Unique username (required)
    - **cafes_visited**: Number of cafes visited (default: 0)
    - **average_rating**: User's average rating (default: 0.0)
    - **password**: Plain text password (required)
    """
    return await user_controller.create_user(user)

@router.get(
    "/users/", 
    response_model=List[UserResponse],
    summary="Get all users",
    description="Retrieve a list of all users with pagination support.",
    response_description="A list of user objects (passwords excluded)."
)
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return")
):
    """
    Get all users with pagination.
    
    - **skip**: Number of users to skip (default: 0)
    - **limit**: Maximum number of users to return (default: 100, max: 1000)
    """
    return await user_controller.get_all_users(skip, limit)

@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get a specific user by ID",
    description="Retrieve a specific user by their unique MongoDB ObjectId.",
    responses={
        200: {
            "description": "User retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "60d5ec49e9af8b2c24e8a1b2",
                        "name": "Alice Coffee",
                        "cafes_visited": 5,
                        "average_rating": 4.2,
                        "profile_picture": "user_60d5ec49e9af8b2c24e8a1b2_profile.jpg",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        404: {"description": "User not found"}
    }
)
async def get_user(user_id: str):
    """
    Retrieve a specific user by their unique ID.
    
    - **user_id**: The unique identifier of the user (MongoDB ObjectId as string)
    """
    return await user_controller.get_user(user_id)

@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
    description="Update user information. Allows partial updates - only provided fields will be updated.",
    response_description="The updated user object.",
    responses={
        200: {"description": "User updated successfully"},
        400: {"description": "Validation error (e.g., duplicate username)"},
        404: {"description": "User not found"}
    }
)
async def update_user(user_id: str, user: UserUpdate):
    """
    Update a user's information.
    
    - **user_id**: The unique identifier of the user
    - **user**: The fields to update (any subset of the User model)
    """
    return await user_controller.update_user(user_id, user)

@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
    description="Delete a user by their unique ID. This action also removes their profile picture if it exists.",
    response_description="Confirmation message of successful deletion.",
    responses={
        200: {
            "description": "User deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "User deleted successfully"}
                }
            }
        },
        404: {"description": "User not found"}
    }
)
async def delete_user(user_id: str):
    """
    Delete a user by their unique ID.
    
    - **user_id**: The unique identifier of the user
    
    This will also delete the user's profile picture if it exists.
    """
    return await user_controller.delete_user(user_id)

@router.post(
    "/users/{user_id}/profile-picture",
    summary="Upload profile picture",
    description="Upload a profile picture for a specific user. Replaces existing profile picture if one exists.",
    response_description="Confirmation of successful upload with filename.",
    responses={
        200: {
            "description": "Profile picture uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Profile picture uploaded successfully",
                        "filename": "user_60d5ec49e9af8b2c24e8a1b2_profile.jpg"
                    }
                }
            }
        },
        400: {"description": "Invalid file type"},
        404: {"description": "User not found"}
    }
)
async def upload_profile_picture(user_id: str, file: UploadFile = File(...)):
    """
    Upload a profile picture for a user.
    
    - **user_id**: The unique identifier of the user
    - **file**: Image file to upload (JPEG, PNG, GIF, etc.)
    
    The file will be saved with a unique name and the user record will be updated.
    """
    return await user_controller.upload_profile_picture(user_id, file)

@router.get(
    "/users/search/",
    response_model=List[UserResponse],
    summary="Search users",
    description="Search for users by username using a text query (case-insensitive)."
)
async def search_users(
    query: str = Query(..., description="Text to search in usernames")
):
    """
    Search for users by username.
    
    - **query**: Text to search in usernames (case-insensitive)
    """
    return await user_controller.search_users(query)

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate a user with username and password (plain text).",
    response_description="Login success response with user information.",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Login successful",
                        "user_id": "60d5ec49e9af8b2c24e8a1b2",
                        "user_name": "Alice Coffee"
                    }
                }
            }
        },
        401: {"description": "Invalid username or password"}
    }
)
async def login(login_data: UserLogin):
    """
    Authenticate a user login.
    
    - **name**: Username
    - **password**: Plain text password
    
    Returns user information if authentication is successful.
    """
    return await user_controller.login(login_data) 