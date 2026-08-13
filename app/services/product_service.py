
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.repositories import product_repository
from app.schemas.product_schema import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
)
from app.utils.exceptions import NotFoundError


# ---------- Category services ----------

def create_category(db: Session, data: CategoryCreate) -> Category:
    """Create a new product category."""
    category = Category(
        name=data.name,
        description=data.description,
    )

    return product_repository.create_category(db, category)


def get_category(db: Session, category_id: int) -> Category:
    """Return a category with its products."""
    category = product_repository.get_category(db, category_id)

    if category is None:
        raise NotFoundError("Category not found")

    return category


def update_category(
    db: Session,
    category_id: int,
    data: CategoryUpdate,
) -> Category:
    """Update an existing category."""
    category = product_repository.get_category(db, category_id)

    if category is None:
        raise NotFoundError("Category not found")

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise ValueError("At least one category field is required")

    return product_repository.update_category(db, category, updates)


# ---------- Product services ----------

def create_product(db: Session, data: ProductCreate) -> Product:
    """Create a product only when its category exists."""
    category = product_repository.get_category(db, data.category_id)

    if category is None:
        raise NotFoundError("Category not found")

    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        category_id=data.category_id,
        is_active=True,
    )

    return product_repository.create_product(db, product)


def get_product(db: Session, product_id: int) -> Product:
    """Return a product by its identifier."""
    product = product_repository.get_product(db, product_id)

    if product is None:
        raise NotFoundError("Product not found")

    return product


def list_products(db: Session) -> list[Product]:
    """Return the current product list."""
    return product_repository.list_products(db)


def update_product(
    db: Session,
    product_id: int,
    data: ProductUpdate,
) -> Product:
    """Update an existing product."""
    product = product_repository.get_product(db, product_id)

    if product is None:
        raise NotFoundError("Product not found")

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise ValueError("At least one product field is required")

    # If the category changes, the new category must exist.
    if "category_id" in updates:
        new_category_id = updates["category_id"]

        if new_category_id is None:
            raise ValueError("category_id cannot be null")

        if product_repository.get_category(db, int(new_category_id)) is None:
            raise NotFoundError("Category not found")

    return product_repository.update_product(db, product, updates)


def deactivate_product(db: Session, product_id: int) -> Product:
    """Deactivate a product without deleting historical data."""
    product = product_repository.get_product(db, product_id)

    if product is None:
        raise NotFoundError("Product not found")

    return product_repository.deactivate_product(db, product)
