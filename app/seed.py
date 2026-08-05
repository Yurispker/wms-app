# seed.py
from app.database import Base, engine, sessionLocal
from app.models.products import Product
from app.models.users import User
from app.security import get_password_hash  
from app.schemas.enums import UserRole


def reset_and_seed():
    print("Dropping all existing database tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating clean database tables...")
    Base.metadata.create_all(bind=engine)

    db = sessionLocal()

    try:

        # SEED USERS

        print("Seeding sample users...")
        
        sample_user = [
            User(
                username="admin",
                email="admin@wms.local",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                role=UserRole.ADMIN
            ),
            User(
                username="manager",
                email="manager@wms.local",
                hashed_password=get_password_hash("manager123"),
                is_active=True,
                role=UserRole.MANAGER
            ),
            User(
                username="picker1",
                email="picker1@wms.local",
                hashed_password=get_password_hash("picker123"),
                is_active=True,
                role=UserRole.PICKER
            ),
        ]
        
        db.add_all(sample_user)


        # SEED PRODUCTS & LOCATIONS

        print("Seeding sample products with locations...")
        
        sample_products = [
            Product(
                sku="A1",
                name="Alpha1",
                description="2.4GHz Optical Mouse",
                quantity=50,
                aisle="Aisle 1",
                rack="Rack A",
                shelf="Shelf 3"
            ),
            Product(
                sku="A2",
                name="Alpha2",
                description="RGB Backlit Blue Switches",
                quantity=25,
                aisle="Aisle 2",
                rack="Rack C",
                shelf="Shelf 1"
            ),
            Product(
                sku="A3",
                name="Alpha3",
                description="IPS Panel with USB-C Hub",
                quantity=10,
                aisle="Aisle 5",
                rack="Rack B",
                shelf="Shelf 2"
            ),
            Product(
                sku="A4",
                name="Alpha4",
                description="Wireless Bluetooth Laser Scanner",
                quantity=100,
                aisle="Aisle 1",
                rack="Rack B",
                shelf="Shelf 4"
            )
        ]

        db.add_all(sample_products)

        # Commit everything to the database
        db.commit()
        print("Database successfully reset and seeded!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    reset_and_seed()