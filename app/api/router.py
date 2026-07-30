# app/api/api_v1/router.py
from fastapi import APIRouter

# 1. Import the endpoint modules (or the router variables directly)
from app.api.api_v1.endpoints import products, users

# 2. Create the master router for API version 1
api_router = APIRouter()

# 3. Adopt each sub-router and attach a URL prefix + Swagger tag
api_router.include_router(
    products.router, 
    prefix="/products", 
    tags=["Products & Inventory"]
)

api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["User Management"]
)