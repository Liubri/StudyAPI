from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from app.services.s3_service import S3Service
from app.config.logging_config import logger

router = APIRouter()
s3_service = S3Service()

@router.post(
    "/upload",
    summary="Upload a file",
    description="Upload a file to DigitalOcean Spaces and get back the public URL",
    response_description="The public URL of the uploaded file",
    responses={
        200: {
            "description": "File uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "url": "https://madstudycafe.nyc3.digitaloceanspaces.com/photos/12345678-1234-1234-1234-123456789abc.jpg",
                        "message": "File uploaded successfully"
                    }
                }
            }
        },
        400: {
            "description": "Bad request - invalid file",
            "content": {
                "application/json": {
                    "example": {"detail": "No file provided"}
                }
            }
        },
        500: {
            "description": "Internal server error - upload failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to upload file to S3"}
                }
            }
        }
    }
)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a single file to DigitalOcean Spaces.
    
    - **file**: The file to upload (multipart/form-data)
    
    Returns the public URL where the file can be accessed.
    """
    logger.info(f"File upload endpoint: Received file '{file.filename}' with content type '{file.content_type}'")
    
    try:
        # Validate file type (optional - you can add specific validations)
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type and file.content_type not in allowed_types:
            logger.warning(f"File upload endpoint: Rejected file type '{file.content_type}'")
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Upload file
        file_url = await s3_service.upload_file(file, folder="photos")
        
        logger.info(f"File upload endpoint: SUCCESS! File uploaded to: {file_url}")
        print(f"🔗 UPLOADED FILE URL: {file_url}")  # Print to console for immediate visibility
        
        return {
            "url": file_url,
            "message": "File uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload endpoint: Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@router.post(
    "/upload-multiple",
    summary="Upload multiple files",
    description="Upload multiple files to DigitalOcean Spaces and get back their public URLs",
    response_description="List of public URLs for the uploaded files",
    responses={
        200: {
            "description": "Files uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "urls": [
                            "https://madstudycafe.nyc3.digitaloceanspaces.com/photos/12345678-1234-1234-1234-123456789abc.jpg",
                            "https://madstudycafe.nyc3.digitaloceanspaces.com/photos/87654321-4321-4321-4321-cba987654321.png"
                        ],
                        "message": "2 files uploaded successfully"
                    }
                }
            }
        },
        400: {
            "description": "Bad request - invalid files",
            "content": {
                "application/json": {
                    "example": {"detail": "No files provided"}
                }
            }
        }
    }
)
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files to DigitalOcean Spaces.
    
    - **files**: List of files to upload (multipart/form-data)
    
    Returns a list of public URLs where the files can be accessed.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Validate file types
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        uploaded_urls = []
        
        for file in files:
            if file.content_type and file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file.content_type} not allowed for file {file.filename}. Allowed types: {', '.join(allowed_types)}"
                )
            
            # Upload each file
            file_url = await s3_service.upload_file(file, folder="photos")
            uploaded_urls.append(file_url)
        
        return {
            "urls": uploaded_urls,
            "message": f"{len(uploaded_urls)} files uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@router.delete(
    "/delete",
    summary="Delete a file",
    description="Delete a file from DigitalOcean Spaces using its URL",
    responses={
        200: {
            "description": "File deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "File deleted successfully"}
                }
            }
        },
        400: {
            "description": "Bad request - invalid URL",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid file URL"}
                }
            }
        },
        404: {
            "description": "File not found",
            "content": {
                "application/json": {
                    "example": {"detail": "File not found"}
                }
            }
        }
    }
)
async def delete_file(file_url: str):
    """
    Delete a file from DigitalOcean Spaces.
    
    - **file_url**: The public URL of the file to delete
    """
    try:
        success = await s3_service.delete_file(file_url)
        
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(
                status_code=404,
                detail="File not found or could not be deleted"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get(
    "/info",
    summary="Get file information",
    description="Get information about a file in DigitalOcean Spaces",
    responses={
        200: {
            "description": "File information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "size": 1024768,
                        "last_modified": "2024-01-15T10:30:00Z",
                        "content_type": "image/jpeg",
                        "etag": "\"d41d8cd98f00b204e9800998ecf8427e\""
                    }
                }
            }
        },
        404: {
            "description": "File not found",
            "content": {
                "application/json": {
                    "example": {"detail": "File not found"}
                }
            }
        }
    }
)
async def get_file_info(file_url: str):
    """
    Get information about a file in DigitalOcean Spaces.
    
    - **file_url**: The public URL of the file
    """
    try:
        file_info = s3_service.get_file_info(file_url)
        
        if file_info:
            return file_info
        else:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) 