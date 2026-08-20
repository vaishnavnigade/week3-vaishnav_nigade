from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.cart_schema import CartItemCreate, CartItemUpdate



from app.models.cart import CartItem
from app.repositories import cart_repository, product_repository, user_repository
from app.schemas.cart_schema import CartItemCreate
from app.utils.exceptions import NotFoundError, OutOfStockError


def add_to_cart(db: Session, user_id: int, data: CartItemCreate) -> CartItem:
    # validate user
    if user_repository.get_user(db, user_id) is None:
        raise NotFoundError("User not found")

    # validate product + stock
    product = product_repository.get_product(db, data.product_id)
    if product is None:
        raise NotFoundError("Product not found")
    if product.stock < data.quantity:
        raise OutOfStockError("Not enough stock available")

    # if already in cart, just increase quantity
    existing = cart_repository.get_cart_item_by_product(db, user_id, data.product_id)
    if existing:
        return cart_repository.update_cart_item(
            db, existing, existing.quantity + data.quantity
        )

    cart_item = CartItem(
        user_id=user_id,
        product_id=data.product_id,
        quantity=data.quantity,
    )
    return cart_repository.add_cart_item(db, cart_item)


def list_cart(db: Session, user_id: int) -> list[CartItem]:
    return cart_repository.list_cart_items(db, user_id)


def remove_from_cart(
    db: Session,
    user_id: int,
    cart_item_id: int,
) -> None:
    # Find the requested cart item.
    cart_item = cart_repository.get_cart_item(db, cart_item_id)

    # Return the same error for missing or unauthorized items.
    # This avoids exposing whether another user's cart item exists.
    if cart_item is None or cart_item.user_id != user_id:
        raise NotFoundError("Cart item not found")

    cart_repository.delete_cart_item(db, cart_item)

def update_cart_item(
    db: Session,
    user_id: int,
    cart_item_id: int,
    payload: CartItemUpdate,
):
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id,
        )
        .first()
    )

    if cart_item is None:
        raise NotFoundError("Cart item not found")

    cart_item.quantity = payload.quantity

    try:
        db.commit()
        db.refresh(cart_item)
    except SQLAlchemyError:
        db.rollback()
        raise

    return cart_item

def update_cart_item(
    db: Session,
    user_id: int,
    cart_item_id: int,
    data: CartItemUpdate,
) -> CartItem:
    """
    Update a cart item's quantity for the authenticated user.

    The cart item must belong to the logged-in user, the product
    must be active, and the requested quantity must be in stock.
    """

    cart_item = cart_repository.get_cart_item(
        db,
        cart_item_id,
    )

    # Hide ownership information from other users.
    if cart_item is None or cart_item.user_id != user_id:
        raise NotFoundError("Cart item not found")

    product = product_repository.get_product(
        db,
        cart_item.product_id,
    )

    if product is None or not product.is_active:
        raise NotFoundError("Product not found")

    if product.stock < data.quantity:
        raise OutOfStockError(
            f"Not enough stock for '{product.name}'"
        )

    return cart_repository.update_cart_item(
        db,
        cart_item,
        data.quantity,
    )