from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_db(cls):
        MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
        MONGODB_URL = f"mongodb+srv://mad:{MONGODB_PASSWORD}@dev.kcr8fhi.mongodb.net/?retryWrites=true&w=majority&appName=dev"
        cls.client = AsyncIOMotorClient(MONGODB_URL)
        cls.db = cls.client.studyapi

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_db(cls):
        return cls.db 