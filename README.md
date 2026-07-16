# RAG Chat Storage Microservice

A production-ready backend microservice for storing and managing RAG chatbot chat histories.

See task [Task](TASK.md).

## Features

- Session management (create, list, get, rename, favorite, delete)
- Message storage with sender, content, and optional RAG context
- API key authentication
- Rate limiting
- Pagination for sessions and messages
- Centralized logging and global error handling
- CORS configuration
- Swagger/OpenAPI documentation
- Dockerized setup with PostgreSQL and Adminer
- Health check endpoint

## Tech Stack

- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Auth:** API Key (X-API-Key header)
- **Rate Limiting:** slowapi
- **Testing:** pytest + httpx
- **Dependency Management:** uv

## Setup & Running

### Prerequisites

- Docker and Docker Compose (for the containerized setup)
- [uv](https://github.com/astral-sh/uv) (for local Python setup)

### Local Development (without Docker)

1. Install dependencies with `uv`:
   ```bash
   uv sync --all-extras
   ```

2. Copy and edit the environment file:
   ```bash
   cp .env.example .env
   ```

3. Run database migrations and start the API:
   ```bash
   uv run alembic upgrade head
   uv run uvicorn app.main:app --reload
   ```

### Quick Start (Docker)

1. Clone the repository and enter the directory:
   ```bash
   cd rag-chat-storage
   ```

2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to set your `API_KEY` and other configuration values.

3. Start the services:
   ```bash
   docker compose up api
   ```

4. Access the services:
   - API: http://localhost:5100
   - Swagger Docs: http://localhost:5100/docs
   - ReDoc: http://localhost:5100/redoc
   - Adminer (DB GUI): http://localhost:5102

### Database Migrations

Migrations run automatically on startup via `alembic upgrade head`. To create new migrations after model changes:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Running Tests

Tests run against a dedicated PostgreSQL instance (`db_test`) to stay close to production.

**With Docker (recommended):**
```bash
docker compose run --rm test
```

This starts `db_test` (port 5433, database `ragchat_test`), installs dev dependencies, and runs the full test suite — fully isolated from the main `db` service.

**Locally (requires a running PostgreSQL):**
```bash
# Start only the test database
docker compose up -d db_test

# Run tests
uv sync --all-extras && pytest -v
```

## Environment Variables

| Variable                | Default            | Description                          |
| ----------------------- | ------------------ | ------------------------------------ |
| `DB_HOST`               | `db`               | PostgreSQL host                      |
| `DB_PORT`               | `5432`             | PostgreSQL port                      |
| `DB_USER`               | `ragchat`          | Database user                        |
| `DB_PASSWORD`           | `ragchat_secret`   | Database password                    |
| `DB_NAME`               | `ragchat`          | Database name                        |
| `DATABASE_URL`          | —                  | Full connection URL (overrides above)|
| `API_KEY`               | `change-me`        | API key for auth                     |
| `RATE_LIMIT_PER_MINUTE` | `60`               | Max requests per minute              |
| `CORS_ORIGINS`          | `*`                | Comma-separated origins              |
| `LOG_LEVEL`             | `INFO`             | Logging level                        |

## API Reference

All endpoints (except `/health` and `/`) require the `X-API-Key` header.

### Health

| Method | Path       | Description         |
| ------ | ---------- | ------------------- |
| GET    | `/health`  | Health check        |
| GET    | `/`        | Service info        |

### Sessions

| Method | Path              | Description                        |
| ------ | ----------------- | ---------------------------------- |
| POST   | `/sessions`       | Create a new chat session          |
| GET    | `/sessions`       | List sessions for a user           |
| GET    | `/sessions/{id}`  | Get session details                |
| PATCH  | `/sessions/{id}`  | Rename or toggle favorite          |
| DELETE | `/sessions/{id}`  | Delete session and its messages    |

**Query parameters for `GET /sessions`:**
- `user_id` (required) - User identifier
- `page` (default: 1) - Page number
- `page_size` (default: 20, max: 100) - Items per page

### Messages

| Method | Path                                          | Description                |
| ------ | --------------------------------------------- | -------------------------- |
| POST   | `/sessions/{session_id}/messages`             | Add a message to a session |
| GET    | `/sessions/{session_id}/messages`             | Get session message history|

**Query parameters for `GET .../messages`:**
- `page` (default: 1) - Page number
- `page_size` (default: 50, max: 200) - Items per page

### Request/Response Examples

**Create Session:**
```json
POST /sessions
{"user_id": "alice", "title": "My Chat"}
```

**Add Message:**
```json
POST /sessions/{id}/messages
{"sender": "user", "content": "What is RAG?", "context": "doc1.txt, doc2.pdf"}
```

`sender` must be one of: `user`, `assistant`, `system`.

**Update Session:**
```json
PATCH /sessions/{id}
{"title": "New Name", "is_favorite": true}
```
