import os
from logging import getLogger

from django.db import models

from profiles.models import Profile

logger = getLogger(__name__)


class Document(models.Model):
    payment = models.ForeignKey("payments.Payment", on_delete=models.CASCADE)

    file_location = models.TextField(null=False)

    doc_type = models.CharField(
        blank=False,
        null=False,
        max_length=20,
        choices=[("payment_proof", "Payment Proof"), ("student_id", "Student ID")],
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        return os.path.basename(self.file_location)


class Payment(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    value = models.FloatField(blank=False, null=False)
    currency = models.CharField(blank=False, null=False, max_length=10, choices=[("eur", "€")])

    due_date = models.DateTimeField()

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
    def get_payment_proof_documents(self):
        return Document.objects.filter(payment=self, doc_type="payment_proof").order_by("-updated_at")

    @property
    def has_payment_proof_document(self):
        return len(self.get_payment_proof_documents) > 0

    @property
    def get_student_id_documents(self):
        return Document.objects.filter(payment=self, doc_type="student_id").order_by("-updated_at")

    @property
    def has_student_id_document(self):
        return len(self.get_student_id_documents) > 0

    @property
    def is_status_accepted(self):
        return self.status == "accepted"

    @property
    def is_status_rejected(self):
        return self.status == "rejected"

    @property
    def is_status_pending_verification(self):
        return self.status == "pending_verification"

    @property
    def is_status_waiting_for_documents(self):
        return self.status == "waiting_for_documents"

    def add_document(self, document: Document) -> None:
        logger.info(f"payment_id={self.id}: new document uploaded")
        document.payment = self
        document.save()

        # now we need to update the payment status to "pending_verification"
        # unless the candidate is a student and is missing the other proof (payment proof or student id)
        profile = Profile.objects.get(user=self.user)

        if profile.is_student:
            has_missing_student_id = document.doc_type == "payment_proof" and not self.has_student_id_document
            has_missing_payment_proof = document.doc_type == "student_id" and not self.has_payment_proof_document
            if has_missing_student_id or has_missing_payment_proof:
                return

        self.status = "pending_verification"
        self.save()
