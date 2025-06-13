from typing import List
from fastapi import HTTPException
from app.models.cafe import Cafe, CafeCreate, CafeUpdate, AccessLevel
from app.services.cafe_service import CafeService
from app.config.logging_config import logger

class CafeController:
    def __init__(self):
        self.service = CafeService()

    async def create_cafe(self, cafe_data: CafeCreate) -> Cafe:
        try:
            logger.info(f"Creating new cafe: {cafe_data.name}")
            # Validate location coordinates
            if not self._validate_coordinates(cafe_data.location.coordinates):
                raise ValueError("Invalid coordinates provided")
            
            cafe = await self.service.create_cafe(cafe_data)
            logger.info(f"Successfully created cafe with ID: {cafe.id}")
            return cafe
        except Exception as e:
            logger.error(f"Failed to create cafe: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create cafe: {str(e)}")

    async def get_cafe(self, cafe_id: str) -> Cafe:
        logger.info(f"Fetching cafe with ID: {cafe_id}")
        cafe = await self.service.get_cafe(cafe_id)
        if not cafe:
            logger.warning(f"Cafe not found with ID: {cafe_id}")
            raise HTTPException(status_code=404, detail="Cafe not found")
        return cafe

    async def get_all_cafes(self) -> List[Cafe]:
        logger.info("Fetching all cafes")
        return await self.service.get_all_cafes()

    async def update_cafe(self, cafe_id: str, cafe_data: CafeUpdate) -> Cafe:
        logger.info(f"Updating cafe with ID: {cafe_id}")
        
        # Validate the cafe exists
        existing_cafe = await self.service.get_cafe(cafe_id)
        if not existing_cafe:
            logger.warning(f"Cafe not found with ID: {cafe_id}")
            raise HTTPException(status_code=404, detail="Cafe not found")

        # Validate coordinates if location is being updated
        if cafe_data.location and not self._validate_coordinates(cafe_data.location.coordinates):
            raise HTTPException(status_code=400, detail="Invalid coordinates provided")

        updated_cafe = await self.service.update_cafe(cafe_id, cafe_data)
        if not updated_cafe:
            logger.warning(f"Failed to update cafe with ID: {cafe_id}")
            raise HTTPException(status_code=500, detail="Failed to update cafe")
        
        logger.info(f"Successfully updated cafe with ID: {cafe_id}")
        return updated_cafe

    async def delete_cafe(self, cafe_id: str) -> bool:
        logger.info(f"Deleting cafe with ID: {cafe_id}")
        success = await self.service.delete_cafe(cafe_id)
        if not success:
            logger.warning(f"Cafe not found with ID: {cafe_id}")
            raise HTTPException(status_code=404, detail="Cafe not found")
        logger.info(f"Successfully deleted cafe with ID: {cafe_id}")
        return success

    async def search_cafes(self, query: str) -> List[Cafe]:
        logger.info(f"Searching cafes with query: {query}")
        if not query.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        return await self.service.search_cafes(query)

    async def find_nearby_cafes(self, longitude: float, latitude: float, max_distance: float) -> List[Cafe]:
        logger.info(f"Finding cafes near coordinates: [{longitude}, {latitude}] within {max_distance}m")
        if not self._validate_coordinates([longitude, latitude]):
            raise HTTPException(status_code=400, detail="Invalid coordinates provided")
        if max_distance <= 0:
            raise HTTPException(status_code=400, detail="Max distance must be greater than 0")
        return await self.service.find_nearby_cafes(longitude, latitude, max_distance)

    async def find_cafes_by_amenities(self, amenities: List[str]) -> List[Cafe]:
        logger.info(f"Finding cafes with amenities: {amenities}")
        if not amenities:
            raise HTTPException(status_code=400, detail="At least one amenity must be specified")
        return await self.service.find_cafes_by_amenities(amenities)

    async def find_cafes_by_rating(self, min_rating: float) -> List[Cafe]:
        logger.info(f"Finding cafes with minimum rating: {min_rating}")
        if not 1 <= min_rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        return await self.service.find_cafes_by_rating(min_rating)

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