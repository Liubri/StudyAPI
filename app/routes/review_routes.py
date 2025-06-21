from fastapi import APIRouter, Path, HTTPException, status, UploadFile, File
from typing import List
from app.models.review import Review, ReviewCreate, ReviewUpdate, PhotoCreate
from app.controllers.review_controller import ReviewController
from app.services.s3_service import S3Service

router = APIRouter()
review_controller = ReviewController()
s3_service = S3Service()

@router.post(
    "/reviews/",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new review",
    description="""
    Create a new review for a study spot.
    
    This endpoint allows users to submit reviews for study spots with ratings for:
    - Overall experience (0-5 scale)
    - Outlet accessibility (0-5 scale)
    - WiFi quality (0-5 scale)
    - Optional text descriptions for atmosphere, energy level, and study-friendliness
    """,
    response_description="The created review object with all details",
    responses={
        201: {
            "description": "Review created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "60d5ec49e9af8b2c24e8a1b2",
                        "study_spot_id": "cafe123",
                        "user_id": "user456",
                        "overall_rating": 4.5,
                        "outlet_accessibility": 4.0,
                        "wifi_quality": 5.0,
                        "atmosphere": "Quiet and peaceful",
                        "energy_level": "Calm",
                        "study_friendly": "Very study-friendly",
                        "photos": [],
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Rating must be between 0 and 5"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to create review"
                    }
                }
            }
        }
    }
)
async def create_review(review: ReviewCreate):
    """
    Create a new review for a study spot.

    - **study_spot_id**: The ID of the study spot being reviewed
    - **user_id**: The ID of the user submitting the review
    - **overall_rating**: Overall rating (0-5)
    - **outlet_accessibility**: Outlet accessibility rating
    - **wifi_quality**: Wifi quality rating
    - **atmosphere**: Optional atmosphere description
    - **energy_level**: Optional energy level description
    - **study_friendly**: Optional study-friendly description
    """
    return await review_controller.create_review(review)

@router.get(
    "/reviews/{review_id}",
    response_model=Review,
    summary="Get a review by ID",
    description="Retrieve a single review by its unique ID, providing detailed information about the review, including ratings and user comments.",
    response_description="The review object with all details",
    responses={
        200: {
            "description": "Review found and returned successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "60d5ec49e9af8b2c24e8a1b2",
                        "study_spot_id": "cafe123",
                        "user_id": "user456",
                        "overall_rating": 4.5,
                        "outlet_accessibility": 4.0,
                        "wifi_quality": 5.0,
                        "atmosphere": "Quiet and peaceful",
                        "energy_level": "Calm",
                        "study_friendly": "Very study-friendly",
                        "photos": [],
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Review not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Review not found"}
                }
            }
        }
    }
)
async def get_review(
    review_id: str = Path(..., description="The unique ID of the review to retrieve")
):
    """
    Get a review by its unique ID.

    - **review_id**: The unique identifier of the review
    """
    return await review_controller.get_review(review_id)

@router.get(
    "/reviews/by-spot/{study_spot_id}",
    response_model=List[Review],
    summary="Get reviews for a study spot",
    description="Retrieve all reviews for a specific study spot, identified by its ID. This is useful for displaying all user feedback for a particular location.",
    response_description="A list of review objects for the specified study spot",
    responses={
        200: {
            "description": "Successfully retrieved list of reviews for the study spot"
        },
        404: {
            "description": "Study spot not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Study spot not found"}
                }
            }
        }
    }
)
async def get_reviews_by_study_spot(
    study_spot_id: str = Path(..., description="The unique ID of the study spot to get reviews for")
):
    """
    Get all reviews for a specific study spot.

    - **study_spot_id**: The unique identifier of the study spot
    """
    return await review_controller.get_reviews_by_study_spot(study_spot_id)

@router.put(
    "/reviews/{review_id}",
    response_model=Review,
    summary="Update a review",
    description="Update an existing review by its ID. This allows for partial updates, so you only need to provide the fields you want to change.",
    response_description="The updated review object",
    responses={
        200: {
            "description": "Review updated successfully"
        },
        404: {
            "description": "Review not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Review not found"}
                }
            }
        },
        500: {
            "description": "Failed to update review"
        }
    }
)
async def update_review(
    review_data: ReviewUpdate,
    review_id: str = Path(..., description="The unique ID of the review to update")
):
    """
    Update a review by its unique ID.

    - **review_id**: The unique identifier of the review
    - **review_data**: The fields to update
    """
    return await review_controller.update_review(review_id, review_data)

@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a review",
    description="Delete a review by its unique ID. This action is irreversible.",
    response_description="Confirmation message of successful deletion",
    responses={
        200: {
            "description": "Review deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Review deleted successfully"}
                }
            }
        },
        404: {
            "description": "Review not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Review not found"}
                }
            }
        },
        500: {
            "description": "Failed to delete review"
        }
    }
)
async def delete_review(
    review_id: str = Path(..., description="The unique ID of the review to delete")
):
    """
    Delete a review by its unique ID.

    - **review_id**: The unique identifier of the review
    """
    await review_controller.delete_review(review_id)
    return {"message": "Review deleted successfully"}

@router.post(
    "/reviews/{review_id}/photos",
    response_model=Review,
    summary="Add a photo to a review",
    description="Attach a new photo to a specific review. The photo details (URL and caption) should be provided in the request body.",
    response_description="The review object, updated with the new photo",
    responses={
        200: {
            "description": "Photo added successfully"
        },
        404: {
            "description": "Review not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Review not found"}
                }
            }
        },
        500: {
            "description": "Failed to add photo"
        }
    }
)
async def add_photo(
    photo: PhotoCreate,
    review_id: str = Path(..., description="The unique ID of the review to add a photo to")
):
    """
    Add a photo to a review.

    - **review_id**: The unique identifier of the review
    - **photo**: The photo object to add
    """
    return await review_controller.add_photo(review_id, photo)

@router.post(
    "/reviews/{review_id}/upload-photo",
    response_model=Review,
    summary="Upload and add a photo to a review",
    description="Upload a photo file directly to DigitalOcean Spaces and attach it to a specific review.",
    response_description="The review object, updated with the new photo",
    responses={
        200: {
            "description": "Photo uploaded and added successfully"
        },
        400: {
            "description": "Invalid file or review not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid file type"}
                }
            }
        },
        404: {
            "description": "Review not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Review not found"}
                }
            }
        },
        500: {
            "description": "Failed to upload photo or add to review"
        }
    }
)
async def upload_photo_to_review(
    file: UploadFile = File(...),
    review_id: str = Path(..., description="The unique ID of the review to add a photo to"),
    caption: str = ""
):
    """
    Upload a photo file and add it to a review.

    - **review_id**: The unique identifier of the review
    - **file**: The photo file to upload (multipart/form-data)
    - **caption**: Optional caption for the photo
    """
    try:
        # Upload file to S3
        file_url = await s3_service.upload_file(file, folder="review-photos")
        
        # Create photo object
        photo = PhotoCreate(
            url=file_url,
            caption=caption or f"Photo for review {review_id}"
        )
        
        # Add photo to review
        return await review_controller.add_photo(review_id, photo)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload photo: {str(e)}"
        ) 