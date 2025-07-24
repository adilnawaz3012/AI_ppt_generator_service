import os
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from arq import create_pool
from arq.connections import RedisSettings

from app.api.v1.endpoints import presentations
from app.core.config import settings, logger
from app.core.custom_exceptions import PresentationNotFoundException

# Create the output directory if it doesn't exist
os.makedirs("generated_presentations", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_cache = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis_cache), prefix="fastapi-cache")
    logger.info("FastAPI Cache initialized.")
    
    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    logger.info("ARQ Redis pool initialized.")
    
    yield
    
    await FastAPICache.clear()
    await app.state.arq_pool.close()
    logger.info("Connections closed.")

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title=settings.APP_NAME,
    version="4.0.0-arq",
    description="A scalable backend service to generate presentations using ARQ.",
    lifespan=lifespan
)

app.state.limiter = limiter
# --- Exception Handlers ---
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(PresentationNotFoundException)
async def presentation_not_found_handler(request: Request, exc: PresentationNotFoundException):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error for request {request.method} {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request body", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled exception for request {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )

# API Routers
app.include_router(
    presentations.router,
    prefix=settings.API_V1_STR + "/presentations",
    tags=["Presentations"],
)

@app.get("/", tags=["Root"])
def read_root():
    """
        For health status check for the service
    """
    return {"status": "ok", "message": f"Welcome to {settings.APP_NAME}"}