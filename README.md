# Moon Rover API

A FastAPI-based backend application that simulates control of a moon rover robot. The application translates commands sent from Earth into robot movements, tracks position and direction, and handles obstacle detection.

## Assumptions

### Context and Scope
For the implementation of this task, I assume the context is to implement a classical backend application with a lunar rover business context. I am not implementing software specifically for a lunar rover, since for that task I would not use Python and HTTP communication. Architectural decisions are made considering this assumption.

### Architecture Choice
Despite the small size of the project, the Clean Architecture pattern was chosen intentionally to demonstrate skills. For a real MVP, a simpler architecture would be more appropriate. Clean Architecture provides the project with increased reliability through comprehensive test coverage and ample room for application logic growth.

## Features

- **Robot Movement Control**: Execute movement commands (Forward, Backward, Left, Right turns)
- **Position Tracking**: Real-time position and direction monitoring
- **Obstacle Detection**: Prevents robot from hitting known obstacles
- **Command History**: Stores all executed commands in PostgreSQL database
- **Health Monitoring**: System health checks and status endpoints
- **API Authentication**: Secure API endpoints with key-based authentication

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.12+**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy 2.0**
- **Alembic**
- **Pydantic**

### Development Tools
- **uv**
- **Ruff**
- **pytest**
- **Docker & Docker Compose**

### Architecture
- **Clean Architecture**
- **Domain-Driven Design**
- **Dependency Injection**
- **Repository Pattern**
- **Unit of Work**

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.12+ (if running locally)
- uv package manager (recommended)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd moon-rover
   ```

2. **Set up environment variables**
   ```bash
   cp .env_example.txt .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the API**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Metrics: http://localhost:8000/metrics
   - Database: localhost:5432

### Local Development

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies**
   ```bash
   uv sync --dev
   ```

3. **Set up database**
   ```bash
   # Start PostgreSQL
   docker-compose up db -d
   
   # Run migrations
   uv run alembic upgrade head
   ```

4. **Run the application**
   ```bash
   uv run python -m app.main
   ```

5. **Run tests locally**
   ```bash
   # Run unit tests only (no database required)
   uv run pytest tests/application tests/domain tests/infrastructure
   
   # Run with coverage
   uv run pytest --cov=app tests/application tests/domain tests/infrastructure
   
   # Run integration tests (requires database)
   # First start the database
   docker compose up db -d
   ```

### Running Tests in Docker Container

**Integration tests require a running database and must be run in the container:**

```bash
# Run integration tests in container (requires database)
docker compose run --rm app uv run pytest tests/test_integration_api.py

# Run all tests in container with coverage
docker compose run --rm app uv run pytest --cov=app

# Run only unit tests in container
docker compose run --rm app uv run pytest tests/application tests/domain tests/infrastructure
```

## API Endpoints

### Health Check
```http
GET /health
```
Returns system health status and database connectivity.

### Get Current Position
```http
GET /positions
Authorization: Basic <base64_encoded_credentials>
```
Returns current robot coordinates and direction.

**Authentication**: Use Basic Auth with username `admin` and password `moon-rover-secret`

### Execute Commands
```http
POST /commands
Authorization: Basic <base64_encoded_credentials>
Content-Type: application/json

{
  "command": "FLFFFRFLB"
}
```
Executes a sequence of robot commands and returns final position.

**Authentication**: Use Basic Auth with username `admin` and password `moon-rover-secret`

#### Available Commands
- `F` - Move forward 1 step in current direction
- `B` - Move backward 1 step in current direction  
- `L` - Turn left 90°
- `R` - Turn right 90°


## Project Structure

```
moon-rover/
├── app/
│   ├── application/         # Application services
│   │   ├── auth_service.py
│   │   ├── command_service.py
│   │   ├── health_service.py
│   │   └── position_service.py
│   ├── domain/              # Domain models and business logic
│   │   ├── entities.py
│   │   ├── exceptions.py
│   │   └── services.py
│   ├── infrastructure/      # Database and external services
│   │   ├── db/              # Database configuration and models
│   │   └── repositories/    # Repository implementations
│   ├── presentation/        # API routes and schemas
│   │   ├── dependencies.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── config.py            # Application settings
│   ├── logging.py           # Logging configuration
│   └── main.py              # FastAPI application
├── config/
│   └── obstacles.json       # Obstacle configuration
├── migrations/              # Database migrations
├── tests/                   # Test suite
│   ├── application/         # Application layer tests
│   ├── domain/              # Domain layer tests
│   ├── infrastructure/      # Infrastructure layer tests
│   └── test_integration_api.py
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Docker image definition
├── entrypoint.sh           # Container entrypoint
└── pyproject.toml          # Project dependencies and configuration
```

## 🔧 Configuration

Key environment variables (see `.env_example.txt`):

**Application Settings:**
- `APP_HOST` - Application host (default: 0.0.0.0)
- `APP_PORT` - Application port (default: 8000)

**Database Settings:**
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_HOST` - Database host
- `POSTGRES_PORT` - Database port
- `ALCHEMY_ECHO` - SQLAlchemy query logging

**Robot Settings:**
- `START_POSITION_X` - Initial robot X coordinate
- `START_POSITION_Y` - Initial robot Y coordinate
- `START_DIRECTION` - Initial robot direction (NORTH/SOUTH/EAST/WEST)

**Authentication:**
- `USERNAME` - API username (default: admin)
- `PASSWORD` - API password (default: moon-rover-secret)

## License

This project is part of a technical assessment and is for demonstration purposes.