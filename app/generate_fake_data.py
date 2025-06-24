#!/usr/bin/env python3
"""
Generate fake data for the StudyAPI MongoDB database.
Creates 10 users, 10 cafes, and 20 reviews with realistic relationships.

Run this after starting the FastAPI server with: uvicorn app.main:app --reload
"""

import requests
import json
import random
from faker import Faker
from typing import List, Dict

# Initialize Faker for generating realistic fake data
fake = Faker()

BASE_URL = "http://localhost:8000/api/v1"

# Realistic data pools for cafes (Boston-themed)
CAFE_NAMES = [
    "The Beantown Grind", "Harvard Square Coffee", "MIT Study Lounge", "Fenway Brew",
    "Tea Party Cafe", "Back Bay Coffee Co.", "The Cambridge Roast", "North End Espresso",
    "Beacon Hill Beans", "South End Study Spot", "Blue Line Coffee", "The Hub Cafe",
    "Quincy Market Coffee", "Boston Common Brew", "Newbury Street Coffee"
]

AMENITIES_POOL = [
    "Free WiFi", "Power outlets", "Outdoor seating", "Quiet zone", 
    "Group study rooms", "Pet friendly", "24/7 access", "Parking available",
    "Wheelchair accessible", "Student discounts", "Meeting rooms", "Printing services",
    "Lockers", "Food available", "Air conditioning", "Natural lighting"
]

ATMOSPHERE_OPTIONS = [
    "Quiet and peaceful", "Bustling with energy", "Cozy and intimate",
    "Modern and minimalist", "Warm and inviting", "Productive atmosphere",
    "Relaxed vibe", "Professional setting", "Creative space", "Academic focused"
]

ENERGY_LEVELS = ["Very calm", "Calm", "Moderate", "Energetic", "Very energetic"]

STUDY_FRIENDLY_OPTIONS = [
    "Perfect for studying", "Good for individual work", "Great for group projects",
    "Excellent for exam prep", "Ideal for reading", "Good for laptop work",
    "Better for short sessions", "Great for long study sessions"
]

# New cafe tag options
ATMOSPHERE_OPTIONS = ["Cozy", "Rustic", "Traditional", "Warm", "Clean"]
ENERGY_LEVEL_OPTIONS = ["quiet", "low-key", "tranquil", "moderate", "average"]
STUDY_FRIENDLY_LEVELS = ["study heaven", "good", "decent", "mixed", "fair"]

# Boston Metropolitan Area coordinates for realistic locations
BOSTON_AREA_BOUNDS = {
    "lat_min": 42.25, "lat_max": 42.45,
    "lng_min": -71.25, "lng_max": -70.95
}

def generate_boston_coordinates():
    """Generate random coordinates within Boston Metropolitan Area"""
    lat = random.uniform(BOSTON_AREA_BOUNDS["lat_min"], BOSTON_AREA_BOUNDS["lat_max"])
    lng = random.uniform(BOSTON_AREA_BOUNDS["lng_min"], BOSTON_AREA_BOUNDS["lng_max"])
    return [lng, lat]  # [longitude, latitude] format for MongoDB

def generate_fake_users(count: int = 10) -> List[Dict]:
    """Generate fake user data"""
    users = []
    
    for i in range(count):
        # Generate realistic user data
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}"
        
        user_data = {
            "name": username,
            "cafes_visited": random.randint(1, 25),
            "average_rating": round(random.uniform(3.0, 5.0), 1),
            "password": f"password{i+1}"  # Simple password for testing
        }
        users.append(user_data)
    
    return users

def generate_fake_cafes(count: int = 10) -> List[Dict]:
    """Generate fake cafe data"""
    cafes = []
    used_names = set()
    
    for i in range(count):
        # Ensure unique cafe names
        cafe_name = random.choice(CAFE_NAMES)
        while cafe_name in used_names:
            cafe_name = random.choice(CAFE_NAMES)
        used_names.add(cafe_name)
        
        # Generate realistic address
        address = {
            "street": fake.street_address(),
            "city": random.choice(["Boston", "Cambridge", "Somerville", "Brookline", "Newton"]),
            "state": "MA",
            "zip_code": fake.zipcode(),
            "country": "USA"
        }
        
        # Generate location coordinates
        coordinates = generate_boston_coordinates()
        location = {
            "type": "Point",
            "coordinates": coordinates
        }
        
        # Generate amenities (3-6 random amenities)
        amenities = random.sample(AMENITIES_POOL, random.randint(3, 6))
        
        # Generate opening hours
        opening_hours = {
            "Monday": f"{random.randint(6,8)}AM - {random.randint(8,10)}PM",
            "Tuesday": f"{random.randint(6,8)}AM - {random.randint(8,10)}PM",
            "Wednesday": f"{random.randint(6,8)}AM - {random.randint(8,10)}PM",
            "Thursday": f"{random.randint(6,8)}AM - {random.randint(8,10)}PM",
            "Friday": f"{random.randint(6,8)}AM - {random.randint(8,10)}PM",
            "Saturday": f"{random.randint(7,9)}AM - {random.randint(7,9)}PM",
            "Sunday": f"{random.randint(7,9)}AM - {random.randint(7,9)}PM"
        }
        
        cafe_data = {
            "name": cafe_name,
            "address": address,
            "location": location,
            "phone": fake.phone_number(),
            "website": f"https://www.{cafe_name.lower().replace(' ', '').replace('&', 'and')}.com",
            "opening_hours": opening_hours,
            "amenities": amenities,
            "thumbnail_url": "https://plus.unsplash.com/premium_photo-1664970900025-1e3099ca757a?q=80&w=987&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            "wifi_access": random.randint(1, 3),  # 1=POOR, 2=FAIR, 3=EXCELLENT
            "outlet_accessibility": random.randint(1, 3),
            "average_rating": random.randint(3, 5),
            "atmosphere": random.sample(ATMOSPHERE_OPTIONS, random.randint(4, min(5, len(ATMOSPHERE_OPTIONS)))),
            "energy_level": random.sample(ENERGY_LEVEL_OPTIONS, random.randint(4, min(5, len(ENERGY_LEVEL_OPTIONS)))),
            "study_friendly": random.sample(STUDY_FRIENDLY_LEVELS, random.randint(4, min(5, len(STUDY_FRIENDLY_LEVELS))))
        }
        cafes.append(cafe_data)
    
    return cafes

def generate_fake_reviews(user_ids: List[str], cafe_ids: List[str], count: int = 20) -> List[Dict]:
    """Generate fake review data with relationships to users and cafes"""
    reviews = []
    
    for i in range(count):
        # Randomly select user and cafe
        user_id = random.choice(user_ids)
        cafe_id = random.choice(cafe_ids)
        
        # Generate correlated ratings (if overall is high, others tend to be high too)
        overall_rating = round(random.uniform(2.5, 5.0), 1)
        
        # Correlation factor (higher overall rating tends to correlate with other ratings)
        correlation_factor = (overall_rating - 2.5) / 2.5  # 0 to 1
        
        wifi_quality = round(random.uniform(
            max(1.0, overall_rating - 1.5), 
            min(5.0, overall_rating + 0.5)
        ), 1)
        
        outlet_accessibility = round(random.uniform(
            max(1.0, overall_rating - 1.5), 
            min(5.0, overall_rating + 0.5)
        ), 1)
        
        review_data = {
            "study_spot_id": cafe_id,
            "user_id": user_id,
            "overall_rating": overall_rating,
            "outlet_accessibility": outlet_accessibility,
            "wifi_quality": wifi_quality,
            "atmosphere": random.choice(ATMOSPHERE_OPTIONS),
            "energy_level": random.choice(ENERGY_LEVELS),
            "study_friendly": random.choice(STUDY_FRIENDLY_OPTIONS)
        }
        reviews.append(review_data)
    
    return reviews

def create_data_via_api():
    """Create all fake data via API calls"""
    print("🚀 Starting fake data generation...\n")
    
    # Generate fake data
    print("📊 Generating fake data...")
    users_data = generate_fake_users(10)
    cafes_data = generate_fake_cafes(10)
    print(f"   ✅ Generated {len(users_data)} users")
    print(f"   ✅ Generated {len(cafes_data)} cafes")
    
    # Create users
    # print("\n👥 Creating users...")
    # created_users = []
    # for i, user_data in enumerate(users_data):
    #     try:
    #         response = requests.post(f"{BASE_URL}/users/", json=user_data)
    #         if response.status_code == 201:
    #             user = response.json()
    #             # Check if 'id' field exists, fallback to '_id' if needed
    #             user_id = user.get('id') or user.get('_id')
    #             if not user_id:
    #                 print(f"   ❌ Response missing both 'id' and '_id' fields. Available keys: {list(user.keys())}")
    #                 continue
    #             # Normalize the response to always have 'id' field
    #             if 'id' not in user and '_id' in user:
    #                 user['id'] = user['_id']
    #             created_users.append(user)
    #             print(f"   ✅ Created user: {user['name']} (ID: {user_id[:8]}...)")
    #         else:
    #             print(f"   ❌ Failed to create user {user_data['name']}: {response.text}")
    #     except KeyError as e:
    #         print(f"   ❌ KeyError accessing field {e} in response for user {user_data['name']}")
    #         print(f"   📥 Full response: {response.json() if response.status_code == 201 else response.text}")
    #     except Exception as e:
    #         print(f"   ❌ Error creating user {user_data['name']}: {e}")
    
    # Create cafes
    print("\n☕ Creating cafes...")
    created_cafes = []
    for i, cafe_data in enumerate(cafes_data):
        try:
            response = requests.post(f"{BASE_URL}/cafes/", json=cafe_data)
            if response.status_code == 201:
                cafe = response.json()
                # Check if 'id' field exists, fallback to '_id' if needed
                cafe_id = cafe.get('id') or cafe.get('_id')
                if not cafe_id:
                    print(f"   ❌ Response missing both 'id' and '_id' fields. Available keys: {list(cafe.keys())}")
                    continue
                # Normalize the response to always have 'id' field
                if 'id' not in cafe and '_id' in cafe:
                    cafe['id'] = cafe['_id']
                created_cafes.append(cafe)
                print(f"   ✅ Created cafe: {cafe['name']} (ID: {cafe_id[:8]}...)")
            else:
                print(f"   ❌ Failed to create cafe {cafe_data['name']}: {response.text}")
        except KeyError as e:
            print(f"   ❌ KeyError accessing field {e} in response for cafe {cafe_data['name']}")
            print(f"   📥 Full response: {response.json() if response.status_code == 201 else response.text}")
        except Exception as e:
            print(f"   ❌ Error creating cafe {cafe_data['name']}: {e}")
    
    # if not created_users or not created_cafes:
    #     print("\n❌ Cannot create reviews without users and cafes!")
    #     return
    
    # # Generate and create reviews
    # user_ids = [user['id'] for user in created_users]
    # cafe_ids = [cafe['id'] for cafe in created_cafes]
    # reviews_data = generate_fake_reviews(user_ids, cafe_ids, 20)
    
    # print(f"\n📝 Creating {len(reviews_data)} reviews...")
    # created_reviews = []
    # for i, review_data in enumerate(reviews_data):
    #     try:
    #         response = requests.post(f"{BASE_URL}/reviews/", json=review_data)
    #         if response.status_code == 201:  # Reviews return 201, not 200
    #             review = response.json()
    #             # Check if 'id' field exists, fallback to '_id' if needed
    #             review_id = review.get('id') or review.get('_id')
    #             if not review_id:
    #                 print(f"   ❌ Response missing both 'id' and '_id' fields. Available keys: {list(review.keys())}")
    #                 continue
    #             # Normalize the response to always have 'id' field
    #             if 'id' not in review and '_id' in review:
    #                 review['id'] = review['_id']
    #             created_reviews.append(review)
    #             print(f"   ✅ Created review {i+1}/20 (ID: {review_id[:8]}...)")
    #         else:
    #             print(f"   ❌ Failed to create review {i+1} (status {response.status_code}): {response.text}")
    #     except KeyError as e:
    #         print(f"   ❌ KeyError accessing field {e} in response for review {i+1}")
    #         print(f"   📥 Full response: {response.json() if response.status_code == 201 else response.text}")
    #     except Exception as e:
    #         print(f"   ❌ Error creating review {i+1}: {e}")
    
    # # Summary
    # print(f"\n🎉 Data generation complete!")
    # print(f"   📊 Users created: {len(created_users)}/10")
    # print(f"   📊 Cafes created: {len(created_cafes)}/10")
    # print(f"   📊 Reviews created: {len(created_reviews)}/20")
    
    # # Show sample data relationships
    # if created_users and created_cafes and created_reviews:
    #     print(f"\n🔗 Sample relationships:")
    #     sample_review = reviews_data[0] if reviews_data else None
    #     if sample_review:
    #         user_name = next((u['name'] for u in created_users if u['id'] == sample_review['user_id']), "Unknown")
    #         cafe_name = next((c['name'] for c in created_cafes if c['id'] == sample_review['study_spot_id']), "Unknown")
    #         print(f"   👤 User '{user_name}' reviewed ☕ '{cafe_name}' with {sample_review['overall_rating']} stars")

def print_generated_data_info():
    """Print information about the data that will be generated"""
    print("📋 Fake Data Generation Script")
    print("=" * 50)
    print()
    print("This script will generate:")
    print("👥 10 realistic users with:")
    print("   - Unique usernames (firstname.lastname + number)")
    print("   - Random cafes visited count (1-25)")
    print("   - Random average ratings (3.0-5.0)")
    print("   - Simple passwords for testing")
    print()
    print("☕ 10 cafes with:")
    print("   - Realistic names from curated list")
    print("   - SF Bay Area addresses and coordinates")
    print("   - Random amenities (3-6 per cafe)")
    print("   - Realistic opening hours")
    print("   - Phone numbers and websites")
    print("   - Access level ratings")
    print()
    print("📝 20 reviews with:")
    print("   - Random user-cafe relationships")
    print("   - Correlated ratings (realistic score relationships)")
    print("   - Varied atmosphere and energy descriptions")
    print("   - Study-friendly assessments")
    print()
    print("🔗 All data will be properly related:")
    print("   - Reviews reference actual user and cafe IDs")
    print("   - No orphaned or invalid references")
    print()

def test_api_connection():
    """Test if the API is accessible"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API server is accessible")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Make sure to start the server first:")
        print("   uvicorn app.main:app --reload")
        return False

if __name__ == "__main__":
    print_generated_data_info()
    print()
    
    # Test API connection first
    if not test_api_connection():
        exit(1)
    
    print()
    
    # Confirm before proceeding
    response = input("Do you want to proceed with data generation? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Data generation cancelled.")
        exit(0)
    
    try:
        create_data_via_api()
    except KeyboardInterrupt:
        print("\n\n❌ Data generation interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}") 