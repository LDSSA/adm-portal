from typing import Any, Dict, Optional

from payments.models import Payment
from users.models import User


def user_has_payment(user: User) -> bool:
    try:
        user.payment
        return True
    except Payment.DoesNotExist:
        return False


def build_context(user: User, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    base_ctx = {"user_has_payment": user_has_payment(user)}
    ctx = ctx or {}

    return {**base_ctx, **ctx}
