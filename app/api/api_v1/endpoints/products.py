from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.products import Product
from app.schemas.products import InventoryAdjust, InventoryUpdate, ProductCreate, ProductResponse, LocationUpdate
from app.schemas.enums import UserRole
from app.security import RequireRole, get_current_user

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,responses={400: 
    {"description": "Bad request - Duplicate SKU detected",
     "content":
        {"application/json": {"example": {"detail": "Product with SKU '12345' already exists."}
                }
            }
        }
    }
)


def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
    ):

    # Check if a product with the same SKU already exists in the database
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(status_code= 400, detail=f"Product with SKU '{product.sku}' already exists.")
    
    db_product = Product(sku=product.sku, 
                         name=product.name, 
                         description=product.description, 
                         quantity=product.quantity, 
                         aisle=product.aisle,
                         rack=product.rack,
                         shelf=product.shelf)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# Get all products
@router.get("/", response_model=list[ProductResponse])
def get_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
    ):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

# Get a product by SKU
@router.get("/sku/{sku}", response_model=ProductResponse)
def get_product_by_sku(sku: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product with SKU '{sku}' not found")
    return product

# Get a product by ID
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return product

# Set inventory to an exact value
@router.patch("/{sku}/inventory", response_model=ProductResponse)
def set_product_inventory(
    sku: str, 
    update_data: InventoryUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
):
    # Directly set the inventory count for a product
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(
            status_code= 404, detail=f"Product with SKU {sku} not found"
        )
    
    product.quantity = update_data.quantity
    db.commit()
    db.refresh(product)
    print(f"Inventory for SKU '{sku}' adjusted by {update_data.quantity}. New quantity: {product.quantity}. Adjusted by user: {current_user.get('username')}")
    return product


# Restock or deduct inventory (+ / -)
@router.post("/{sku}/inventory/adjust", response_model=ProductResponse)
def adjust_product_inventory(
    sku: str, 
    adjustment: InventoryAdjust, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
):

    """Adjust inventory by a relative amount.
    - Positive amount (+10): Restocks inventory.
    - Negative amount (-5): Deducts inventory."""

    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(
            status_code = 404, detail=f"Product with SKU {sku} not found"
        )

    new_quantity = product.quantity + adjustment.amount

    # Safety check: prevent negative stock
    if new_quantity < 0:
        raise HTTPException(
            status_code= 400, detail=f"Insufficient quantity. Current: {product.quantity}, requested reduction: {abs(adjustment.amount)}"
        )

    product.quantity = new_quantity
    db.commit()
    db.refresh(product)

    print(f"Inventory for SKU '{sku}' adjusted by {adjustment.amount}. New quantity: {product.quantity}. Adjusted by user: {current_user.get('username')}")
    return product

@router.patch("/{sku}/location", response_model=ProductResponse)
def update_product_location(
    sku: str, 
    location_data: LocationUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
):
    # Update where a product is physically stored in the warehouse
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(
            status_code = 404, detail=f"Product with SKU '{sku}' not found"
        )

    # Only update fields that were sent in the request
    if location_data.aisle is not None:
        product.aisle = location_data.aisle
    if location_data.rack is not None:
        product.rack = location_data.rack
    if location_data.shelf is not None:
        product.shelf = location_data.shelf

    db.commit()
    db.refresh(product)

    print(f"Location for SKU '{sku}' updated to Aisle: {product.aisle}, Rack: {product.rack}, Shelf: {product.shelf}. Updated by user: {current_user.get('username')}")

    return product