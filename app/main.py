from fastapi import FastAPI
from app.routers import organizations, buildings, activities

app = FastAPI(
    title="Organizations Directory API",
    description="REST API for organizations, buildings and activities",
    version="1.0.0"
)

app.include_router(organizations.router)
app.include_router(buildings.router)
app.include_router(activities.router)

@app.get("/")
def root():
    return {"message": "Organizations Directory API. Go to /docs for documentation"}