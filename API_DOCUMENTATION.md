# REST API Documentation

Base URL: `http://localhost:5000/api/v1`

## Authentication

All endpoints (except `/login` and `/health`) require a JWT token in the Authorization header:

```
Authorization: Bearer <your-token>
```

### Login

**POST** `/api/v1/login`

Get an authentication token.

**Request:**
```json
{
  "email": "admin@school.edu",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "Admin User",
    "email": "admin@school.edu",
    "is_admin": true
  }
}
```

## Endpoints

### Health Check

**GET** `/api/v1/health`

Check API status (no auth required).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-26T10:30:00"
}
```

### Users

#### Get All Users (Admin Only)

**GET** `/api/v1/users`

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@school.edu",
      "department": "Mathematics",
      "is_admin": false
    }
  ]
}
```

#### Get User

**GET** `/api/v1/users/<user_id>`

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@school.edu",
  "department": "Mathematics",
  "is_admin": false,
  "created_at": "2024-01-15T10:00:00"
}
```

### Print Requests

#### Get All Requests

**GET** `/api/v1/requests`

Get all print requests (admin sees all, users see only their own).

**Response:**
```json
{
  "requests": [
    {
      "id": 1,
      "request_number": "PR-20241126-ABC123",
      "document_name": "Math Worksheet.pdf",
      "pages": 5,
      "copies": 30,
      "status": "pending",
      "submitted_at": "2024-11-26T09:00:00"
    }
  ]
}
```

#### Get Specific Request

**GET** `/api/v1/requests/<request_id>`

**Response:**
```json
{
  "id": 1,
  "request_number": "PR-20241126-ABC123",
  "document_name": "Math Worksheet.pdf",
  "pages": 5,
  "copies": 30,
  "color": false,
  "double_sided": true,
  "status": "pending",
  "submitted_at": "2024-11-26T09:00:00",
  "user": {
    "id": 2,
    "name": "Sarah Johnson",
    "email": "sarah.johnson@school.edu"
  }
}
```

### Statistics (Admin Only)

**GET** `/api/v1/stats`

Get system statistics.

**Response:**
```json
{
  "total_users": 25,
  "total_requests": 150,
  "pending_requests": 12,
  "completed_requests": 120
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message description"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

## Example Usage

### Using cURL

```bash
# Login
curl -X POST http://localhost:5000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@school.edu","password":"admin123"}'

# Get users (with token)
curl -X GET http://localhost:5000/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Add credit
curl -X POST http://localhost:5000/api/v1/users/2/credit \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"amount":50,"description":"Monthly allocation"}'
```

### Using Python

```python
import requests

# Login
response = requests.post('http://localhost:5000/api/v1/login', json={
    'email': 'admin@school.edu',
    'password': 'admin123'
})
token = response.json()['token']

# Get users
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:5000/api/v1/users', headers=headers)
users = response.json()['users']
```

### Using JavaScript (Fetch)

```javascript
// Login
const response = await fetch('http://localhost:5000/api/v1/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'admin@school.edu',
    password: 'admin123'
  })
});
const {token} = await response.json();

// Get users
const usersResponse = await fetch('http://localhost:5000/api/v1/users', {
  headers: {'Authorization': `Bearer ${token}`}
});
const {users} = await usersResponse.json();
```

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting for production use.

## CORS

CORS is not configured by default. Add CORS headers if accessing from a different domain.
