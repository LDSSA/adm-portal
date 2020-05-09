from logging import getLogger
from typing import Any

from payments.domain import Domain as PaymentsDomain
from payments.models import Payment
from profiles.models import Profile
from selected.models import Selected
from users.models import User

logger = getLogger(__name__)


class DomainException(Exception):
    pass


class Domain:
    @staticmethod
    def current_selected() -> Any:
        """Query that powers the first table of the `selected` page"""
        return (
            Profile.objects.exclude(user__selected__isnull=True)
            .exclude(user__payment__isnull=True)
            .exclude(user__payment__status="rejected")
        )

    @staticmethod
    def pre_selected() -> Any:
        """Query that powers the second table of the `selected` page"""
        return Profile.objects.filter(user__selected__isnull=False).filter(user__payment__isnull=True)

    @staticmethod
    def commit() -> None:
        for profile in Domain.pre_selected():
            PaymentsDomain.create_payment(profile)

    @staticmethod
    def delete(u: User) -> None:
        if Payment.objects.filter(user=u).exists():
            logger.warning(f"user `{u.email}` - trying to delete user.selected but user.payment exists")
            raise DomainException("cannot be deleted, payment exists")

        try:
            s = Selected.objects.get(user=u)
            s.delete()
        except Selected.DoesNotExist:
            logger.warning(f"user `{u.email}` - trying to delete user.selected but user.select doesn't exist")
            raise DomainException("cannot be deleted, not in `selected` table")
