# app/schemas/enums.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"        # Full system access, client keys, dangerous settings
    MANAGER = "manager"    # Can manage orders, inventory overrides, re-assignments
    PICKER = "picker"      # Can only view assigned pick lists, scan items, & print labels