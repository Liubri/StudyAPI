import boto3
import uuid
import os
from typing import Optional
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError, NoCredentialsError

class S3Service:
    def __init__(self):
        # DigitalOcean Spaces configuration
        self.endpoint_url = "https://nyc3.digitaloceanspaces.com"
        self.bucket_name = "madstudycafe"
        self.access_key = os.getenv("DO_SPACES_ACCESS_KEY", "DO00EPMZYTVZHPHR3G8P")
        self.secret_key = os.getenv("DO_SPACES_SECRET_KEY", "FA8l/8u9JAZPBfBni/781lBKsb9KEhBO7s3+s3ptYK4")
        self.region = "nyc3"
        
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
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # Generate unique filename
            file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            
            # Create the full key (path) for the file
            file_key = f"{folder}/{unique_filename}"
            
            # Read file content
            file_content = await file.read()
            
            # Upload to DigitalOcean Spaces
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type or "application/octet-stream",
                ACL='public-read'  # Make the file publicly accessible
            )
            
            # Construct the public URL
            public_url = f"https://{self.bucket_name}.{self.region}.digitaloceanspaces.com/{file_key}"
            
            return public_url
            
        except NoCredentialsError:
            raise HTTPException(
                status_code=500,
                detail="S3 credentials not configured properly"
            )
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to S3: {str(e)}"
            )
        except Exception as e:
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