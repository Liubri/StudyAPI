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
    async def connect_db(cls, test_mode: bool = False):
        print("Connecting to MongoDB...")
        MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
        print(MONGODB_PASSWORD)
        MONGODB_URL = f"mongodb+srv://dev:{MONGODB_PASSWORD}@dev.wukiztm.mongodb.net/?retryWrites=true&w=majority&appName=dev"
        cls.client = AsyncIOMotorClient(MONGODB_URL)
        
        if test_mode:
            cls.db = cls.client.studyapi_test
        else:
            cls.db = cls.client.studyapi
        # validate the database connection
        try:
            await cls.client.admin.command('ping')
            # Create geospatial index for cafes
            await cls.db.cafes.create_index([("location", "2dsphere")])
        except Exception as e:
            print("Fatal error - Could not connect to MongoDB")
            print(f"Connection error details: {str(e)}")
            raise Exception(f"Database connection failed: {str(e)}")

        print("Connected to MongoDB")

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_db(cls):
        return cls.db 