from fastapi import APIRouter, Query, status
from typing import List
from app.models.cafe import Cafe, CafeCreate, CafeUpdate, AccessLevel
from app.controllers.cafe_controller import CafeController

router = APIRouter()
cafe_controller = CafeController()

@router.post(
    "/cafes/", 
    response_model=Cafe,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafe",
    description="Create a new cafe with details such as name, address, location, and amenities.",
    response_description="The created cafe object."
)
async def create_cafe(cafe: CafeCreate):
    return await cafe_controller.create_cafe(cafe)

@router.get(
    "/cafes/", 
    response_model=List[Cafe],
    summary="Get all cafes",
    description="Retrieve a list of all cafes in the database.",
    response_description="A list of cafe objects."
)
async def get_all_cafes():
    return await cafe_controller.get_all_cafes()

@router.get(
    "/cafes/{cafe_id}",
    response_model=Cafe,
    summary="Retrieve a specific cafe by its unique ID",
    description="Retrieve a specific cafe by its unique ID",
    responses={
        200: {
            "description": "Cafe retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Cafe Name",
                        "location": {
                            "type": "Point",
                            "coordinates": [-122.4194, 37.7749]
                        }
                    }
                }
            }
        },
        404: {"description": "Cafe not found"}
    }
)
async def get_cafe(
    cafe_id: str
):
    """
    Retrieve a specific cafe by its unique ID.

    - **cafe_id**: The unique identifier of the cafe (MongoDB ObjectId as a string)
    """
    return await cafe_controller.get_cafe(cafe_id)

@router.put(
    "/cafes/{cafe_id}",
    response_model=Cafe,
    summary="Update a cafe",
    description="Update the details of a specific cafe by its ID. Allows for partial updates.",
    response_description="The updated cafe object.",
    responses={
        200: {"description": "Cafe updated successfully"},
        404: {"description": "Cafe not found"}
    }
)
async def update_cafe(
    cafe_id: str,
    cafe: CafeUpdate
):
    """
    Update a cafe's information.

    - **cafe_id**: The unique identifier of the cafe
    - **cafe**: The fields to update (any subset of the Cafe model)
    """
    return await cafe_controller.update_cafe(cafe_id, cafe)

@router.delete(
    "/cafes/{cafe_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a cafe",
    description="Delete a cafe by its unique ID. This action is irreversible.",
    response_description="Confirmation message of successful deletion.",
    responses={
        200: {
            "description": "Cafe deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Cafe deleted successfully"}
                }
            }
        },
        404: {"description": "Cafe not found"}
    }
)
async def delete_cafe(
    cafe_id: str
):
    """
    Delete a cafe by its unique ID.

    - **cafe_id**: The unique identifier of the cafe
    """
    await cafe_controller.delete_cafe(cafe_id)
    return {"message": "Cafe deleted successfully"}

@router.get(
    "/cafes/search/",
    response_model=List[Cafe],
    summary="Search cafes",
    description="Search for cafes by name, city, or street using a text query."
)
async def search_cafes(
    query: str = Query(..., description="Text to search in cafe name, city, or street")
):
    """
    Search for cafes by a text query.

    - **query**: Text to search in cafe name, city, or street
    """
    return await cafe_controller.search_cafes(query)

@router.get(
    "/cafes/nearby/",
    response_model=List[Cafe],
    summary="Find nearby cafes",
    description="Find cafes within a certain distance of a geographic point"
)
async def find_nearby_cafes(
    longitude: float = Query(..., description="Longitude coordinate"),
    latitude: float = Query(..., description="Latitude coordinate"),
    max_distance: float = Query(5000, description="Maximum distance in meters")
):
    """
    Find cafes near a given geographic location.

    - **longitude**: Longitude of the point
    - **latitude**: Latitude of the point
    - **max_distance**: Maximum distance in meters (default 5000)
    """
    return await cafe_controller.find_nearby_cafes(longitude, latitude, max_distance)

@router.get(
    "/cafes/by-amenities/",
    response_model=List[Cafe],
    summary="Find cafes by amenities",
    description="Find cafes that have all of the specified amenities"
)
async def find_cafes_by_amenities(
    amenities: List[str] = Query(..., description="List of amenities to search for")
):
    """
    Find cafes that have all specified amenities.

    - **amenities**: List of amenities (e.g., wifi, power_outlets)
    """
    return await cafe_controller.find_cafes_by_amenities(amenities)

@router.get(
    "/cafes/by-rating/",
    response_model=List[Cafe],
    summary="Find cafes by minimum rating",
    description="Find cafes with an average rating greater than or equal to the specified value"
)
async def find_cafes_by_rating(
    min_rating: float = Query(..., ge=1, le=5, description="Minimum rating (1-5)")
):
    """
    Find cafes with an average rating greater than or equal to the specified value.

    - **min_rating**: Minimum average rating (1-5)
    """
    return await cafe_controller.find_cafes_by_rating(min_rating) 