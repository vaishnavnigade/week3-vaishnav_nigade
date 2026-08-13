from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Category ----------
class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None


# ---------- Product ----------
class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    category_id: int

class ProductUpdate(BaseModel):
    """Fields that an admin may update on an existing product."""

    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = None


class CategoryUpdate(BaseModel):
    """Fields that an admin may update on an existing category."""

    name: str | None = None
    description: str | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    price: Decimal
    stock: int
    category_id: int
    created_at: datetime


# Category with its nested products (same idea as DepartmentRead -> employees)
class CategoryWithProductsRead(CategoryRead):
   products: list[ProductRead] = Field(default_factory=list)