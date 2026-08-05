from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    status = Column(String, default="pending")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
        )
    

    # Delete items if parent order is deleted
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    quantity_picked = Column(Integer, default=0, nullable=False)

    # Relationships back to parent order and product
    order = relationship("Order", back_populates="items")
    product = relationship("Product")