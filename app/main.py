from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal
from app.exceptions import register_exception_handlers
from app.middleware.logging import logging_middleware, logger
from app.routers import sessions, messages
from app.middleware.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server — env_name=%s", settings.env_name)
    yield


app = FastAPI(
    title="RAG Chat Storage API",
    description="Microservice for storing RAG chatbot chat histories",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None if settings.env_name != "local" else "/redoc",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)

app.middleware("http")(logging_middleware)

register_exception_handlers(app)

app.include_router(sessions.router)
app.include_router(messages.router)


@app.get("/health", tags=["Health"])
def health_check():
    db_status = "unhealthy"
    db = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        logger.exception("Database health check failed")
    finally:
        if db is not None:
            db.close()

    return {"status": "healthy", "database": db_status}


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "RAG Chat Storage API",
        "version": "1.0.0",
        "docs": "/docs",
    }
