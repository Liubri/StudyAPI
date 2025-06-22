# StudyAPI

A FastAPI application for managing study spots, reviews, and users.

## Features

### 🏠 Study Spots & Reviews

-   Create and manage reviews for study spots
-   Upload photos for reviews
-   Rate study spots on multiple criteria

### 📖 Bookmark System (NEW!)

-   **Save Favorite Cafes**: Users can bookmark their favorite study spots
-   **Manage Bookmarks**: Create, view, and delete bookmarks
-   **User Bookmark Lists**: Get all bookmarks for a user with cafe details
-   **Bookmark Validation**: Check if a bookmark already exists
-   **Timestamp Tracking**: Automatic timestamping of when cafes were bookmarked

### 👤 User Management

-   **User CRUD Operations**: Create, read, update, and delete users
-   **Simple Login System**: Plain text authentication (no encryption)
-   **Profile Pictures**: Upload and manage user profile pictures
-   **User Statistics**: Track cafes visited and average ratings

#### User Fields

-   **Name**: Unique username for the user
-   **Cafes Visited**: Number of cafes the user has visited
-   **Average Rating**: User's average rating across all reviews
-   **Profile Picture**: Optional profile picture upload
-   **Password**: Plain text password for simple authentication

#### Bookmark Fields

-   **User ID**: ID of the user who created the bookmark
-   **Cafe ID**: ID of the cafe being bookmarked
-   **Bookmarked At**: Automatic timestamp when bookmark was created
-   **Cafe Info**: Full cafe details included when retrieving user bookmarks

## API Endpoints

### Bookmark Endpoints (NEW!)

-   `POST /bookmarks/` - Create a new bookmark for a user and cafe
-   `GET /bookmarks/{bookmark_id}` - Get a specific bookmark by ID
-   `GET /users/{user_id}/bookmarks` - Get all bookmarks for a user (with cafe details)
-   `DELETE /bookmarks/{bookmark_id}` - Delete a bookmark by ID
-   `DELETE /users/{user_id}/bookmarks/{cafe_id}` - Delete a bookmark by user and cafe
-   `GET /users/{user_id}/bookmarks/{cafe_id}/exists` - Check if a bookmark exists

### User Endpoints

-   `POST /users` - Create a new user
-   `GET /users` - Get all users (with pagination)
-   `GET /users/{user_id}` - Get specific user by ID
-   `PUT /users/{user_id}` - Update user information
-   `DELETE /users/{user_id}` - Delete user
-   `POST /users/{user_id}/profile-picture` - Upload profile picture
-   `POST /login` - Simple login authentication

### Review Endpoints

-   `POST /reviews` - Create or update a review
-   `POST /reviews/{review_id}/photos` - Upload photos for a review

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the server:

```bash
uvicorn main:app --reload
```

3. Test the User API:

```bash
python test_users.py
```

4. Visit the interactive API docs: http://localhost:8000/docs

## Example Usage

### Create a User

```json
POST /users
{
  "name": "Alice Coffee",
  "cafes_visited": 5,
  "average_rating": 4.2,
  "password": "mypassword123"
}
```

### Login

```json
POST /login
{
  "name": "Alice Coffee",
  "password": "mypassword123"
}
```

### Update User

```json
PUT /users/1
{
  "cafes_visited": 8,
  "average_rating": 4.5
}
```

### Create a Bookmark

```json
POST /bookmarks/
{
  "user_id": "60d5ec49e9af8b2c24e8a1b2",
  "cafe_id": "60d5ec49e9af8b2c24e8a1b3"
}
```

### Get User Bookmarks (with Cafe Details)

```json
GET /users/60d5ec49e9af8b2c24e8a1b2/bookmarks

Response:
[
  {
    "id": "60d5ec49e9af8b2c24e8a1b4",
    "user_id": "60d5ec49e9af8b2c24e8a1b2",
    "cafe_id": "60d5ec49e9af8b2c24e8a1b3",
    "bookmarked_at": "2024-01-15T10:30:00Z",
    "cafe": {
      "id": "60d5ec49e9af8b2c24e8a1b3",
      "name": "The Coffee Corner",
      "address": {
        "street": "123 Main St",
        "city": "San Francisco",
        "state": "CA"
      },
      "average_rating": 4
    }
  }
]
```

### Check if Bookmark Exists

```json
GET /users/60d5ec49e9af8b2c24e8a1b2/bookmarks/60d5ec49e9af8b2c24e8a1b3/exists

Response:
{
  "exists": true
}
```

## Security Notice

⚠️ **This implementation uses plain text passwords for simplicity as requested. In production, always use proper password hashing and authentication mechanisms.**

```

tests:
docker-compose run --rm -e TEST_MODE=1 api python -m pytest -v

docker-compose up
```
