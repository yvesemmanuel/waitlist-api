# Waitlist API

A sophisticated RESTful API for managing appointments between users and service providers with an advanced queue system that prioritizes reliable users.

## 📋 Overview

The Waitlist API provides a streamlined system for booking and managing appointments between users and service accounts. It features an intelligent queue system that automatically prioritizes users based on their reliability history.

### Core Features

- **User & Service Management**: Complete user and service provider (service account) management
- **Appointment Scheduling**: Book, cancel, complete, and track appointments
- **Intelligent Waitlist System**: Queue prioritization based on user reliability
- **Data Validation**: Comprehensive input validation with Pydantic
- **Standardized Response Format**: Consistent API responses with proper error handling
- **Modern Architecture**: Built with FastAPI, SQLAlchemy, and Pydantic

## 🏗️ Data Model

The API uses a simplified and intuitive data model:

1. **Users**: Regular users who can book appointments
2. **Service Accounts**: Special type of user that provides services
3. **Appointments**: Bookings between users and service accounts

This streamlined model simplifies the previous concept that had separate entities for services and providers.

## ⚙️ Waitlist System

The API implements a sophisticated waitlist system with the following features:

- **One Appointment Per Day**: Users can only have one active appointment per day for a specific service
- **Day-Based Scheduling**: Appointments are booked for specific days, not exact times
- **Reliability Penalty System**: Users who have a history of cancellations or no-shows receive a higher penalty value
- **Priority Ranking**: The waitlist for each service is automatically ranked by:
  1. User reliability (lower penalty = higher priority)
  2. Appointment creation time (earlier = higher priority)
- **No-Show Impact**: No-shows have a greater impact on future penalties than cancellations

### User Reliability and Penalties

The system calculates a reliability penalty for each user when they create a new appointment:

- New users start with a penalty of 0.0 (perfect reliability)
- The penalty is based on the user's entire appointment history with that specific service:
  - Number of cancellations, no-shows, and successfully completed appointments
  - Cancellations and no-shows are weighted differently based on service settings
  - Completed appointments positively affect reliability
  - Weights are automatically normalized to ensure the penalty stays within 0-1 range
- Lower penalties get higher priority in the waitlist
- Penalties are calculated at appointment creation time and stay with the appointment for historical tracking

#### Penalty Calculation

The penalty is calculated using a sophisticated formula that considers both the user's complete appointment history and the recency of events:

$$\text{normalized\_cancellation\_weight} = \frac{\text{cancellation\_weight}}{\text{cancellation\_weight} + \text{no\_show\_weight}}$$

$$\text{normalized\_no\_show\_weight} = \frac{\text{no\_show\_weight}}{\text{cancellation\_weight} + \text{no\_show\_weight}}$$

$$\text{cancellation\_rate} = \frac{\text{total\_cancellations}}{\text{total\_appointments}}$$

$$\text{no\_show\_rate} = \frac{\text{total\_no\_shows}}{\text{total\_appointments}}$$

$$\text{base\_penalty} = \text{cancellation\_rate} \times \text{normalized\_cancellation\_weight} + \text{no\_show\_rate} \times \text{normalized\_no\_show\_weight}$$

$$\text{adjusted\_penalty} = \text{base\_penalty} \times (0.7 + 0.3 \times \text{recency\_penalty})$$

$$\text{reliability\_score} = \text{adjusted\_penalty} \times \text{volume\_factor}$$

Where the recency penalty is calculated using an exponential decay function that gives more weight to recent appointment behavior:

$$\text{recency\_weight} = e^{-0.023 \times \text{days\_ago}}$$

This formula provides several advantages:
- Considers both frequency and recency of cancellations and no-shows
- Applies different weights to cancellations and no-shows based on service account preferences
- Gives more weight to recent behavior through exponential decay
- Normalizes weights to ensure consistent scoring regardless of weight magnitude
- Ensures the final score stays within 0-1 range

#### Customizable Penalty System

Service accounts can customize how penalties are calculated:

- **Enable/Disable Penalties**: Service accounts can opt out of the penalty system entirely. When disabled, all users have equal priority (penalty = 0.0).
- **Cancellation Weight**: How much a cancellation impacts the user's penalty calculation (default: 1.0)
- **No-Show Weight**: How much a no-show impacts the user's penalty calculation (default: 2.0)

These weights allow service accounts to tailor the queue prioritization to their specific business needs.

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
- Docker and Docker Compose (optional, for containerized deployment)
- Git

### Installation

#### Option 1: Running Locally with Python

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

4. **Initialize the database and run migrations**:
```bash
alembic upgrade head
```

5. **Start the API server**:
```bash
# Development env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Option 2: Running with Docker

The project includes a Makefile for simplified Docker operations:

```bash
make dev      # Start in development mode
make prod     # Start in production mode
make down     # Stop containers
make cleanup  # Stop and remove containers
make logs     # View logs
make rebuild  # Rebuild and restart containers
```

### Migrating from Previous Version

If upgrading from a previous version, run the migration script:

```bash
python -m app.migrate_data
```

This will convert existing services and providers to the new service account model.

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔌 API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/` | Create a new regular user |
| POST | `/users/service-accounts` | Create a new service account |
| GET | `/users/` | List all users |
| GET | `/users/service-accounts` | List service accounts only |
| GET | `/users/{user_id}` | Get details for a specific user |
| PUT | `/users/{user_id}` | Update a user |
| DELETE | `/users/{user_id}` | Delete a user |

### Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/appointments/` | Create a new appointment |
| GET | `/appointments/` | Get appointments for a service account as a prioritized queue |
| GET | `/appointments/{appointment_id}` | Get details for a specific appointment |
| DELETE | `/appointments/{appointment_id}` | Cancel an appointment |
| PUT | `/appointments/{appointment_id}/complete` | Mark an appointment as completed |
| PUT | `/appointments/{appointment_id}/no-show` | Mark a user as no-show |

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
    "success": false,
    "message": "Operation failed",
    "error": "Detailed error message",
    "data": null
}
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_users.py
pytest tests/test_appointments.py

# Run with coverage report
pytest --cov=app tests/
```

## 📁 Project Structure

```
waitlist_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── appointments.py
├── alembic/
│   ├── versions/
│   ├── env.py
├── tests/
│   ├── __init__.py
│   ├── test_users.py
│   ├── test_appointments.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 📋 Example API Requests

### Creating a Service Account

```bash
curl -X 'POST' \
  'http://localhost:8000/users/service-accounts' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Downtown Spa",
  "phone": "+12025550178",
  "email": "info@downtownspa.com",
  "description": "Relaxing spa treatments in the heart of downtown"
}'
```

### Creating an Appointment

```bash
curl -X 'POST' \
  'http://localhost:8000/appointments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 1,
  "service_account_id": 2,
  "appointment_date": "2025-03-15",
  "duration_minutes": 60,
  "notes": "First-time customer"
}'
```

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.