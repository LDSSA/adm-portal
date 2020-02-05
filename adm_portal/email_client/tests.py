from django.test import TestCase, tag

from .elastic_email import ElasticEmail


class TestSendExampleEmail(TestCase):
    @tag("integration")
    def test_send_success(self) -> None:
        client = ElasticEmail()
        client.send_example_email("maria@lisbondatascience.org", "Chizo")
