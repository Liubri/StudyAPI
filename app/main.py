from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes import review_routes
from app.routes import cafe_routes
from app.config.database import Database
from app.config.logging_config import logger
import time
import os

app = FastAPI(title="Study Spot Reviews API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(review_routes.router, prefix="/api/v1")
app.include_router(cafe_routes.router, prefix="/api/v1")

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

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to Study Spot Reviews API"} 