from django.test import TestCase

from payments.domain import Domain, DomainException
from payments.models import Document, Payment
from profiles.models import Profile
from users.models import User


class TestDomain(TestCase):
    def setUp(self) -> None:
        self.staff_user = User.objects.create_staff_user(email="staff@adm.com", password="secret")

    def test_create_payment_regular(self) -> None:
        user = User.objects.create_user(email="user@adm.com", password="strong")
        profile = Profile.objects.create(user=user, full_name="name", ticket_type="regular")

        payment = Domain.create_payment(profile)

        self.assertEqual(payment.ticket_type, "regular")
        self.assertEqual(payment.value, 500)
        self.assertEqual(payment.currency, "eur")
        self.assertEqual(payment.status, "waiting_for_documents")

    def test_create_payment_student(self) -> None:
        user = User.objects.create_user(email="student@adm.com", password="strong")
        profile = Profile.objects.create(user=user, full_name="name", ticket_type="student")

        payment = Domain.create_payment(profile)

        self.assertEqual(payment.ticket_type, "student")
        self.assertEqual(payment.value, 300)
        self.assertEqual(payment.currency, "eur")
        self.assertEqual(payment.status, "waiting_for_documents")

    def test_create_payment_company(self) -> None:
        user = User.objects.create_user(email="company@adm.com", password="strong")
        profile = Profile.objects.create(user=user, full_name="name", ticket_type="company")

        payment = Domain.create_payment(profile)

        self.assertEqual(payment.ticket_type, "company")
        self.assertEqual(payment.value, 1500)
        self.assertEqual(payment.currency, "eur")
        self.assertEqual(payment.status, "waiting_for_documents")

    def test_reset_payment(self) -> None:
        user = User.objects.create_user(email="company@adm.com", password="strong")
        profile = Profile.objects.create(user=user, full_name="name", ticket_type="company")

        payment = Domain.create_payment(profile)
        Domain.add_document(payment, Document())

        payment.status = "waiting_for_documents"
        payment.save()
        profile.ticket_type = "student"
        profile.save()

        reset_payment = Domain.reset_payment(payment, self.staff_user)

        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(reset_payment.id, payment.id)
        self.assertEqual(payment.ticket_type, "student")
        self.assertEqual(payment.value, 300)
        self.assertEqual(payment.currency, "eur")
        self.assertEqual(payment.status, "waiting_for_documents")

        payment.status = "pending_verification"
        payment.save()

        payment = Domain.reset_payment(payment, self.staff_user)

        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(payment.ticket_type, "student")
        self.assertEqual(payment.value, 300)
        self.assertEqual(payment.currency, "eur")
        self.assertEqual(payment.status, "waiting_for_documents")

        payment.status = "accepted"
        payment.save()

        with self.assertRaises(DomainException):
            Domain.reset_payment(payment, self.staff_user)

        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(payment.ticket_type, "student")
        self.assertEqual(payment.value, 300)
        self.assertEqual(payment.currency, "eur")
        self.assertEqual(payment.status, "accepted")

        payment.status = "rejected"
        payment.save()

        with self.assertRaises(DomainException):
            Domain.reset_payment(payment, self.staff_user)

        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(payment.ticket_type, "student")
        self.assertEqual(payment.value, 300)
        self.assertEqual(payment.currency, "eur")
        self.assertEqual(payment.status, "rejected")

    def test_add_document_regular(self) -> None:
        user = User.objects.create_user(email="user@adm.com", password="strong")
        profile = Profile.objects.create(user=user, full_name="name", ticket_type="regular")
        payment = Domain.create_payment(profile)

        self.assertFalse(payment.has_payment_proof_document)
        self.assertFalse(payment.has_student_id_document)
        self.assertEqual(Document.objects.filter(payment=payment).count(), 0)

        document = Document(doc_type="payment_proof", file_location="dummy")
        Domain.add_document(payment, document)

        self.assertEqual(payment.status, "pending_verification")
        self.assertTrue(payment.has_payment_proof_document)
        self.assertFalse(payment.has_student_id_document)
        self.assertEqual(Document.objects.filter(payment=payment).count(), 1)

    def test_add_document_student(self) -> None:
        user = User.objects.create_user(email="user@adm.com", password="strong")
        profile = Profile.objects.create(user=user, full_name="name", ticket_type="student")
        payment = Domain.create_payment(profile)

        self.assertFalse(payment.has_payment_proof_document)
        self.assertFalse(payment.has_student_id_document)
        self.assertEqual(Document.objects.filter(payment=payment).count(), 0)

        document = Document(doc_type="payment_proof", file_location="dummy")
        Domain.add_document(payment, document)

        self.assertEqual(payment.status, "waiting_for_documents")
        self.assertTrue(payment.has_payment_proof_document)
        self.assertFalse(payment.has_student_id_document)
        self.assertEqual(Document.objects.filter(payment=payment).count(), 1)

        document = Document(doc_type="student_id", file_location="dummy")
        Domain.add_document(payment, document)

        self.assertEqual(payment.status, "pending_verification")
        self.assertTrue(payment.has_payment_proof_document)
        self.assertTrue(payment.has_student_id_document)
        self.assertEqual(Document.objects.filter(payment=payment).count(), 2)
