#!/usr/bin/env python3
"""
Simple test script to verify the fake data generation and relationships work properly.
Run this after generating fake data to verify everything is working.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_data_relationships():
    """Test that the generated data has proper relationships"""
    print("🔍 Testing generated data relationships...\n")
    
    # Get all users
    print("1. Fetching users...")
    users_response = requests.get(f"{BASE_URL}/users/")
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.text}")
        return
    
    users = users_response.json()
    print(f"   ✅ Found {len(users)} users")
    
    # Get all cafes
    print("\n2. Fetching cafes...")
    cafes_response = requests.get(f"{BASE_URL}/cafes/")
    if cafes_response.status_code != 200:
        print(f"❌ Failed to get cafes: {cafes_response.text}")
        return
    
    cafes = cafes_response.json()
    print(f"   ✅ Found {len(cafes)} cafes")
    
    # Get all reviews
    print("\n3. Fetching reviews...")
    reviews_response = requests.get(f"{BASE_URL}/reviews/")
    if reviews_response.status_code != 200:
        print(f"❌ Failed to get reviews: {reviews_response.text}")
        return
    
    reviews = reviews_response.json()
    print(f"   ✅ Found {len(reviews)} reviews")
    
    if not users or not cafes or not reviews:
        print("\n❌ Not enough data to test relationships. Run generate_fake_data.py first!")
        return
    
    # Test relationships
    print("\n4. Testing data relationships...")
    
    user_ids = set(user['id'] for user in users)
    cafe_ids = set(cafe['id'] for cafe in cafes)
    
    valid_reviews = 0
    invalid_reviews = 0
    
    for review in reviews:
        user_id = review.get('user_id')
        cafe_id = review.get('study_spot_id')
        
        if user_id in user_ids and cafe_id in cafe_ids:
            valid_reviews += 1
        else:
            invalid_reviews += 1
            print(f"   ❌ Invalid review: user_id={user_id}, cafe_id={cafe_id}")
    
    print(f"   ✅ Valid reviews: {valid_reviews}")
    print(f"   ❌ Invalid reviews: {invalid_reviews}")
    
    # Show sample data
    print("\n5. Sample data:")
    sample_user = users[0]
    sample_cafe = cafes[0]
    sample_review = reviews[0] if reviews else None
    
    print(f"   👤 Sample User: {sample_user['name']}")
    print(f"      - Cafes visited: {sample_user['cafes_visited']}")
    print(f"      - Average rating: {sample_user['average_rating']}")
    
    print(f"   ☕ Sample Cafe: {sample_cafe['name']}")
    print(f"      - Address: {sample_cafe['address']['street']}, {sample_cafe['address']['city']}")
    print(f"      - Amenities: {', '.join(sample_cafe['amenities'][:3])}...")
    print(f"      - Average rating: {sample_cafe['average_rating']}")
    
    if sample_review:
        user_name = next((u['name'] for u in users if u['id'] == sample_review['user_id']), "Unknown")
        cafe_name = next((c['name'] for c in cafes if c['id'] == sample_review['study_spot_id']), "Unknown")
        print(f"   📝 Sample Review:")
        print(f"      - User: {user_name}")
        print(f"      - Cafe: {cafe_name}")
        print(f"      - Overall rating: {sample_review['overall_rating']}")
        print(f"      - Atmosphere: {sample_review['atmosphere']}")
    
    # Test login with generated user
    print("\n6. Testing login with generated user...")
    if users:
        # Try to login with first user (password should be password1, password2, etc.)
        test_user = users[0]
        # Extract number from user ID or use index
        password_num = 1  # Default to 1 since we don't store which password was used
        
        login_data = {
            "name": test_user['name'],
            "password": f"password{password_num}"
        }
        
        login_response = requests.post(f"{BASE_URL}/login", json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"   ✅ Login successful for user: {login_result['user_name']}")
        else:
            # Try a few different password numbers
            success = False
            for i in range(1, 11):
                login_data['password'] = f"password{i}"
                login_response = requests.post(f"{BASE_URL}/login", json=login_data)
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    print(f"   ✅ Login successful for user: {login_result['user_name']} with password{i}")
                    success = True
                    break
            
            if not success:
                print(f"   ❌ Login failed for user {test_user['name']}")
    
    print(f"\n🎉 Data relationship testing complete!")
    print(f"   📊 Summary: {len(users)} users, {len(cafes)} cafes, {len(reviews)} reviews")
    print(f"   🔗 Valid relationships: {valid_reviews}/{len(reviews)} reviews")

def get_data_statistics():
    """Get detailed statistics about the generated data"""
    print("📊 Data Statistics")
    print("=" * 40)
    
    try:
        # Users stats
        users_response = requests.get(f"{BASE_URL}/users/")
        if users_response.status_code == 200:
            users = users_response.json()
            if users:
                avg_cafes_visited = sum(u['cafes_visited'] for u in users) / len(users)
                avg_user_rating = sum(u['average_rating'] for u in users) / len(users)
                print(f"👥 Users: {len(users)}")
                print(f"   Average cafes visited: {avg_cafes_visited:.1f}")
                print(f"   Average user rating: {avg_user_rating:.1f}")
        
        # Cafes stats  
        cafes_response = requests.get(f"{BASE_URL}/cafes/")
        if cafes_response.status_code == 200:
            cafes = cafes_response.json()
            if cafes:
                cities = [c['address']['city'] for c in cafes]
                city_counts = {}
                for city in cities:
                    city_counts[city] = city_counts.get(city, 0) + 1
                
                print(f"☕ Cafes: {len(cafes)}")
                print(f"   Cities: {dict(list(city_counts.items())[:3])}...")  # Show top 3 cities
        
        # Reviews stats
        reviews_response = requests.get(f"{BASE_URL}/reviews/")
        if reviews_response.status_code == 200:
            reviews = reviews_response.json()
            if reviews:
                avg_overall = sum(r['overall_rating'] for r in reviews) / len(reviews)
                avg_wifi = sum(r['wifi_quality'] for r in reviews) / len(reviews)
                print(f"📝 Reviews: {len(reviews)}")
                print(f"   Average overall rating: {avg_overall:.1f}")
                print(f"   Average wifi rating: {avg_wifi:.1f}")
                
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")

if __name__ == "__main__":
    print("🧪 Fake Data Testing Script")
    print("=" * 50)
    print()
    
    try:
        # Test API connection
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ API server not accessible")
            exit(1)
        
        get_data_statistics()
        print()
        test_data_relationships()
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Make sure to start the server first:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error during testing: {e}") 