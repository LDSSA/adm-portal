from django.test import TestCase

from .models import Profile
from .views import get_context


class TestUserView(TestCase):
    def setUp(self) -> None:
        self.chi = Profile.objects.create(
            full_name="chi", profession="data scientist", gender="female", ticket_type="regular"
        )

        self.joao = Profile.objects.create(
            full_name="joao", profession="software engineer", gender="male", ticket_type="company"
        )

    def test_get_context(self) -> None:
        context = get_context()
        self.assertEqual(len(context), 2)
        self.assertIn("column_names", context)
        self.assertIn("profiles", context)

        self.assertEqual(
            context["column_names"],
            ["ID", "Full Name", "Profession", "Gender", "Ticket Type", "Updated At", "Created At"],
        )

        self.assertEqual(len(context["profiles"]), 2)
