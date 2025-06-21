from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routes import review_routes
from app.routes import cafe_routes
from app.routes import file_routes
from app.routes import user_routes
from app.config.database import Database
from app.config.logging_config import logger
import time
import os

app = FastAPI(
    title="Study Spot Reviews API",
    description="""
    A comprehensive API for managing study spots, cafes, user reviews, and user management.
    
    ## Features
    
    * **User Management**: Create, read, update, and delete users with simple authentication
    * **Cafe Management**: Create, read, update, and delete cafe information
    * **Review System**: Submit and manage reviews for study spots
    * **Photo Uploads**: Attach photos to reviews and upload profile pictures
    * **Search & Discovery**: Find cafes by location, amenities, and ratings
    * **Geospatial Queries**: Find nearby cafes based on coordinates
    * **File Management**: Upload, delete, and manage files in cloud storage
    * **Simple Login**: Plain text authentication system for users
    
    ## Getting Started
    
    1. Use the `/api/v1/users/` endpoints to manage user accounts and authentication
    2. Use the `/api/v1/cafes/` endpoints to manage cafe information
    3. Use the `/api/v1/reviews/` endpoints to manage reviews
    4. Use the `/api/v1/files/` endpoints to upload and manage files
    5. All endpoints return JSON responses
    
    ## User System
    
    The user system includes:
    - **User CRUD Operations**: Create, read, update, and delete users
    - **Simple Login**: Plain text password authentication
    - **Profile Pictures**: Upload and manage user profile pictures
    - **User Statistics**: Track cafes visited and average ratings
    """,
    version="1.0.0",
    contact={
        "name": "Study Spot Reviews API Support",
        "email": "support@studyspotreviews.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with tags
app.include_router(
    user_routes.router, 
    prefix="/api/v1",
    tags=["Users"]
)
app.include_router(
    review_routes.router, 
    prefix="/api/v1",
    tags=["Reviews"]
)
app.include_router(
    cafe_routes.router, 
    prefix="/api/v1",
    tags=["Cafes"]
)
app.include_router(
    file_routes.router, 
    prefix="/api/v1/files",
    tags=["File Management"]
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.2f}s"
    )
    return response

# Only connect to the database on startup if not in test mode
# The test setup will handle the database connection
if not os.getenv("TEST_MODE"):
    @app.on_event("startup")
    async def startup_db_client():
        logger.info("Starting up application...")
        await Database.connect_db()
        logger.info("Database connection established")

    @app.on_event("shutdown")
    async def shutdown_db_client():
        logger.info("Shutting down application...")
        await Database.close_db()
        logger.info("Database connection closed")

@app.get(
    "/",
    summary="API Root",
    description="Welcome endpoint for the Study Spot Reviews API",
    tags=["Health Check"]
)
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Study Spot Reviews API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "User Management & Authentication",
            "Cafe Management",
            "Review System",
            "Photo & File Uploads",
            "Search & Discovery",
            "Geospatial Queries"
        ]
    }

@app.get(
    "/health",
    summary="Health Check",
    description="Check if the API is running and healthy",
    tags=["Health Check"]
)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi 