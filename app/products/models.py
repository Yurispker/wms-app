from sqlalchemy import Column, Integer, String
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    inventory = Column(Integer, default=0, nullable=False)

# Racking locations
    aisle = Column(String, nullable=True)
    rack = Column(String, nullable=True)
    shelf = Column(String, nullable=True)

