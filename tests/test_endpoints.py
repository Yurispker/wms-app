import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 1. Import Base and database dependency
from app.database import Base, get_db

# 2. Import models so SQLAlchemy registers metadata
from app.models.users import User, UserRole
from app.models.products import Product
from app.models.orders import Order, OrderItem

from app.security import get_password_hash
from app.main import app

# Shared in-memory SQLite database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

state = {}


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    admin_user = User(
        username="admin_test",
        email="admin@test.local",
        hashed_password=get_password_hash("AdminPass123"),
        is_active=True,
        role=UserRole.ADMIN
    )
    db.add(admin_user)
    db.commit()
    db.close()
    
    yield
    Base.metadata.drop_all(bind=engine)


# USER ENDPOINTS & AUTHENTICATION

def test_01_admin_login():
    """Authenticate as Admin to retrieve Bearer token for protected endpoints."""
    payload = {"username": "admin_test", "password": "AdminPass123"}
    response = client.post("/api/v1/users/login", data=payload)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    state["admin_headers"] = {"Authorization": f"Bearer {token}"}


def test_02_register_picker_user():
    """Admin registers a new warehouse picker."""
    payload = {
        "username": "warehouse_picker",
        "email": "picker@example.com",
        "password": "SecurePassword123",
        "role": "picker"
    }
    response = client.post("/api/v1/users/register", json=payload, headers=state["admin_headers"])
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == "warehouse_picker"
    assert "hashed_password" not in data
    state["user_id"] = data["id"]


def test_03_login_picker_user():
    """Authenticate created picker user to verify login endpoint."""
    payload = {
        "username": "warehouse_picker",
        "password": "SecurePassword123"
    }
    response = client.post("/api/v1/users/login", data=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]
    state["picker_headers"] = {"Authorization": f"Bearer {token}"}


def test_04_get_current_user_profile():
    """Fetch current user profile using Auth header."""
    response = client.get("/api/v1/users/me", headers=state["picker_headers"])
    assert response.status_code == 200


# PRODUCT ENDPOINTS

def test_05_create_first_product():
    payload = {
        "sku": "TSHIRT-RED-L",
        "name": "Red T-Shirt",
        "description": "Cotton Shirt",
        "quantity": 100
    }
    response = client.post("/api/v1/products", json=payload, headers=state["admin_headers"])
    assert response.status_code == 201
    
    data = response.json()
    state["product_1_id"] = data["id"]


def test_06_create_second_product():
    payload = {
        "sku": "HAT-BLUE-OS",
        "name": "Blue Hat",
        "description": "Baseball Cap",
        "quantity": 50
    }
    response = client.post("/api/v1/products", json=payload, headers=state["admin_headers"])
    assert response.status_code == 201
    
    state["product_2_id"] = response.json()["id"]


# ORDERS ENDPOINTS

def test_07_create_order_with_items():
    payload = {
        "order_number": "ORD-TEST-001",
        "customer_name": "Acme Corp",
        "items": [
            {"product_id": state["product_1_id"], "quantity": 2},
            {"product_id": state["product_2_id"], "quantity": 1}
        ]
    }
    response = client.post("/api/v1/orders", json=payload, headers=state["admin_headers"])
    assert response.status_code == 201
    
    data = response.json()
    assert data["order_number"] == "ORD-TEST-001"
    assert len(data["items"]) == 2
    state["order_id"] = data["id"]


def test_08_prevent_duplicate_order():
    payload = {
        "order_number": "ORD-TEST-001",
        "customer_name": "Duplicate Tester",
        "items": [{"product_id": state["product_1_id"], "quantity": 1}]
    }
    response = client.post("/api/v1/orders", json=payload, headers=state["admin_headers"])
    assert response.status_code == 409


def test_09_get_order_by_number():
    response = client.get("/api/v1/orders/number/ORD-TEST-001", headers=state["admin_headers"])
    assert response.status_code == 200
    assert response.json()["customer_name"] == "Acme Corp"
    assert len(response.json()["items"]) == 2


def test_10_get_order_by_id():
    order_id = state["order_id"]
    response = client.get(f"/api/v1/orders/{order_id}", headers=state["admin_headers"])
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == order_id
    assert len(data["items"]) == 2