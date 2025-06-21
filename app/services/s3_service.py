import boto3
import uuid
import os
from typing import Optional
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError, NoCredentialsError
from app.config.logging_config import logger

class S3Service:
    def __init__(self):
        # DigitalOcean Spaces configuration
        self.endpoint_url = "https://nyc3.digitaloceanspaces.com"
        self.bucket_name = "madstudycafe"
        self.access_key = os.getenv("DO_SPACES_ACCESS_KEY", "DO00EPMZYTVZHPHR3G8P")
        self.secret_key = os.getenv("DO_SPACES_SECRET_KEY", "FA8l/8u9JAZPBfBni/781lBKsb9KEhBO7s3+s3ptYK4")
        self.region = "nyc3"
        
        logger.info(f"S3Service initialized with:")
        logger.info(f"  Endpoint: {self.endpoint_url}")
        logger.info(f"  Bucket: {self.bucket_name}")
        logger.info(f"  Region: {self.region}")
        logger.info(f"  Access Key: {self.access_key[:10]}..." if self.access_key else "  Access Key: Not set")
        logger.info(f"  Secret Key: {'Set' if self.secret_key else 'Not set'}")
        
        # Initialize S3 client for DigitalOcean Spaces
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
    
    async def upload_file(self, file: UploadFile, folder: str = "photos") -> str:
        """
        Upload a file to DigitalOcean Spaces and return the public URL.
        
        Args:
            file: The uploaded file from FastAPI
            folder: The folder/prefix to store the file in (default: "photos")
            
        Returns:
            str: The public URL of the uploaded file
            
        Raises:
            HTTPException: If upload fails
        """
        logger.info(f"S3Service: Starting file upload to folder '{folder}'")
        
        try:
            # Validate file
            if not file.filename:
                logger.error("S3Service: No filename provided")
                raise HTTPException(status_code=400, detail="No file provided")
            
            logger.info(f"S3Service: Processing file '{file.filename}' with content type '{file.content_type}'")
            
            # Generate unique filename
            file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            
            # Create the full key (path) for the file
            file_key = f"{folder}/{unique_filename}"
            logger.info(f"S3Service: Generated file key: {file_key}")
            
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            logger.info(f"S3Service: Read {file_size} bytes from uploaded file")
            
            # Reset file position for potential re-reads
            await file.seek(0)
            
            # Validate content type
            content_type = file.content_type or "application/octet-stream"
            logger.info(f"S3Service: Using content type: {content_type}")
            
            # Debug S3 client configuration
            logger.info(f"S3Service: About to upload with:")
            logger.info(f"  Bucket: {self.bucket_name}")
            logger.info(f"  Key: {file_key}")
            logger.info(f"  Content-Type: {content_type}")
            logger.info(f"  Content size: {file_size}")
            
            # Upload to DigitalOcean Spaces
            logger.info(f"S3Service: Uploading to bucket '{self.bucket_name}' with key '{file_key}'")
            
            # Try the upload with detailed error handling
            try:
                response = self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_key,
                    Body=file_content,
                    ContentType=content_type,
                    ACL='public-read'  # Make the file publicly accessible
                )
                logger.info(f"S3Service: put_object response: {response}")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                logger.error(f"S3Service: ClientError - Code: {error_code}, Message: {error_message}")
                logger.error(f"S3Service: Full error response: {e.response}")
                raise e
            except Exception as e:
                logger.error(f"S3Service: Unexpected error during put_object: {str(e)}")
                logger.error(f"S3Service: Error type: {type(e)}")
                raise e
            
            # Construct the public URL
            public_url = f"https://{self.bucket_name}.{self.region}.digitaloceanspaces.com/{file_key}"
            logger.info(f"S3Service: Upload successful! File available at: {public_url}")
            
            return public_url
            
        except NoCredentialsError as e:
            logger.error(f"S3Service: Credentials error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="S3 credentials not configured properly"
            )
        except ClientError as e:
            logger.error(f"S3Service: Client error during upload: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to S3: {str(e)}"
            )
        except Exception as e:
            logger.error(f"S3Service: Unexpected error during upload: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during file upload: {str(e)}"
            )
    
    async def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from DigitalOcean Spaces using its URL.
        
        Args:
            file_url: The public URL of the file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Extract the file key from the URL
            # URL format: https://madstudycafe.nyc3.digitaloceanspaces.com/photos/filename.jpg
            if not file_url.startswith(f"https://{self.bucket_name}.{self.region}.digitaloceanspaces.com/"):
                return False
            
            file_key = file_url.split(f"https://{self.bucket_name}.{self.region}.digitaloceanspaces.com/")[1]
            
            # Delete the file
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            return True
            
        except ClientError as e:
            print(f"Error deleting file from S3: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error during file deletion: {str(e)}")
            return False
    
    def get_file_info(self, file_url: str) -> Optional[dict]:
        """
        Get information about a file in DigitalOcean Spaces.
        
        Args:
            file_url: The public URL of the file
            
        Returns:
            dict: File information or None if file doesn't exist
        """
        try:
            # Extract the file key from the URL
            if not file_url.startswith(f"https://{self.bucket_name}.{self.region}.digitaloceanspaces.com/"):
                return None
            
            file_key = file_url.split(f"https://{self.bucket_name}.{self.region}.digitaloceanspaces.com/")[1]
            
            # Get file metadata
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            return {
                "size": response.get("ContentLength"),
                "last_modified": response.get("LastModified"),
                "content_type": response.get("ContentType"),
                "etag": response.get("ETag")
            }
            
        except ClientError:
            return None
        except Exception:
            return None 