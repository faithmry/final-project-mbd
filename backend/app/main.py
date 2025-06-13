# C:\Users\Faith\Downloads\myits-collab\backend\app\main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- ADD THIS IMPORT
from app.db.database import engine, Base

# Import all your models files so SQLAlchemy knows about them
from app.models import user
from app.models import projects # Changed from 'project' to 'projects' as per your file structure
from app.models import applications # Changed from 'application' to 'applications'

# Import your routers
from app.routers import auth
from app.routers import projects # Changed from 'project' to 'projects'
from app.routers import users
from app.routers import applications # Changed from 'application' to 'applications'

# Import the OAuth2PasswordBearer scheme
from app.dependencies import oauth2_scheme


# This line attempts to create all tables defined with Base.
# Only run this once to create tables or if you explicitly want to recreate them.
# In a real app, you'd use Alembic for migrations.
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app and explicitly define the security scheme for OpenAPI
app = FastAPI(
    security=[{"BearerAuth": []}],
    openapi_extra={
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT Authorization header using the Bearer scheme. Enter your token in the format: **Bearer &lt;token>**"
                }
            }
        }
    }
)

# Configure CORS middleware <--- ADD THIS BLOCK
origins = [
    "http://localhost",        # Default for many local dev setups
    "http://localhost:8001",   # Your frontend server (Python http.server or live-server)
    "http://127.0.0.1",
    "http://127.0.0.1:8000",   # Your backend itself
    # For file:// origins when opening directly in browser, though serving via http.server is better:
    # "file://",
    # "null"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # List of allowed origins
    allow_credentials=True,      # Allow cookies to be included in cross-origin HTTP requests
    allow_methods=["*"],         # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],         # Allow all headers
)

# Include your routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(users.router)
app.include_router(applications.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to MyITS Collab Backend!"}