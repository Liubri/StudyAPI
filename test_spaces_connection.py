#!/usr/bin/env python3
import boto3
import os
from io import BytesIO
from botocore.exceptions import ClientError, NoCredentialsError

def test_spaces_connection():
    """Test Digital Ocean Spaces connection and upload functionality"""
    
    # Configuration
    endpoint_url = "https://nyc3.digitaloceanspaces.com"
    bucket_name = "madstudycafe"
    access_key = os.getenv("DO_SPACES_ACCESS_KEY", "DO00EPMZYTVZHPHR3G8P")
    secret_key = os.getenv("DO_SPACES_SECRET_KEY", "FA8l/8u9JAZPBfBni/781lBKsb9KEhBO7s3+s3ptYK4")
    region = "nyc3"
    
    print("🔍 Testing Digital Ocean Spaces Connection...")
    print(f"Endpoint: {endpoint_url}")
    print(f"Bucket: {bucket_name}")
    print(f"Access Key: {access_key[:10]}..." if access_key else "❌ Not set")
    print(f"Secret Key: {'✅ Set' if secret_key else '❌ Not set'}")
    print("-" * 50)
    
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test 1: List buckets
        print("📋 Test 1: Listing buckets...")
        try:
            response = s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            print(f"✅ Available buckets: {buckets}")
            
            if bucket_name not in buckets:
                print(f"❌ ERROR: Bucket '{bucket_name}' not found in available buckets!")
                return False
        except Exception as e:
            print(f"❌ ERROR listing buckets: {str(e)}")
            return False
        
        # Test 2: Test upload
        print("📤 Test 2: Testing file upload...")
        test_content = b"This is a test file for Digital Ocean Spaces"
        test_key = "test/connection_test.txt"
        
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType="text/plain",
                ACL='public-read'
            )
            
            # Construct public URL
            public_url = f"https://{bucket_name}.{region}.digitaloceanspaces.com/{test_key}"
            print(f"✅ File uploaded successfully!")
            print(f"📍 Public URL: {public_url}")
            
        except Exception as e:
            print(f"❌ ERROR uploading file: {str(e)}")
            return False
        
        # Test 3: Verify file exists
        print("🔍 Test 3: Verifying uploaded file...")
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=test_key)
            print(f"✅ File verified! Size: {response.get('ContentLength')} bytes")
        except Exception as e:
            print(f"❌ ERROR verifying file: {str(e)}")
            return False
        
        # Test 4: Clean up test file
        print("🧹 Test 4: Cleaning up test file...")
        try:
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print("✅ Test file deleted successfully!")
        except Exception as e:
            print(f"⚠️  WARNING: Could not delete test file: {str(e)}")
        
        print("\n🎉 All tests passed! Digital Ocean Spaces is working correctly.")
        return True
        
    except NoCredentialsError:
        print("❌ ERROR: S3 credentials not configured properly")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_spaces_connection()
    exit(0 if success else 1) 