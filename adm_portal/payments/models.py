import os
from logging import getLogger
from typing import List

from django.db import models

logger = getLogger(__name__)


doc_type_choices = [("payment_proof", "Payment Proof"), ("student_id", "Student ID")]
ticket_types_choices = [("student", "Student"), ("regular", "Regular"), ("company", "Company")]


class Document(models.Model):
    payment = models.ForeignKey("payments.Payment", on_delete=models.CASCADE, related_name="documents")

    file_location = models.TextField(null=False)

    doc_type = models.CharField(blank=False, null=False, max_length=20, choices=doc_type_choices)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self) -> str:
        return os.path.basename(self.file_location)


class Payment(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    value = models.FloatField(blank=False, null=False)
    currency = models.CharField(blank=False, null=False, max_length=10, choices=[("eur", "€")])

    due_date = models.DateTimeField()

    ticket_type = models.CharField(blank=False, null=False, choices=ticket_types_choices, max_length=15)

    status = models.CharField(
        blank=False,
        null=False,
        max_length=30,
        default="waiting_for_documents",
        choices=[
            ("waiting_for_documents", "Waiting for candidate documents"),
            ("pending_verification", "Pending verification"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def ticket_type_is_student(self) -> bool:
        return self.ticket_type == "student"

    @property
    def get_payment_proof_documents(self) -> List[Document]:
        return self.documents.filter(doc_type="payment_proof").order_by("-updated_at")

    @property
    def has_payment_proof_document(self) -> bool:
        return len(self.get_payment_proof_documents) > 0

    @property
    def get_student_id_documents(self) -> List[Document]:
        return self.documents.filter(doc_type="student_id").order_by("-updated_at")

    @property
    def has_student_id_document(self) -> bool:
        return len(self.get_student_id_documents) > 0

    @property
    def is_status_accepted(self) -> bool:
        return self.status == "accepted"

    @property
    def is_status_rejected(self) -> bool:
        return self.status == "rejected"

    @property
    def is_status_pending_verification(self) -> bool:
        return self.status == "pending_verification"

    @property
    def is_status_waiting_for_documents(self) -> bool:
        return self.status == "waiting_for_documents"
