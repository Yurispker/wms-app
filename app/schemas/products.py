from pydantic import BaseModel, ConfigDict, Field

# Create a product
class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50, description="SKU of the product")
    name: str =Field(..., min_length=1, max_length=100, description="Name of the product")
    description: str | None = None
    quantity: int = Field(default=0, ge=0)  # Quantity must be a non-negative integer

    # Racking location fields
    aisle: str | None = Field(default=None, examples=["Aisle 4"])
    rack: str | None = Field(default=None, examples=["Rack 02"])
    shelf: str | None = Field(default=None, examples=["Shelf B"])

# Fetch a product
class ProductResponse(ProductCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

# Schema for directly setting inventory (e.g., setting inventory to 50)
class InventoryUpdate(BaseModel):
    inventory: int = Field(ge=0, description="The new total inventory count")

# Schema for relative changes (+10 or -5)
class InventoryAdjust(BaseModel):
    amount: int = Field(description="Positive integer to restock, negative integer to reduce")

class LocationUpdate(BaseModel):
    aisle: str | None = Field(default=None, examples=["Aisle 4"])
    rack: str | None = Field(default=None, examples=["Rack 02"])
    shelf: str | None = Field(default=None, examples=["Shelf B"])