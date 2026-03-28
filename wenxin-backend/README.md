# VULCA Backend API

FastAPI backend for the VULCA platform. Serves the Canvas web UI and exposes REST API endpoints for pipeline execution, gallery, and authentication.

> **Note**: This is the web backend component of the [VULCA monorepo](https://github.com/vulca-org/vulca). For the standalone Python SDK/CLI, see [`vulca/`](../vulca/) or `pip install vulca`.

## Development Setup

```bash
git clone https://github.com/vulca-org/vulca.git
cd vulca/wenxin-backend
pip install -r requirements.txt -c constraints.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8001
```

## Tech Stack

- **Framework**: FastAPI + Pydantic
- **Database**: PostgreSQL + SQLAlchemy
- **Cache**: Redis
- **Vector DB**: Qdrant
- **Task Queue**: Celery
- **AI Framework**: LangChain + Transformers

## Getting Started

### 1. Environment Setup

```bash
cd wenxin-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env to configure database etc.
```

### 2. Start Base Services

```bash
docker-compose up -d  # PostgreSQL, Redis, Qdrant
```

### 3. Database Migration

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Start Application

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

Visit http://localhost:8001/docs for API documentation.

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login

### AI Model Management
- `GET /api/v1/models` - List models
- `GET /api/v1/models/{id}` - Model details
- `POST /api/v1/models` - Create model (admin)
- `PUT /api/v1/models/{id}` - Update model (admin)
- `DELETE /api/v1/models/{id}` - Delete model (admin)

### Evaluation System
- `POST /api/v1/evaluations/start` - Start evaluation
- `GET /api/v1/evaluations/{id}` - Evaluation status
- `GET /api/v1/evaluations/history` - Evaluation history

### Works Management
- `GET /api/v1/works` - List works
- `GET /api/v1/works/{id}` - Work details
- `GET /api/v1/works/similar` - Similar works

## Project Structure

```
wenxin-backend/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Core config
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   │   ├── ai_evaluation/  # AI evaluation service
│   │   └── langchain/       # LangChain integration
│   └── tasks/         # Celery tasks
├── alembic/           # Database migrations
├── tests/             # Test files
├── docker-compose.yml # Docker config
└── requirements.txt   # Dependencies
```

## Testing

```bash
pytest                    # Run tests
pytest --cov=app tests/   # Test coverage
```

## Deployment

Docker deployment recommended:

```bash
docker build -t vulca-backend .
docker run -d -p 8001:8001 --env-file .env vulca-backend
```

## License

Apache 2.0
