from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.database import engine, Base
from app.models.products import Product
from app.models.users import User
from app.api.router import api_router
from app.seed import reset_and_seed

Base.metadata.create_all(bind=engine)

reset_and_seed()  # Reset and seed the database on startup

app = FastAPI(
    title="WMS Backend",
    description="A Warehouse Management System Backend API to manage inventory, orders, and shipments.",
    version="0.1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")