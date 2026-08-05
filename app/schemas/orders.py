from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="Database ID of the product")
    quantity: int = Field(..., gt=0, description="Quantity to pick")


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    quantity_picked: int

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=50, description="Unique external order identifier")
    customer_name: str = Field(..., min_length=1, max_length=100)
    items: list[OrderItemCreate] = Field(..., min_length=1, description="List of items in this order")


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    status: str
    created_at: datetime
    items: list[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)