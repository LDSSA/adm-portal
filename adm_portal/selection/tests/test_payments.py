from django.test import TestCase

from profiles.models import Profile
from users.models import User

from ..models import Selection
from ..payment import load_payment_data
from ..status import SelectionStatus


class TestDomain(TestCase):
    def setUp(self) -> None:
        self.staff_user = User.objects.create_staff_user(email="staff@adm.com", password="secret")

    def test_load_payment_data(self) -> None:
        user = User.objects.create_user(email="user@adm.com", password="strong")
        Profile.objects.create(user=user, full_name="name", ticket_type="regular")
        selection = Selection.objects.create(user=user, status=SelectionStatus.SELECTED)
        load_payment_data(selection)

        self.assertEqual(selection.ticket_type, "regular")
        self.assertEqual(selection.payment_value, 500)
        self.assertEqual(selection.status, SelectionStatus.SELECTED)

    def test_create_payment_student(self) -> None:
        user = User.objects.create_user(email="student@adm.com", password="strong")
        Profile.objects.create(user=user, full_name="name", ticket_type="student")
        selection = Selection.objects.create(user=user, status=SelectionStatus.SELECTED)
        load_payment_data(selection)

        self.assertEqual(selection.ticket_type, "student")
        self.assertEqual(selection.payment_value, 300)
        self.assertEqual(selection.status, SelectionStatus.SELECTED)

    def test_create_payment_company(self) -> None:
        user = User.objects.create_user(email="company@adm.com", password="strong")
        Profile.objects.create(user=user, full_name="name", ticket_type="company")
        selection = Selection.objects.create(user=user, status=SelectionStatus.SELECTED)
        load_payment_data(selection)

        self.assertEqual(selection.ticket_type, "company")
        self.assertEqual(selection.payment_value, 1500)
        self.assertEqual(selection.status, SelectionStatus.SELECTED)

    #
    # def test_add_document_regular(self) -> None:
    #     user = User.objects.create_user(email="user@adm.com", password="strong")
    #     Profile.objects.create(user=user, full_name="name", ticket_type="regular")
    #     selection = Selection.objects.create(user=user, status=SelectionStatus.SELECTED)
    #
    #     self.assertFalse(selection.has_payment_proof_document)
    #     self.assertFalse(payment.has_student_id_document)
    #     self.assertEqual(Document.objects.filter(payment=payment).count(), 0)
    #
    #     document = Document(doc_type="payment_proof", file_location="dummy")
    #     Domain.add_document(payment, document)
    #
    #     self.assertEqual(payment.status, "pending_verification")
    #     self.assertTrue(payment.has_payment_proof_document)
    #     self.assertFalse(payment.has_student_id_document)
    #     self.assertEqual(Document.objects.filter(payment=payment).count(), 1)
    #
    # def test_add_document_student(self) -> None:
    #     user = User.objects.create_user(email="user@adm.com", password="strong")
    #     profile = Profile.objects.create(user=user, full_name="name", ticket_type="student")
    #     SelectedDomain.new_candidate(user)
    #     payment = Domain.create_payment(profile)
    #
    #     self.assertFalse(payment.has_payment_proof_document)
    #     self.assertFalse(payment.has_student_id_document)
    #     self.assertEqual(Document.objects.filter(payment=payment).count(), 0)
    #
    #     document = Document(doc_type="payment_proof", file_location="dummy")
    #     Domain.add_document(payment, document)
    #
    #     self.assertEqual(payment.status, "waiting_for_documents")
    #     self.assertTrue(payment.has_payment_proof_document)
    #     self.assertFalse(payment.has_student_id_document)
    #     self.assertEqual(Document.objects.filter(payment=payment).count(), 1)
    #
    #     document = Document(doc_type="student_id", file_location="dummy")
    #     Domain.add_document(payment, document)
    #
    #     self.assertEqual(payment.status, "pending_verification")
    #     self.assertTrue(payment.has_payment_proof_document)
    #     self.assertTrue(payment.has_student_id_document)
    #     self.assertEqual(Document.objects.filter(payment=payment).count(), 2)
