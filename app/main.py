from fastapi import FastAPI
from app.database import engine, Base
from app.products.models import Product
from app.products.routers import router as product_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WMS Backend",
    description="A Warehouse Management System Backend API to manage inventory, orders, and shipments.",
    version="0.0.1",
)

app.include_router(product_router)

@app.get("/")
def read_root():
    return{
        "status": "healthy",
        "system": "WMS Backend API",
        "message": "Welcome to the WMS Backend API. Use the /docs endpoint to explore the available API endpoints and their documentation."
    }