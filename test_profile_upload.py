#!/usr/bin/env python3
"""
Test script for profile picture upload functionality
"""
import asyncio
import aiohttp
import json
from io import BytesIO
from PIL import Image
import os

BASE_URL = "http://localhost:8000/api/v1"

async def create_test_image():
    """Create a simple test image"""
    # Create a simple 100x100 red square image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to BytesIO buffer
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer.getvalue()

async def test_file_upload():
    """Test the general file upload endpoint"""
    print("🔬 Testing general file upload endpoint...")
    
    # Create test image
    image_data = await create_test_image()
    
    async with aiohttp.ClientSession() as session:
        # Create form data
        data = aiohttp.FormData()
        data.add_field('file', 
                      image_data, 
                      filename='test_image.png', 
                      content_type='image/png')
        
        # Upload file
        async with session.post(f"{BASE_URL}/files/upload", data=data) as response:
            result = await response.json()
            print(f"Status: {response.status}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status == 200:
                print(f"✅ File upload successful!")
                print(f"🔗 URL: {result.get('url')}")
                return result.get('url')
            else:
                print(f"❌ File upload failed!")
                return None

async def create_test_user():
    """Create a test user for profile picture upload"""
    print("👤 Creating test user...")
    
    user_data = {
        "name": f"testuser_{os.urandom(4).hex()}",
        "password": "testpassword123",
        "cafes_visited": 0,
        "average_rating": 0.0
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/users/", json=user_data) as response:
            result = await response.json()
            print(f"Status: {response.status}")
            
            if response.status == 201:
                user_id = result.get('id')
                print(f"✅ User created successfully! ID: {user_id}")
                return user_id
            else:
                print(f"❌ User creation failed: {result}")
                return None

async def test_profile_picture_upload(user_id):
    """Test profile picture upload"""
    print(f"🖼️  Testing profile picture upload for user {user_id}...")
    
    # Create test image
    image_data = await create_test_image()
    
    async with aiohttp.ClientSession() as session:
        # Create form data
        data = aiohttp.FormData()
        data.add_field('file', 
                      image_data, 
                      filename='profile_picture.png', 
                      content_type='image/png')
        
        # Upload profile picture
        async with session.post(f"{BASE_URL}/users/{user_id}/profile-picture", data=data) as response:
            result = await response.json()
            print(f"Status: {response.status}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status == 200:
                print(f"✅ Profile picture upload successful!")
                print(f"🔗 URL: {result.get('url')}")
                return result.get('url')
            else:
                print(f"❌ Profile picture upload failed!")
                return None

async def get_user_details(user_id):
    """Get user details to verify profile picture was saved"""
    print(f"🔍 Getting user details for {user_id}...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/users/{user_id}") as response:
            result = await response.json()
            print(f"Status: {response.status}")
            print(f"User profile picture: {result.get('profile_picture')}")
            return result

async def main():
    """Main test function"""
    print("🚀 Starting profile picture upload tests...")
    print("=" * 60)
    
    try:
        # Test 1: General file upload
        print("\n1️⃣  Testing general file upload endpoint...")
        file_url = await test_file_upload()
        
        if not file_url:
            print("❌ General file upload failed, stopping tests")
            return
        
        # Test 2: Create a test user
        print("\n2️⃣  Creating test user...")
        user_id = await create_test_user()
        
        if not user_id:
            print("❌ User creation failed, stopping tests")
            return
        
        # Test 3: Upload profile picture
        print("\n3️⃣  Testing profile picture upload...")
        profile_url = await test_profile_picture_upload(user_id)
        
        # Test 4: Verify user details
        print("\n4️⃣  Verifying user profile was updated...")
        await get_user_details(user_id)
        
        if profile_url:
            print(f"\n🎉 All tests completed!")
            print(f"Profile picture URL: {profile_url}")
        else:
            print(f"\n❌ Profile picture upload test failed")
            
    except Exception as e:
        print(f"💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 