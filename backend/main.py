"""
AI Trip Planner Agent — FastAPI application entry point.

Run locally:
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import DATABASE_URL, init_db
from routers import places, trips, weather
from utils.helpers import get_env

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("trip_planner")

# ---------------------------------------------------------------------------
# Rate limiting (slowapi) — optional; graceful no-op if not installed
# ---------------------------------------------------------------------------
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.util import get_remote_address
    from utils.helpers import get_env as _get_env

    _rate_limit = _get_env("PLAN_TRIP_RATE_LIMIT", "10/minute")
    limiter = Limiter(key_func=get_remote_address, default_limits=[_rate_limit])
    _RATE_LIMITING = True
    logger.info("Rate limiting enabled: %s per IP", _rate_limit)
except ImportError:
    limiter = None  # type: ignore[assignment]
    _RATE_LIMITING = False
    logger.warning("slowapi not installed — rate limiting disabled")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create database tables on startup."""
    db_engine = "PostgreSQL" if "postgresql" in DATABASE_URL else "SQLite"
    logger.info("Initializing database… (%s)", db_engine)
    init_db()
    logger.info("AI Trip Planner API ready")
    yield
    logger.info("Shutting down AI Trip Planner API")


app = FastAPI(
    title="AI Trip Planner Agent",
    description="Production API for personalized AI-powered travel planning.",
    version="1.1.0",
    lifespan=lifespan,
)

# Wire up rate limiter middleware and error handler
if _RATE_LIMITING and limiter is not None:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

# CORS — allow local Vite + production Vercel origins
cors_origins_raw = get_env(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
cors_origins = [o.strip() for o in (cors_origins_raw or "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    """Catch-all to avoid leaking stack traces in production responses."""
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


@app.get("/", tags=["health"])
def root():
    return {
        "name": "AI Trip Planner Agent",
        "version": "1.1.0",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health():
    db_type = "PostgreSQL" if "postgresql" in DATABASE_URL else "SQLite (Ephemeral on Vercel)" if "/tmp" in DATABASE_URL else "SQLite"
    return {
        "status": "healthy",
        "database": db_type
    }


# Apply rate limiter to plan-trip route
if _RATE_LIMITING and limiter is not None:
    trips.router.routes  # ensure router is loaded
    for route in trips.router.routes:
        if hasattr(route, "path") and route.path == "/plan-trip":
            limiter.limit(_rate_limit)(route.endpoint)

app.include_router(trips.router)
app.include_router(weather.router)
app.include_router(places.router)
