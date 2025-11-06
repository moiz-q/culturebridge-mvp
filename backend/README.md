# CultureBridge Backend

This is the backend API for CultureBridge, built with FastAPI, SQLAlchemy, and PostgreSQL.

## Getting Started

### Prerequisites

- Python 3.11+ installed
- PostgreSQL database
- Redis server

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the environment variables:
```bash
cp .env.example .env
```

4. Update the `.env` file with your configuration.

### Database Setup

1. Create the database:
```bash
createdb culturebridge
```

2. Run migrations:
```bash
alembic upgrade head
```

### Development

Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── routers/         # API route handlers
│   ├── services/        # Business logic
│   ├── repositories/    # Data access layer
│   ├── middleware/      # Custom middleware
│   ├── utils/          # Utility functions
│   ├── config.py       # Configuration
│   ├── database.py     # Database connection
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── tests/              # Test suite
└── requirements.txt    # Python dependencies
```

## Technologies

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **PostgreSQL**: Relational database
- **Redis**: Caching layer
- **Pydantic**: Data validation
- **JWT**: Authentication
- **Stripe**: Payment processing
- **OpenAI**: AI matching engine
- **AWS S3**: File storage
