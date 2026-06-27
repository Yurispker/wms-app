from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.products.models import Product
from app.products.schemas import ProductCreate

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductCreate)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):

    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(status_code=400, detail=f"Product with SKU '{product.sku}' already exists.")
    
    db_product = Product(sku=product.sku, name=product.name, description=product.description)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
