from datetime import datetime

from django.test import TestCase

from payments.models import Payment
from profiles.models import Profile
from selected.domain import Domain, DomainException
from selected.models import Selected
from users.models import User


class TestDomain(TestCase):
    def setUp(self) -> None:
        u_not_selected = User.objects.create(email="not_selected@amd.com")
        u_payment_none = User.objects.create(email="payment_none@amd.com")
        u_payment_awaiting = User.objects.create(email="payment_awaiting@amd.com")
        u_payment_pending = User.objects.create(email="payment_pending@amd.com")
        u_payment_accepted = User.objects.create(email="payment_accepted@amd.com")
        u_payment_rejected = User.objects.create(email="payment_rejected@amd.com")

        Profile.objects.create(user=u_not_selected, ticket_type="regular")
        Profile.objects.create(user=u_payment_none, ticket_type="regular")
        Profile.objects.create(user=u_payment_awaiting, ticket_type="regular")
        Profile.objects.create(user=u_payment_pending, ticket_type="regular")
        Profile.objects.create(user=u_payment_accepted, ticket_type="regular")
        Profile.objects.create(user=u_payment_rejected, ticket_type="regular")

        Payment.objects.create(
            user=u_payment_awaiting, status="waiting_for_documents", value=100, due_date=datetime.now()
        )
        Payment.objects.create(
            user=u_payment_pending, status="pending_verification", value=100, due_date=datetime.now()
        )
        Payment.objects.create(user=u_payment_accepted, status="accepted", value=100, due_date=datetime.now())
        Payment.objects.create(user=u_payment_rejected, status="rejected", value=100, due_date=datetime.now())

        Selected.objects.create(user=u_payment_none)
        Selected.objects.create(user=u_payment_awaiting)
        Selected.objects.create(user=u_payment_pending)
        Selected.objects.create(user=u_payment_accepted)
        Selected.objects.create(user=u_payment_rejected)

    def test_query_current_selected(self) -> None:
        q = Domain.current_selected()
        self.assertEqual(q.count(), 3)
        for qi in q:
            self.assertIsNotNone(qi.user.email)

    def test_query_pre_selected(self) -> None:
        q = Domain.pre_selected()
        self.assertEqual(q.count(), 1)
        for qi in q:
            self.assertIsNotNone(qi.user.email)

    def test_commit(self) -> None:
        current_selected_before = Domain.current_selected().count()
        pre_selected_before = Domain.pre_selected().count()

        Domain.commit()

        current_selected_after = Domain.current_selected().count()
        pre_selected_after = Domain.pre_selected().count()

        self.assertEqual(current_selected_after, current_selected_before + 1)
        self.assertEqual(pre_selected_after, pre_selected_before - 1)

    def test_delete_pre_selected(self) -> None:
        pre_selected_before = Domain.pre_selected().count()

        u_to_delete = User.objects.get(email="payment_none@amd.com")
        Domain.delete(u_to_delete)

        self.assertFalse(Selected.objects.filter(user__email="payment_none@amd.com").exists())
        self.assertEqual(Domain.pre_selected().count(), pre_selected_before - 1)

    def test_delete_current_selected_raise(self) -> None:
        current_selected_before = Domain.current_selected().count()

        u_to_delete = User.objects.get(email="payment_awaiting@amd.com")
        with self.assertRaises(DomainException):
            Domain.delete(u_to_delete)

        self.assertTrue(Selected.objects.filter(user__email="payment_awaiting@amd.com").exists())
        self.assertEqual(Domain.current_selected().count(), current_selected_before)
