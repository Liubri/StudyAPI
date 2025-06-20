from typing import List, Optional
from fastapi import HTTPException
from app.models.cafe import Cafe, CafeCreate, CafeUpdate
from app.repositories.cafe_repository import CafeRepository
from app.config.logging_config import logger

class CafeService:
    def __init__(self):
        self.repository = CafeRepository()

    def _validate_coordinates(self, coordinates: List[float]) -> bool:
        """
        Validate that coordinates are within valid ranges
        longitude: -180 to 180
        latitude: -90 to 90
        """
        if len(coordinates) != 2:
            return False
        longitude, latitude = coordinates
        return -180 <= longitude <= 180 and -90 <= latitude <= 90

    async def create_cafe(self, cafe_data: CafeCreate) -> Cafe:
        logger.info(f"Service: Creating new cafe: {cafe_data.name}")
        if not self._validate_coordinates(cafe_data.location.coordinates):
            logger.error("Invalid coordinates provided for new cafe")
            raise HTTPException(status_code=400, detail="Invalid coordinates provided")
        
        try:
            created_cafe = await self.repository.create_cafe(cafe_data)
            logger.info(f"Service: Successfully created cafe with ID: {created_cafe.id}")
            return created_cafe
        except Exception as e:
            logger.error(f"Service: Failed to create cafe: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create cafe: {str(e)}")

    async def get_cafe(self, cafe_id: str) -> Optional[Cafe]:
        logger.info(f"Service: Fetching cafe with ID: {cafe_id}")
        cafe = await self.repository.get_cafe(cafe_id)
        if not cafe:
            logger.warning(f"Service: Cafe not found with ID: {cafe_id}")
            return None
        return cafe

    async def get_all_cafes(self) -> List[Cafe]:
        logger.info("Service: Fetching all cafes")
        return await self.repository.get_all_cafes()

    async def update_cafe(self, cafe_id: str, cafe_data: CafeUpdate) -> Optional[Cafe]:
        logger.info(f"Service: Updating cafe with ID: {cafe_id}")
        existing_cafe = await self.get_cafe(cafe_id)
        if not existing_cafe:
            return None

        if cafe_data.location and not self._validate_coordinates(cafe_data.location.coordinates):
            logger.error(f"Invalid coordinates for cafe update: {cafe_id}")
            raise HTTPException(status_code=400, detail="Invalid coordinates provided")
        
        update_data = cafe_data.model_dump(exclude_unset=True)
        
        updated_cafe = await self.repository.update_cafe(cafe_id, update_data)
        if not updated_cafe:
             logger.warning(f"Service: Failed to update cafe with ID: {cafe_id}")
             return None
        
        logger.info(f"Service: Successfully updated cafe with ID: {cafe_id}")
        return updated_cafe

    async def delete_cafe(self, cafe_id: str) -> bool:
        logger.info(f"Service: Deleting cafe with ID: {cafe_id}")
        return await self.repository.delete_cafe(cafe_id)

    async def search_cafes(self, query: str) -> List[Cafe]:
        logger.info(f"Service: Searching cafes with query: {query}")
        if not query.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        return await self.repository.search_cafes(query)

    async def find_nearby_cafes(self, longitude: float, latitude: float, max_distance: float) -> List[Cafe]:
        logger.info(f"Service: Finding cafes near [{longitude}, {latitude}] within {max_distance}m")
        if not self._validate_coordinates([longitude, latitude]):
            raise HTTPException(status_code=400, detail="Invalid coordinates provided")
        if max_distance <= 0:
            raise HTTPException(status_code=400, detail="Max distance must be greater than 0")
        return await self.repository.find_nearby_cafes(longitude, latitude, max_distance)

    async def find_cafes_by_amenities(self, amenities: List[str]) -> List[Cafe]:
        logger.info(f"Service: Finding cafes with amenities: {amenities}")
        if not amenities:
            raise HTTPException(status_code=400, detail="At least one amenity must be specified")
        return await self.repository.find_cafes_by_amenities(amenities)

    async def find_cafes_by_rating(self, min_rating: float) -> List[Cafe]:
        logger.info(f"Service: Finding cafes with min rating: {min_rating}")
        if not 1 <= min_rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        return await self.repository.find_cafes_by_rating(min_rating) 