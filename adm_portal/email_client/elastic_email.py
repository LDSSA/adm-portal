from typing import Dict

import requests
from django.conf import settings

from .client import EmailClient


class ElasticEmail(EmailClient):
    def __init__(self) -> None:
        # Get this from settings
        self.url = settings.ELASTICEMAIL_API_URL
        self.api_key = settings.ELASTICEMAIL_API_KEY
        self.email_from = settings.ELASTICEMAIL_API_FROM

    def _send(self, email_to: str, template_id: int, subject: str, merge_fields: Dict[str, str]) -> None:
        base_data = {
            "apikey": self.api_key,
            "subject": subject,
            "from": self.email_from,
            "to": email_to,
            "template": template_id,
        }
        data = {**base_data, **merge_fields}

        r = requests.post(self.url, data=data)

        if not r.json()["success"]:
            raise RuntimeError(r.json()["error"])

    def send_example_email(self, email_to: str, username: str) -> None:
        subject = "This is a subject"
        template_id = 8280
        merge_fields = {"merge_coco": username}

        self._send(email_to, template_id, subject, merge_fields)
