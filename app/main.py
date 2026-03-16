"""
MediScribe AI — Application Entry Point.

FastAPI application factory with lifecycle management.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.database import init_db

# ── Logging ──────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("🚀 Iniciando MediScribe AI...")
    await init_db()
    logger.info("✅ Base de datos inicializada.")
    yield
    logger.info("👋 MediScribe AI detenido.")


# ── App Factory ──────────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware (Hardened) ──────────────────────────────

# [SOC-NOTE]: Restricting origins to prevent unauthorized Cross-Origin requests.
# In production, this should be a list of trusted domains.
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS.split(",") if hasattr(settings, "ALLOWED_ORIGINS") else ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # [SOC-NOTE]: Only allowing necessary methods.
    allow_headers=["Content-Type", "Authorization"],
)

# ── Security Headers Middleware ──────────────────────────────

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# ── Register Routes ──────────────────────────────────────────

app.include_router(router)


# ── Root Redirect ────────────────────────────────────────────


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API docs."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")
