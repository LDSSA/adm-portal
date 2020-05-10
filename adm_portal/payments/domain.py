from datetime import datetime
from enum import Enum
from logging import getLogger
from typing import Any, Dict, List, Optional

from profiles.models import Profile
from users.models import User

from .models import Document, Payment, PaymentLogs

logger = getLogger(__name__)


class DomainException(Exception):
    pass


class PaymentEvents(Enum):
    created = "[Payment Created]"
    reset = "[Payment Reset]"
    add_doc = "[Added Payment Document]"
    status_update = "[Payment Status Updated]"
    note = "[Payment Note Added]"


class Domain:
    values = {"student": 300, "regular": 500, "company": 1500}

    @staticmethod
    def create_payment(profile: Profile, staff: Optional[User] = None) -> Payment:
        ticket_type = profile.ticket_type
        value = Domain.values[ticket_type]
        payment = Payment.objects.create(
            user=profile.user,
            value=value,
            currency="eur",
            due_date=datetime(day=21, month=6, year=2020),
            ticket_type=ticket_type,
        )
        Domain.payment_log(
            payment, PaymentEvents.created, data={"value": value, "ticket-type": ticket_type}, user=staff
        )
        return payment

    @staticmethod
    def payment_can_be_updated(payment: Payment) -> bool:
        return payment.status not in ["accepted", "rejected"]

    @staticmethod
    def reset_payment(payment: Payment, staff: User) -> Payment:
        if not Domain.payment_can_be_updated(payment):
            raise DomainException(f"payment is frozen (status=`{payment.status}`)")

        old_status = payment.status
        old_value = payment.value
        old_ticket_type = payment.ticket_type

        value = Domain.values[payment.user.profile.ticket_type]
        ticket_type = payment.user.profile.ticket_type
        status = "waiting_for_documents"
        payment.value = value
        payment.ticket_type = ticket_type
        payment.status = status
        payment.save()
        Domain.payment_log(
            payment,
            PaymentEvents.reset,
            data={
                "old-value": old_value,
                "new-value": value,
                "old-ticket-type": old_ticket_type,
                "new-ticket-type": ticket_type,
                "old-status": old_status,
                "new-status": status,
            },
            user=staff,
        )

        return payment

    @staticmethod
    def add_document(payment: Payment, document: Document) -> None:
        if not Domain.payment_can_be_updated(payment):
            raise DomainException(f"payment is frozen (status=`{payment.status}`)")
        logger.info(f"payment_id={payment.id}: new document uploaded")
        document.payment = payment
        document.save()
        Domain.payment_log(
            payment,
            PaymentEvents.add_doc,
            data={"doc-type": document.doc_type, "doc-location": document.file_location},
            user=payment.user,
        )

        # now we need to update the payment status to "pending_verification"
        # unless the candidate is a student and is missing the other proof (payment proof or student id)
        if payment.user.profile.is_student:
            has_missing_student_id = document.doc_type == "payment_proof" and not payment.has_student_id_document
            has_missing_payment_proof = document.doc_type == "student_id" and not payment.has_payment_proof_document
            if has_missing_student_id or has_missing_payment_proof:
                return  # status not updated

        Domain.update_status(
            payment, "pending_verification", context="automatically updated because document was added"
        )

    @staticmethod
    def update_status(
        payment: Payment, new_status: str, *, context: Optional[str] = None, staff: Optional[User] = None
    ) -> None:
        if not Domain.payment_can_be_updated(payment):
            raise DomainException(f"payment is frozen (status=`{payment.status}`)")
        old_status = payment.status
        payment.status = new_status
        payment.save()

        Domain.payment_log(
            payment,
            PaymentEvents.status_update,
            data={"old-status": old_status, "new-status": new_status, "context": context},
            user=staff,
        )

    @staticmethod
    def manual_update_status(payment: Payment, new_status: str, staff: User, *, msg: Optional[str] = None) -> None:
        Domain.update_status(payment, new_status, context=msg, staff=staff)

    @staticmethod
    def add_payment_note(payment: Payment, note: str, user: User) -> None:
        Domain.payment_log(payment, PaymentEvents.note, data={"note": note}, user=user)

    @staticmethod
    def payment_log(
        payment: Payment, event: PaymentEvents, *, data: Dict[str, Any], user: Optional[User] = None
    ) -> None:
        data_s = "\n".join([f"{k}: {v}" for k, v in data.items()])
        msg = f"{event.value}\n{data_s}\n---\ntriggered by {user.email if user is not None else 'unknown'}"
        PaymentLogs.objects.create(payment=payment, event=event.name, message=msg)


class DomainQueries:
    @staticmethod
    def get_payment_logs(payment: Payment) -> List[Dict[str, Any]]:
        return PaymentLogs.objects.filter(payment=payment).values("event", "message", "created_at")
