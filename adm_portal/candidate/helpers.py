from typing import Any, Dict

from payments.models import Payment
from users.models import User


def user_has_payment(user: User) -> bool:
    try:
        user.payment
        return True
    except Payment.DoesNotExist:
        return False


def build_context(user: User, ctx: Dict[str, Any]) -> Dict[str, Any]:
    base_ctx = {"user_has_payment": user_has_payment(user)}
    return {**base_ctx, **ctx}
