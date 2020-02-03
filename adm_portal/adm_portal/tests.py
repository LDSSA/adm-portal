from django.test import TestCase

from .views import ping_pong


class PingTestCase(TestCase):
    def test_ping_pong(self) -> None:
        self.assertEqual(ping_pong(), "Pong")
