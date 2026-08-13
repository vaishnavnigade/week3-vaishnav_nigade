
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.utils.authorization import require_roles


def test_admin_can_access_admin_route():
    """Admin users should pass an admin-only authorization check."""
    checker = require_roles("admin")
    admin_user = SimpleNamespace(role="admin")

    result = checker(admin_user)

    assert result is admin_user


def test_support_can_access_support_route():
    """Support users should pass a support-authorized check."""
    checker = require_roles("admin", "support")
    support_user = SimpleNamespace(role="support")

    result = checker(support_user)

    assert result is support_user


def test_customer_cannot_access_admin_route():
    """Customers should receive HTTP 403 for admin-only operations."""
    checker = require_roles("admin")
    customer_user = SimpleNamespace(role="customer")

    with pytest.raises(HTTPException) as error:
        checker(customer_user)

    assert error.value.status_code == 403
