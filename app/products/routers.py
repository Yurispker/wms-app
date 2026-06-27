from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.products.models import Product
from app.products.schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

# Error 400 (Duplicate SKU) response example added to the endpoint documentation
@router.post("/", response_model=ProductCreate, responses={400: 
    {"description": "Bad request - Duplicate SKU detected",
     "content":
        {"application/json": {"example": {"detail": "Product with SKU '12345' already exists."}
                }
            }
        }
    }
)


def create_product(product: ProductCreate, db: Session = Depends(get_db)):

    # Check if a product with the same SKU already exists in the database
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(status_code=400, detail=f"Product with SKU '{product.sku}' already exists.")
    
    db_product = Product(sku=product.sku, name=product.name, description=product.description)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# GET all products
@router.get("/", response_model=list[ProductResponse])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

# GET a product by ID
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return product