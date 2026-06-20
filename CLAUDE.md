# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WizMap is a scalable interactive visualization tool for exploring large machine learning embeddings. This is a full-stack application with:

- **Frontend**: Svelte + TypeScript SPA with D3.js visualizations
- **Backend**: FastAPI service with PostgreSQL, Redis, MinIO, and Celery
- **Deployment**: Docker-based with development and production configurations
- **Core Feature**: Multi-resolution embedding summarization and map-like interaction

## Architecture

### Frontend Structure
```
frontend/
├── src/
│   ├── components/        # Svelte components organized by feature
│   │   ├── embedding/     # Core embedding visualization (D3.js, WebGL)
│   │   ├── mapview/       # Main map interface with zoom/pan
│   │   ├── dataset-upload/ # File upload interface
│   │   ├── search-panel/  # Search functionality
│   │   └── floating-window/ # Detail inspection
│   ├── stores.ts          # Svelte stores for state management
│   ├── types/             # TypeScript type definitions
│   └── utils/             # Helper functions
├── vite.config.ts        # Vite build configuration with multiple modes
└── package.json
```

### Backend Structure
```
backend/
├── app/
│   ├── api/v1/           # FastAPI route handlers
│   ├── core/             # Database, config, security
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic schemas for validation
│   ├── services/        # Business logic (MinIO, processing)
│   └── workers/         # Celery background tasks
├── requirements.txt
└── Dockerfile
```

### Data Flow
1. **Upload**: User uploads file → FastAPI validates → MinIO storage → PostgreSQL metadata
2. **Processing**: Celery worker picks up task → generates embeddings → creates WizMap summaries
3. **Visualization**: Frontend fetches processed data → D3.js rendering → interactive map

## Development Commands

### Frontend Development
```bash
# Start Vite dev server with hot reload
cd frontend
npm run dev                    # Runs on port 3000

# Build for different targets
npm run build                  # Production build to dist/
npm run build:github          # GitHub Pages build
npm run build:vercel          # Vercel build
npm run build:notebook        # Jupyter notebook widget build

# Type checking
npm run check                 # Svelte type checking
```

### Backend Development
```bash
# Start backend with hot reload
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest                        # Run all tests
pytest tests/test_api.py      # Run specific test file
pytest -v                     # Verbose output

# Database migrations
alembic upgrade head         # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration
```

### Docker Environment
```bash
# Start development environment with hot reload
./bin/start_dev.sh            # Frontend:3002, Backend:8080

# Start production environment (no HMR, more stable)
docker compose -f docker-compose.yml up -d    # Frontend:3001

# Start stable environment (recommended for debugging WebSocket issues)
./bin/start_stable.sh

# Service management
./bin/stop                    # Stop all services
./bin/restart                 # Restart services
./bin/status                  # Check service status
./bin/logs                    # View real-time logs

# Rebuild after major changes
docker compose build --no-cache frontend    # Rebuild frontend
docker compose build --no-cache backend     # Rebuild backend
```

## Key Architectural Patterns

### Vite Multi-Mode Build System
The `vite.config.ts` uses conditional configuration based on command and mode:
- **Development**: HMR with WebSocket configuration for Docker compatibility
- **Production**: Optimized build with code splitting
- **GitHub**: Custom base path for GitHub Pages deployment
- **Notebook**: IIFE bundle for Jupyter integration

**Critical**: When developing with Docker, the HMR configuration requires `clientPort: 3002` (external port) instead of the internal container port 3000.

### FastAPI Service Layer Pattern
Backend follows a clean service layer pattern:
- **API routes** (`api/v1/`): Handle HTTP requests, validation, responses
- **Services** (`services/`): Business logic, external API calls
- **Models** (`models/`): Database schema with SQLAlchemy
- **Schemas** (`schemas/`): Pydantic models for request/response validation

### Async File Handling
When working with FastAPI's `UploadFile`, always use `await`:
```python
# Correct
content = await file.read()

# Incorrect - will cause "a bytes-like object is required, not 'coroutine'" error
content = file.read()
```

### Svelte Component Communication
- **Parent to Child**: Props (`export let prop = value`)
- **Child to Parent**: Events (`dispatch('event', detail)`)
- **Global State**: Svelte stores (`stores.ts`) with `writable()`
- **URL-based State**: URL search params drive dataset selection

### D3.js Integration Pattern
D3.js is imported as a module (`utils/d3-import.ts`) to avoid SSR issues. Components use a lifecycle pattern:
1. `onMount`: Initialize D3 selections, set up scales
2. Reactive statements: Update visualizations when data changes
3. `onDestroy`: Clean up event listeners, timers

## Critical Files

### Frontend
- `frontend/vite.config.ts`: Build configuration, HMR setup
- `frontend/src/stores.ts`: Global state management
- `frontend/App.svelte`: Main app routing based on URL params
- `frontend/src/components/mapview/MapView.svelte`: Core visualization

### Backend
- `backend/app/main.py`: FastAPI app initialization, CORS, route registration
- `backend/app/core/config.py`: Environment variables, settings
- `backend/app/services/minio_service.py`: Object storage operations
- `backend/app/services/processing_service.py`: Embedding generation, WizMap summarization

### Docker
- `docker-compose.yml`: Production services (Nginx on :3001, backend on :8080)
- `docker-compose.dev.yml`: Development override (Vite HMR on :3002)
- `Dockerfile`: Multi-stage production build (Node build → Nginx serve)
- `Dockerfile.dev`: Development image with volume mounts

## Development Workflow

### Making Frontend Changes
1. Edit files in `frontend/src/`
2. Vite HMR auto-refreshes (dev mode on :3002)
3. For production builds: `npm run build` then restart containers

### Making Backend Changes
1. Edit files in `backend/app/`
2. Uvicorn --reload auto-restarts (dev mode)
3. For production: rebuild backend container

### Adding New API Endpoints
1. Create Pydantic schemas in `backend/app/schemas/`
2. Add route handler in `backend/app/api/v1/`
3. Register router in `backend/app/main.py`
4. Update `backend/requirements.txt` if adding dependencies

### Debugging WebSocket Issues
If frontend flickers with WebSocket errors in dev mode:
1. Use stable production environment: `docker compose -f docker-compose.yml up -d`
2. Or ensure HMR config uses external port: `clientPort: 3002`

## Testing

### Frontend Testing
```bash
cd frontend
npm run check                 # Type checking
npm run build                 # Ensures build succeeds
```

### Backend Testing
```bash
cd backend
pytest                        # Run all tests
pytest tests/test_api.py      # Test API endpoints
pytest -v                     # Verbose output
```

### Integration Testing
```bash
# Test file upload functionality
python test_upload.py

# Test backend health
curl http://localhost:8080/health
curl http://localhost:8080/docs  # API documentation
```

## Environment Variables

Key environment variables (see `backend/.env.example`):
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis for Celery broker
- `MINIO_ENDPOINT`: MinIO for object storage
- `MINIO_BUCKET`: Upload storage bucket name
- `CELERY_BROKER_URL`: Redis connection for Celery

## Common Issues

### Port Conflicts
- Frontend dev: 3002 (Vite), 3001 (Nginx production)
- Backend: 8080
- MinIO: 9100 (API), 9101 (console)

### Build Failures
- Clear node_modules: `rm -rf frontend/node_modules && npm install`
- Rebuild Docker: `docker compose build --no-cache <service>`

### Import Errors in Backend
Processing service imports from `notebook-widget/wizmap` module. Ensure this path is correct and dependencies are installed.

### Hot Reload Not Working
- Ensure volume mounts are correct in docker-compose.dev.yml
- Check file permissions on mounted volumes
- Verify `--reload` flag in Uvicorn command