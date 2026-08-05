from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.orders import Order, OrderItem
from app.models.products import Product
from app.schemas.orders import OrderCreate, OrderResponse
from app.schemas.enums import UserRole
from app.security import RequireRole, get_current_user

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
):
    
    # Check for duplicate order number
    existing_order = db.query(Order).filter(Order.order_number == order_in.order_number).first()
    if existing_order:
        raise HTTPException(
            status_code= 409,
            detail=f"Order number '{order_in.order_number}' already exists."
        )

    # Validate that all referenced product IDs exist in DB
    product_ids = [item.product_id for item in order_in.items]
    existing_products = db.query(Product.id).filter(Product.id.in_(product_ids)).all()
    found_product_ids = {p.id for p in existing_products}

    for item in order_in.items:
        if item.product_id not in found_product_ids:
            raise HTTPException(
                status_code= 400,
                detail=f"Product ID {item.product_id} does not exist."
            )

    # Create parent order
    db_order = Order(
        order_number=order_in.order_number,
        customer_name=order_in.customer_name,
        status="pending"
    )
    db.add(db_order)
    db.flush()  # Generates db_order.id before committing

    # Create child order items
    for item in order_in.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            quantity_picked=0
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    return db_order


@router.get("/", response_model=list[OrderResponse])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all orders in the system."""
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders


# Get order by order number
@router.get("/number/{order_number}", response_model=OrderResponse)
def get_order_by_number(
    order_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(
            status_code= 404,
            detail=f"Order number '{order_number}' not found."
        )
    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code= 404,
            detail=f"Order with ID {order_id} not found."
        )
    return order