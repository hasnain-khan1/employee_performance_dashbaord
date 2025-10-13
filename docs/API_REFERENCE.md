# API Reference

This document provides comprehensive information about the EPMS API endpoints.

## Base URL
```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

### Getting Tokens

**Login**
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "employee_id": "EMP000001",
    "username": "john.doe",
    "email": "john.doe@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "employee",
    "status": "active"
  }
}
```

**Refresh Token**
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

## Endpoints

### Authentication (`/api/auth/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/login/` | Login user | No |
| POST | `/register/` | Register new user | No |
| POST | `/logout/` | Logout user | Yes |
| POST | `/token/refresh/` | Refresh access token | No |
| GET | `/profile/` | Get user profile | Yes |
| PATCH | `/profile/` | Update user profile | Yes |
| POST | `/change-password/` | Change password | Yes |
| POST | `/reset-password/` | Request password reset | No |
| GET | `/users/` | List users | Yes |
| GET | `/users/{id}/` | Get user details | Yes |

### Goals (`/api/goals/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List goals | Yes |
| POST | `/` | Create goal | Yes |
| GET | `/{id}/` | Get goal details | Yes |
| PATCH | `/{id}/` | Update goal | Yes |
| DELETE | `/{id}/` | Delete goal | Yes |
| POST | `/{id}/approve/` | Approve goal | Yes (Manager) |
| POST | `/{id}/reject/` | Reject goal | Yes (Manager) |
| GET | `/{id}/updates/` | Get goal updates | Yes |
| POST | `/{id}/updates/` | Create goal update | Yes |
| GET | `/categories/` | List goal categories | Yes |
| POST | `/categories/` | Create category | Yes (HR/Admin) |

### Review Cycles (`/api/cycles/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List cycles | Yes |
| POST | `/` | Create cycle | Yes (HR/Admin) |
| GET | `/{id}/` | Get cycle details | Yes |
| PATCH | `/{id}/` | Update cycle | Yes (HR/Admin) |
| DELETE | `/{id}/` | Delete cycle | Yes (HR/Admin) |
| POST | `/{id}/start/` | Start cycle | Yes (HR/Admin) |
| POST | `/{id}/complete/` | Complete cycle | Yes (HR/Admin) |
| GET | `/{id}/participants/` | Get cycle participants | Yes |
| POST | `/{id}/participants/` | Add participant | Yes (HR/Admin) |
| GET | `/templates/` | List cycle templates | Yes |
| POST | `/templates/` | Create template | Yes (HR/Admin) |

### Feedback (`/api/feedback/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List feedback requests | Yes |
| POST | `/` | Create feedback request | Yes |
| GET | `/{id}/` | Get feedback request | Yes |
| PATCH | `/{id}/` | Update feedback request | Yes |
| DELETE | `/{id}/` | Delete feedback request | Yes |
| POST | `/{id}/accept/` | Accept feedback request | Yes |
| POST | `/{id}/decline/` | Decline feedback request | Yes |
| GET | `/{id}/response/` | Get feedback response | Yes |
| POST | `/{id}/response/` | Submit feedback response | Yes |
| GET | `/templates/` | List feedback templates | Yes |

### Reviews (`/api/reviews/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List reviews | Yes |
| POST | `/` | Create review | Yes |
| GET | `/{id}/` | Get review details | Yes |
| PATCH | `/{id}/` | Update review | Yes |
| DELETE | `/{id}/` | Delete review | Yes |
| POST | `/{id}/submit/` | Submit review | Yes |
| POST | `/{id}/approve/` | Approve review | Yes (Manager/HR) |
| POST | `/{id}/reject/` | Reject review | Yes (Manager/HR) |
| GET | `/{id}/sections/` | Get review sections | Yes |
| POST | `/{id}/sections/` | Create review section | Yes |
| GET | `/templates/` | List review templates | Yes |

### Analytics (`/api/analytics/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/reports/` | List reports | Yes (HR/Admin) |
| POST | `/reports/` | Create report | Yes (HR/Admin) |
| GET | `/reports/{id}/` | Get report details | Yes (HR/Admin) |
| GET | `/reports/{id}/download/` | Download report | Yes (HR/Admin) |
| GET | `/dashboards/` | List dashboards | Yes (HR/Admin) |
| POST | `/dashboards/` | Create dashboard | Yes (HR/Admin) |
| GET | `/metrics/` | List metrics | Yes (HR/Admin) |
| GET | `/performance/` | Get performance data | Yes (HR/Admin) |
| GET | `/goals/` | Get goals analytics | Yes (HR/Admin) |

### Organization (`/api/org/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/departments/` | List departments | Yes |
| POST | `/departments/` | Create department | Yes (HR/Admin) |
| GET | `/departments/{id}/` | Get department details | Yes |
| PATCH | `/departments/{id}/` | Update department | Yes (HR/Admin) |
| DELETE | `/departments/{id}/` | Delete department | Yes (HR/Admin) |
| GET | `/teams/` | List teams | Yes |
| POST | `/teams/` | Create team | Yes (Manager/HR) |
| GET | `/teams/{id}/` | Get team details | Yes |
| GET | `/positions/` | List positions | Yes |
| POST | `/positions/` | Create position | Yes (HR/Admin) |

## Request/Response Examples

### Create Goal

**Request**
```http
POST /api/goals/
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Improve Sales Performance",
  "description": "Increase sales by 20% this quarter",
  "goal_type": "performance",
  "priority": "high",
  "metric": "Sales Revenue",
  "target_value": 100000,
  "start_date": "2024-01-01",
  "target_date": "2024-03-31",
  "weight": 25,
  "specific": "Increase quarterly sales revenue by 20%",
  "measurable": "Track monthly sales reports and revenue",
  "achievable": "Based on current market conditions and team capacity",
  "relevant": "Aligns with company growth objectives",
  "time_bound": "Complete by end of Q1 2024"
}
```

**Response**
```json
{
  "id": 1,
  "title": "Improve Sales Performance",
  "description": "Increase sales by 20% this quarter",
  "goal_type": "performance",
  "priority": "high",
  "status": "draft",
  "progress_percentage": 0,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Create Feedback Request

**Request**
```http
POST /api/feedback/
Content-Type: application/json
Authorization: Bearer <token>

{
  "recipient": 2,
  "cycle": 1,
  "message": "Please provide feedback on my recent project work"
}
```

**Response**
```json
{
  "id": 1,
  "requester": 1,
  "recipient": 2,
  "cycle": 1,
  "status": "pending",
  "message": "Please provide feedback on my recent project work",
  "due_date": "2024-01-15T23:59:59Z",
  "created_at": "2024-01-01T10:00:00Z"
}
```

## Error Responses

### Validation Error (400)
```json
{
  "field_name": ["This field is required."],
  "another_field": ["This field must be a valid email."]
}
```

### Authentication Error (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Permission Error (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Not Found (404)
```json
{
  "detail": "Not found."
}
```

## Pagination

List endpoints support pagination:

**Request**
```http
GET /api/goals/?page=2&page_size=20
```

**Response**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/goals/?page=3",
  "previous": "http://localhost:8000/api/goals/?page=1",
  "results": [...]
}
```

## Filtering and Searching

Many endpoints support filtering and searching:

```http
GET /api/goals/?status=in_progress&priority=high&search=sales
GET /api/users/?role=employee&department=1
GET /api/cycles/?is_active=true
```

## Rate Limiting

API requests are rate limited:
- General API: 10 requests per second
- Login endpoint: 5 requests per minute

## WebSocket Support

Real-time updates are available via WebSocket connections for:
- Goal progress updates
- Review status changes
- Feedback notifications
- System announcements