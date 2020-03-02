from datetime import datetime
from logging import getLogger

from django.db import transaction

from profiles.models import Profile

from .models import Document, Payment

logger = getLogger(__name__)


class DomainException(Exception):
    pass


class Domain:
    values = {"student": 300, "regular": 500, "company": 1500}

    @staticmethod
    def create_payment(profile: Profile) -> Payment:
        return Payment.objects.create(
            user=profile.user,
            value=Domain.values[profile.ticket_type],
            currency="eur",
            due_date=datetime(day=21, month=6, year=2020),
            ticket_type=profile.ticket_type,
        )

    @staticmethod
    def reset_payment(payment: Payment, profile: Profile) -> Payment:
        if not Domain.can_reset_payment(payment):
            raise DomainException(f"can't reset payment in state `{payment.status}`")
        with transaction.atomic():
            payment.delete()
            payment = Domain.create_payment(profile)
        return payment

    @staticmethod
    def can_reset_payment(payment: Payment) -> bool:
        return payment.status in ["waiting_for_documents", "pending_verification"]

    @staticmethod
    def add_document(payment: Payment, document: Document) -> None:
        logger.info(f"payment_id={payment.id}: new document uploaded")
        document.payment = payment
        document.save()

        # now we need to update the payment status to "pending_verification"
        # unless the candidate is a student and is missing the other proof (payment proof or student id)
        if payment.user.profile.is_student:
            has_missing_student_id = document.doc_type == "payment_proof" and not payment.has_student_id_document
            has_missing_payment_proof = document.doc_type == "student_id" and not payment.has_payment_proof_document
            if has_missing_student_id or has_missing_payment_proof:
                return

        payment.status = "pending_verification"
        payment.save()
