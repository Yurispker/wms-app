from pydantic import BaseModel

# Create a product
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str | None = None

# Fetch a product
class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True
