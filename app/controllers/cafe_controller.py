from typing import List
from fastapi import HTTPException
from app.models.cafe import Cafe, CafeCreate, CafeUpdate
from app.services.cafe_service import CafeService
from app.config.logging_config import logger

class CafeController:
    def __init__(self):
        self.service = CafeService()

    async def create_cafe(self, cafe_data: CafeCreate) -> Cafe:
        try:
            logger.info(f"Controller: Received request to create cafe: {cafe_data.name}")
            cafe = await self.service.create_cafe(cafe_data)
            return cafe
        except HTTPException as e:
            logger.error(f"Controller: Error creating cafe - {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Controller: Unexpected error creating cafe: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    async def get_cafe(self, cafe_id: str) -> Cafe:
        logger.info(f"Controller: Received request to get cafe with ID: {cafe_id}")
        cafe = await self.service.get_cafe(cafe_id)
        if not cafe:
            logger.warning(f"Controller: Cafe not found with ID: {cafe_id}")
            raise HTTPException(status_code=404, detail="Cafe not found")
        return cafe

    async def get_all_cafes(self) -> List[Cafe]:
        logger.info("Controller: Received request to get all cafes")
        return await self.service.get_all_cafes()

    async def update_cafe(self, cafe_id: str, cafe_data: CafeUpdate) -> Cafe:
        logger.info(f"Controller: Received request to update cafe with ID: {cafe_id}")
        try:
            updated_cafe = await self.service.update_cafe(cafe_id, cafe_data)
            if not updated_cafe:
                logger.warning(f"Controller: Cafe not found for update with ID: {cafe_id}")
                raise HTTPException(status_code=404, detail="Cafe not found")
            return updated_cafe
        except HTTPException as e:
            logger.error(f"Controller: Error updating cafe - {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Controller: Unexpected error updating cafe: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    async def delete_cafe(self, cafe_id: str):
        logger.info(f"Controller: Received request to delete cafe with ID: {cafe_id}")
        success = await self.service.delete_cafe(cafe_id)
        if not success:
            logger.warning(f"Controller: Cafe not found for deletion with ID: {cafe_id}")
            raise HTTPException(status_code=404, detail="Cafe not found")
        return {"message": "Cafe deleted successfully"}

    async def search_cafes(self, query: str) -> List[Cafe]:
        logger.info(f"Controller: Received request to search cafes with query: '{query}'")
        return await self.service.search_cafes(query)

    async def find_nearby_cafes(self, longitude: float, latitude: float, max_distance: float) -> List[Cafe]:
        logger.info(f"Controller: Received request to find nearby cafes.")
        return await self.service.find_nearby_cafes(longitude, latitude, max_distance)

    async def find_cafes_by_amenities(self, amenities: List[str]) -> List[Cafe]:
        logger.info(f"Controller: Received request to find cafes by amenities: {amenities}")
        return await self.service.find_cafes_by_amenities(amenities)

    async def find_cafes_by_rating(self, min_rating: float) -> List[Cafe]:
        logger.info(f"Controller: Received request to find cafes by rating: >{min_rating}")
        return await self.service.find_cafes_by_rating(min_rating) 