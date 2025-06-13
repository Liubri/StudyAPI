from fastapi import APIRouter, Path
from typing import List
from app.models.review import Review, ReviewCreate, ReviewUpdate, PhotoCreate
from app.controllers.review_controller import ReviewController

router = APIRouter()
review_controller = ReviewController()

@router.post(
    "/reviews/",
    response_model=Review,
    summary="Create a new review",
    description="Create a new review for a study spot.",
    response_description="The created review object",
    responses={
        201: {"description": "Review created successfully"},
        400: {"description": "Invalid input"},
        500: {"description": "Failed to create review"}
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
    description="Retrieve a review by its unique ID.",
    responses={
        200: {"description": "Review found"},
        404: {"description": "Review not found"}
    }
)
async def get_review(
    review_id: str = Path(..., description="The unique ID of the review")
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
    description="Retrieve all reviews for a specific study spot.",
    responses={
        200: {"description": "List of reviews for the study spot"}
    }
)
async def get_reviews_by_study_spot(
    study_spot_id: str = Path(..., description="The unique ID of the study spot")
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
    description="Update an existing review by its ID.",
    responses={
        200: {"description": "Review updated successfully"},
        404: {"description": "Review not found"},
        500: {"description": "Failed to update review"}
    }
)
async def update_review(
    review_id: str = Path(..., description="The unique ID of the review"),
    review_data: ReviewUpdate = ...
):
    """
    Update a review by its unique ID.

    - **review_id**: The unique identifier of the review
    - **review_data**: The fields to update
    """
    return await review_controller.update_review(review_id, review_data)

@router.delete(
    "/reviews/{review_id}",
    summary="Delete a review",
    description="Delete a review by its unique ID.",
    responses={
        200: {"description": "Review deleted successfully"},
        404: {"description": "Review not found"},
        500: {"description": "Failed to delete review"}
    }
)
async def delete_review(
    review_id: str = Path(..., description="The unique ID of the review")
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
    description="Attach a photo to a specific review.",
    responses={
        200: {"description": "Photo added successfully"},
        404: {"description": "Review not found"},
        500: {"description": "Failed to add photo"}
    }
)
async def add_photo(
    review_id: str = Path(..., description="The unique ID of the review"),
    photo: PhotoCreate = ...
):
    """
    Add a photo to a review.

    - **review_id**: The unique identifier of the review
    - **photo**: The photo object to add
    """
    return await review_controller.add_photo(review_id, photo) 