# StudyAPI

A FastAPI application for managing study spots, reviews, and users.

## Features

### 🏠 Study Spots & Reviews

-   Create and manage reviews for study spots
-   Upload photos for reviews
-   Rate study spots on multiple criteria

### 👤 User Management (NEW!)

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

## API Endpoints

### User Endpoints

-   `POST /users` - Create a new user
-   `GET /users` - Get all users (with pagination)
-   `GET /users/{user_id}` - Get specific user by ID
-   `PUT /users/{user_id}` - Update user information
-   `DELETE /users/{user_id}` - Delete user
-   `POST /users/{user_id}/profile-picture` - Upload profile picture
-   `POST /login` - Simple login authentication

### Review Endpoints (Existing)

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

## Security Notice

⚠️ **This implementation uses plain text passwords for simplicity as requested. In production, always use proper password hashing and authentication mechanisms.**

```

tests:
docker-compose run --rm -e TEST_MODE=1 api python -m pytest -v

docker-compose up
```
