# SwissHacks Monorepo

A monorepo containing:

- `frontend`: Next.js + React + TypeScript web application
- `backend`: Python FastAPI backend
- `scripts`: Python analytical scripts
- `docker`: Docker configuration files

## Getting Started with Docker

The easiest way to run the entire application locally is with Docker Compose:

```bash
# Build and start all services in development mode
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

Once running, you can access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- API Documentation: http://localhost:8000/api/v1/docs
- PostgreSQL Database: localhost:5432 (username: postgres, password: postgres, database: swisshacks)

## Manual Setup

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

### Scripts

```bash
cd scripts

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run a script
python analyze_data.py
```
