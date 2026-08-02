from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from app.database import Base
from app.schemas.enums import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    role = Column(SQLEnum(UserRole), default=UserRole.PICKER, nullable=False)