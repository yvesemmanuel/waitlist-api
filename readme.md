# Waitlist API

A sophisticated RESTful API for managing appointments between users and service providers with an advanced queue system that prioritizes reliable users.

## 📋 Overview

The Waitlist API provides a streamlined system for booking and managing appointments between users and service accounts. It features an intelligent queue system that automatically prioritizes users based on their reliability history.

### Core Features

- **User & Service Account Management**: Complete user and service provider account management using phone numbers as identifiers
- **Appointment Scheduling**: Book, cancel, complete, and mark no-show appointments
- **Intelligent Waitlist System**: Queue prioritization based on user reliability scores
- **Data Validation**: Comprehensive input validation with Pydantic v2
- **Standardized Response Format**: Consistent API responses with proper error handling

## 🏗️ Data Model

The API uses a simplified and intuitive data model:

1. **Users**: Regular users who can book appointments (identified by phone number)
2. **Service Accounts**: Providers that offer services (identified by phone number)
3. **Appointments**: Bookings between users and service accounts with status tracking

## ⚙️ Waitlist System

The API implements a sophisticated waitlist system with the following features:

- **One Appointment Per Day**: Users can only have one active appointment per day with any service account
- **Reliability Penalty System**: Users with a history of cancellations or no-shows receive a higher penalty value
- **Priority Ranking**: The waitlist for each service account is automatically ranked by:
  1. User reliability (lower penalty = higher priority)
  2. Appointment creation time (earlier = higher priority)
- **No-Show Impact**: No-shows have a greater impact on future penalties than cancellations

### User Reliability and Penalties

The system calculates a reliability penalty for each user when they create a new appointment:

- New users start with a penalty of 0.0 (perfect reliability)
- The penalty is based on the user's appointment history with that specific service account:
  - Cancellations and no-shows increase the penalty score
  - Weights are customizable by each service account
  - Recent behavior has more impact than older history (exponential decay)
- Lower penalties get higher priority in the waitlist

#### Customizable Penalty System

Service accounts can customize how penalties are calculated:

- **Enable/Disable Penalties**: Service accounts can opt out of the penalty system entirely
- **Cancellation Weight**: How much a cancellation impacts the user's penalty (default: 1.0)
- **No-Show Weight**: How much a no-show impacts the user's penalty (default: 2.0)

## 🔄 Appointment Status Flow

Appointments follow this status progression:

1. **ACTIVE**: Initial state when created
2. **CANCELED**: When explicitly canceled by user or staff
3. **COMPLETED**: When service has been provided
4. **NO_SHOW**: When user doesn't attend the appointment

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Supported database (PostgreSQL recommended)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/waitlist-api.git
cd waitlist-api
```

2. **Create and activate a virtual environment**:
```bash
python -m venv venv

# Windows
venv\Scripts\activate
# Unix/Mac
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
Create a `.env` file with your database connection string and other settings:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/waitlist
SECRET_KEY=your_secret_key
```

5. **Start the API server**:
```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔌 API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/` | Create a new regular user |
| GET | `/users/` | List all users |
| GET | `/users/{phone}` | Get details for a specific user |
| PUT | `/users/{phone}` | Update a user |
| DELETE | `/users/{phone}` | Delete a user |

### Service Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/service-accounts/` | Create a new service account |
| GET | `/service-accounts/` | List all service accounts |
| GET | `/service-accounts/{phone}` | Get details for a specific service account |
| PUT | `/service-accounts/{phone}` | Update a service account |
| DELETE | `/service-accounts/{phone}` | Delete a service account |

### Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/appointments/` | Create a new appointment |
| GET | `/appointments/` | Get appointments for a service account as a prioritized queue |
| GET | `/appointments/{id}` | Get details for a specific appointment |
| DELETE | `/appointments/{id}` | Cancel an appointment |
| PUT | `/appointments/{id}/complete` | Mark an appointment as completed |
| PUT | `/appointments/{id}/no-show` | Mark a user as no-show |

## 📊 API Response Format

All API endpoints follow a standardized response format:

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Response data here
    }
}
```

### Error Response
```json
{
    "detail": "..." // Error message
}
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_user.py
pytest tests/test_service_account.py
pytest tests/test_appointment.py

# Run with verbose output
pytest -vs tests/test_appointment.py
```

## 📋 Example API Requests

### Creating a User

```bash
curl -X 'POST' \
  'http://localhost:8000/users/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "John Doe",
  "phone": "+12025550178",
  "email": "john@example.com"
}'
```

### Creating a Service Account

```bash
curl -X 'POST' \
  'http://localhost:8000/service-accounts/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Downtown Spa",
  "phone": "+12025550179",
  "description": "Relaxing spa treatments",
  "enable_cancellation_scoring": true,
  "cancellation_weight": 1.0,
  "no_show_weight": 2.0
}'
```

### Creating an Appointment

```bash
curl -X 'POST' \
  'http://localhost:8000/appointments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_phone": "+12025550178",
  "service_account_phone": "+12025550179",
  "appointment_date": "2025-03-15T10:00:00Z",
  "duration_minutes": 60,
  "notes": "First-time customer"
}'
```

### Retrieving Appointment Queue

```bash
curl -X 'GET' \
  'http://localhost:8000/appointments/?service_account_phone=+12025550179&day=2025-03-15' \
  -H 'accept: application/json'
```

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.