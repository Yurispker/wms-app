from pydantic import BaseModel

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str | None = None
