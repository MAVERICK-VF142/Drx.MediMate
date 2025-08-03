from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers
from backend.routes import user_routes, dashboard_routes, admin_routes  # ✅ add this

# Create FastAPI app
app = FastAPI(
    title="Drx.MediMate API",
    description="Backend API for Drx.MediMate",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_routes.router, prefix="/api", tags=["User Routes"])
app.include_router(dashboard_routes.router, prefix="/api", tags=["Dashboard Routes"])
app.include_router(admin_routes.router, prefix="/api", tags=["Admin Routes"])  # ✅ added

# Health check
@app.get("/")
def read_root():
    return {"message": "Drx.MediMate backend is running!"}
