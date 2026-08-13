from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.category import Category
from app.models.product import Product


# ---------- Category ----------
def create_category(db: Session, category: Category) -> Category:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: int) -> Category | None:
    # eager-load products (same idea as selectinload(Department.employees))
    statement = (
        select(Category)
        .options(selectinload(Category.products))
        .where(Category.id == category_id)
    )
    return db.scalar(statement)


# ---------- Product ----------
def create_product(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)




def list_products(db: Session) -> list[Product]:
    return list(db.scalars(select(Product)))


def update_stock(db: Session, product: Product, new_stock: int) -> Product:
    product.stock = new_stock
    db.commit()
    db.refresh(product)
    return product

def update_product(
    db: Session,
    product: Product,
    updates: dict,
) -> Product:
    """
    Update only the fields supplied by the service layer.
    """

    for field, value in updates.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def deactivate_product(
    db: Session,
    product: Product,
) -> Product:
    """
    Soft-delete a product by marking it inactive.
    The database record is preserved for order history and auditing.
    """

    product.is_active = False

    db.commit()
    db.refresh(product)

    return product


def update_category(
    db: Session,
    category: Category,
    updates: dict,
) -> Category:
    """
    Update only the category fields supplied by the service layer.
    """

    for field, value in updates.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category

def get_active_product(db: Session, product_id: int) -> Product | None:
    """Return a product only when it exists and is active."""
    statement = select(Product).where(
        Product.id == product_id,
        Product.is_active.is_(True),
    )
    return db.scalar(statement)


def list_active_products(db: Session) -> list[Product]:
    """Return only products available for customer browsing."""
    statement = select(Product).where(Product.is_active.is_(True))
    return list(db.scalars(statement))