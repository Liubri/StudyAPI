#!/usr/bin/env python3
"""
Test script for the MongoDB-based User CRUD operations and login functionality.
Run this after starting the FastAPI server with: uvicorn app.main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_user_operations():
    print("🚀 Testing MongoDB User CRUD Operations\n")
    
    # 1. Create a new user
    print("1. Creating a new user...")
    user_data = {
        "name": "Alice Coffee MongoDB",
        "cafes_visited": 5,
        "average_rating": 4.2,
        "password": "mypassword123"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code == 201:
        user = response.json()
        user_id = user["id"]
        print(f"✅ User created successfully! ID: {user_id}")
        print(f"   Name: {user['name']}")
        print(f"   Cafes visited: {user['cafes_visited']}")
        print(f"   Average rating: {user['average_rating']}")
    else:
        print(f"❌ Failed to create user: {response.text}")
        return
    
    print()
    
    # 2. Test login
    print("2. Testing login...")
    login_data = {
        "name": "Alice Coffee MongoDB",
        "password": "mypassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    if response.status_code == 200:
        login_result = response.json()
        print(f"✅ Login successful!")
        print(f"   Message: {login_result['message']}")
        print(f"   User ID: {login_result['user_id']}")
        print(f"   User Name: {login_result['user_name']}")
    else:
        print(f"❌ Login failed: {response.text}")
    
    print()
    
    # 3. Test wrong password
    print("3. Testing login with wrong password...")
    wrong_login_data = {
        "name": "Alice Coffee MongoDB",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=wrong_login_data)
    if response.status_code == 401:
        print("✅ Correctly rejected wrong password")
    else:
        print(f"❌ Should have rejected wrong password: {response.text}")
    
    print()
    
    # 4. Get all users
    print("4. Fetching all users...")
    response = requests.get(f"{BASE_URL}/users/")
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"   - {user['name']} (ID: {user['id'][:12]}..., Cafes: {user['cafes_visited']})")
    else:
        print(f"❌ Failed to get users: {response.text}")
    
    print()
    
    # 5. Update user
    print("5. Updating user...")
    update_data = {
        "cafes_visited": 8,
        "average_rating": 4.5
    }
    
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
    if response.status_code == 200:
        updated_user = response.json()
        print(f"✅ User updated successfully!")
        print(f"   New cafes visited: {updated_user['cafes_visited']}")
        print(f"   New average rating: {updated_user['average_rating']}")
    else:
        print(f"❌ Failed to update user: {response.text}")
    
    print()
    
    # 6. Test duplicate username
    print("6. Testing unique name constraint...")
    duplicate_user_data = {
        "name": "Alice Coffee MongoDB",
        "password": "anotherpassword"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=duplicate_user_data)
    if response.status_code == 400:
        print("✅ Correctly rejected duplicate username")
    else:
        print(f"❌ Should have rejected duplicate username: {response.text}")
    
    print()
    
    # 7. Delete user
    print("7. Deleting user...")
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Failed to delete user: {response.text}")
    
    print()
    
    # 8. Verify user is deleted
    print("8. Verifying user deletion...")
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    if response.status_code == 404:
        print("✅ User successfully deleted (404 Not Found)")
    else:
        print(f"❌ User should be deleted: {response.status_code}")
    
    print("\n🎉 MongoDB User CRUD testing complete!")

def print_api_documentation():
    print("📚 MongoDB User API Documentation")
    print("=" * 60)
    print()
    print("Base URL: http://localhost:8000/api/v1")
    print()
    print("Available Endpoints:")
    print("POST   /users/                     - Create a new user")
    print("GET    /users/                     - Get all users (with pagination)")
    print("GET    /users/{user_id}            - Get specific user by ID")
    print("PUT    /users/{user_id}            - Update user")
    print("DELETE /users/{user_id}            - Delete user")
    print("POST   /users/{user_id}/profile-picture - Upload profile picture")
    print("GET    /users/search/?query=text   - Search users by name")
    print("POST   /login                      - Simple login")
    print()
    print("Features:")
    print("✅ Full CRUD operations")
    print("✅ Plain text authentication")
    print("✅ Profile picture upload")
    print("✅ MongoDB integration")
    print("✅ Comprehensive error handling")
    print()

if __name__ == "__main__":
    print_api_documentation()
    print()
    
    try:
        test_user_operations()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API server.")
        print("💡 Make sure to start the server first:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error during testing: {e}") 