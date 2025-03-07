# Barbershop Waitlist API

A production-ready REST API for managing a barbershop waitlist system, built with FastAPI and SQLite.

## Features

- **User Management**: Create, read, update and delete users with phone number validation
- **Appointment Scheduling**: Book appointments, cancel appointments, and view daily waitlists
- **Data Validation**: Comprehensive input validation including Brazilian phone format
- **Docker Support**: Containerized deployment for consistent environments
- **Database Migrations**: Managed through Alembic for version control
- **Testing**: Complete test suite with pytest
- **Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Standardized Response Format**: Consistent API responses with success/error handling

## API Response Format

All API endpoints follow a standardized response format:

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
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

### Response Fields
- `success`: Boolean indicating if the operation was successful
- `message`: Human-readable message describing the operation result
- `data`: The actual response data (null for error responses)
- `error`: Detailed error message (only present in error responses)

## Prerequisites

- Python 3.9+
- pip (Python package manager)
- Docker and Docker Compose (optional, for containerized deployment)
- Git

## Getting Started

### Cloning the Repository

```bash
git clone https://github.com/yourusername/barbershop-waitlist.git
cd barbershop-waitlist
```

### Option 1: Running Locally with Python

1. **Create and activate a virtual environment** (recommended):

```bash
python -m venv venv

venv\Scripts\activate
source venv/bin/activate
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Initialize the database and run migrations**:

```bash
alembic init alembic
alembic upgrade head
```

4. **Start the API server**:

```bash
# Development env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. **Access the API**:
   - API endpoints: http://localhost:8000/
   - Interactive API documentation: http://localhost:8000/docs
   - Alternative API documentation: http://localhost:8000/redoc

### Option 2: Running with Docker

The project includes a Makefile for simplified Docker operations. Here are the available commands:

```bash
make up
make down
make clean
make logs
make ps
make rebuild
make cleanup
make dev
make prod
```

#### Quick Start with Docker

1. **Start the containers**:
```bash
make dev
```

2. **Access the API**:
   - API endpoints: http://localhost:8000/
   - Interactive API documentation: http://localhost:8000/docs

3. **Stop and clean up**:
```bash
make cleanup
```

#### Development Workflow

When making changes to the code:

1. **Rebuild and restart containers**:
```bash
make rebuild
```

2. **View logs**:
```bash
make logs
```

3. **Check container status**:
```bash
make ps
```

## Database Migrations

The project uses Alembic for database migrations:

```bash
alembic revision --autogenerate -m "Updating..."
alembic upgrade head
alembic downgrade <revision_id>
alembic history
```

## Running Tests

```bash
pytest
pytest tests/test_users.py
pytest --cov=app tests/
```

## API Endpoints

### Users

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/users/` | Create a new user | `{"name": "John Doe", "phone": "+5511987654321"}` | User object |
| GET | `/users/{user_id}` | Get user details | - | User object with appointments |
| PUT | `/users/{user_id}` | Update user | `{"name": "Jane Doe", "phone": "+5511123456789"}` | Updated user object |
| DELETE | `/users/{user_id}` | Delete a user | - | Success message |

### Appointments

| Method | Endpoint | Description | Request Body / Query | Response |
|--------|----------|-------------|---------------------|----------|
| POST | `/appointments/` | Create appointment | `{"user_id": 1, "appointment_date": "2025-03-07T10:00:00"}` | Appointment object |
| GET | `/appointments/?day=2025-03-07` | Get appointments for a day | Query param: `day` (YYYY-MM-DD) | List of appointments |
| DELETE | `/appointments/{appointment_id}` | Cancel appointment | - | Updated appointment with status "canceled" |

## Project Structure

```
barbershop_waitlist/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── endpoints/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── appointments.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── tests/
│   ├── __init__.py
│   ├── test_users.py
│   ├── test_appointments.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.