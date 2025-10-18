from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, classes, bookings
from app.middleware.logging import LoggingMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from markupsafe import Markup
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    await connect_to_mongo()
    logger.info("Application startup complete")

    yield

    logger.info("Shutting down application...")
    await close_mongo_connection()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    description=Markup(
        """
<b>Features</b><br><br>

<ul>
<li><b>User Authentication</b> – JWT-based authentication with secure password hashing</li>
<li><b>Class Management</b> – Create and view fitness classes</li>
<li><b>Booking System</b> – Book classes with race condition prevention</li>
<li><b>Timezone Support</b> – All times managed in IST (Indian Standard Time)</li>
</ul>

<h3>Authentication</h3>
<ol>
<li>Register using <code>/api/v1/auth/signup</code></li>
<li>Login using <code>/api/v1/auth/login</code> to get JWT token</li>
<li>Include token in Authorization header: <code>Bearer &lt;your_token&gt;</code></li>
</ol>
"""
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(bookings.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", tags=["Health Check"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Fitness Booking API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "database": "connected",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )


from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for op in path.values():
            op.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
