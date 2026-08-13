
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.sessions import get_db
from app.schemas.product_schema import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CategoryWithProductsRead,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.services import product_service
from app.utils.authorization import require_roles
from app.utils.exceptions import NotFoundError


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# ============================================================================
# CATEGORY APIs
# ============================================================================

@router.post(
    "/categories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin"))],
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
):
    """Create a product category. Admin access required."""
    try:
        return product_service.create_category(db, payload)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.put(
    "/categories/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(require_roles("admin"))],
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
):
    """Update a product category. Admin access required."""
    try:
        return product_service.update_category(
            db,
            category_id,
            payload,
        )

    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/categories/{category_id}",
    response_model=CategoryWithProductsRead,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    """Return one category with its products."""
    try:
        return product_service.get_category(db, category_id)

    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


# ============================================================================
# CUSTOMER PRODUCT APIs
# ============================================================================

@router.get(
    "",
    response_model=list[ProductRead],
)
def list_products(
    db: Session = Depends(get_db),
):
    """Return the available products."""
    return product_service.list_products(db)


@router.get(
    "/{product_id}",
    response_model=ProductRead,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Return one product by ID."""
    try:
        return product_service.get_product(db, product_id)

    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


# ============================================================================
# ADMIN PRODUCT APIs
# ============================================================================

@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin"))],
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
):
    """Create a product. Admin access required."""
    try:
        return product_service.create_product(db, payload)

    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.put(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(require_roles("admin"))],
)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    """Update a product. Admin access required."""
    try:
        return product_service.update_product(
            db,
            product_id,
            payload,
        )

    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.patch(
    "/{product_id}/deactivate",
    response_model=ProductRead,
    dependencies=[Depends(require_roles("admin"))],
)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Deactivate a product without deleting its database record."""
    try:
        return product_service.deactivate_product(
            db,
            product_id,
        )

    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
