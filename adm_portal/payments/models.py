from logging import getLogger

from django.db import models

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


class Payment(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    value = models.FloatField(blank=False, null=False)
    currency = models.CharField(blank=False, null=False, max_length=10, choices=[("eur", "€")])

    due_date = models.DateTimeField()

    status = models.CharField(
        blank=False,
        null=False,
        max_length=10,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")],
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def add_document(self, document: Document) -> None:
        logger.info(f"payment_id={self.id}: new document uploaded")
        document.payment = self
        document.save()

    @property
    def get_payment_proof_documents(self):
        return Document.objects.filter(payment=self, doc_type="payment_proof")

    @property
    def get_student_id_documents(self):
        return Document.objects.filter(payment=self, doc_type="student_id")
