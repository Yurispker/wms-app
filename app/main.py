from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models.products import Product
from app.models.users import User
from app.api.api_v1.router import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WMS Backend",
    description="A Warehouse Management System Backend API to manage inventory, orders, and shipments.",
    version="0.1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")