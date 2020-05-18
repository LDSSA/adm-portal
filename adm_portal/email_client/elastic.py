from logging import getLogger
from typing import Any, Dict, Optional

import requests

from .client import EmailClient

logger = getLogger(__name__)


ELASTIC_EMAIL_URL = "https://api.elasticemail.com/v2/"


class ElasticEmailException(Exception):
    pass


class ElasticEmailClient(EmailClient):
    def __init__(self, api_key: str, sender: str) -> None:
        self.api_key = api_key
        self.url = ELASTIC_EMAIL_URL
        self.sender = sender

    def _send_email(
        self, receiver: str, template_id: int, subject: str, *, merge: Optional[Dict[str, Any]] = None
    ) -> None:
        data = {
            "apikey": self.api_key,
            "from": self.sender,
            "subject": subject,
            "to": receiver,
            "template": template_id,
        }

        if merge is not None:
            data = {**data, **{f"merge_{k}": v for k, v in merge.items()}}

        resp = requests.post(f"{self.url}/email/send", data=data)

        if not resp.ok:
            logger.error(
                f"email not sent, response not ok: "
                f"template_id={template_id}, to={receiver}, status_code={resp.status_code}"
            )
            return
        resp_json = resp.json()
        if not resp_json["success"]:
            logger.error(
                f"email not sent, response error: "
                f"template_id={template_id}, to={receiver}, error={resp_json['error']}"
            )
            return

        logger.info(f"email sent: template_id={template_id}, to={receiver}")

    def send_signup_email(self, to: str, *, email_confirmation_url: str) -> None:
        subject = "subject (todo)"
        template_id = 8280
        merge = {"email_confirmation_url": email_confirmation_url}
        self._send_email(to, template_id, subject, merge=merge)

    def send_reset_password_email(self, to: str, *, reset_password_url: str) -> None:
        subject = "subject (todo)"
        template_id = 0
        merge = {"reset_password_url": reset_password_url}
        self._send_email(to, template_id, subject, merge=merge)

    def send_payment_accepted_proof_email(self, to: str, *, message: Optional[str] = None) -> None:
        subject = "subject (todo)"
        template_id = 0
        default_msg = "default message (todo)"
        merge = {"message": message or default_msg}
        self._send_email(to, template_id, subject, merge=merge)

    def send_payment_need_additional_proof_email(self, to: str, *, message: str) -> None:
        subject = "subject (todo)"
        template_id = 0
        merge = {"message": message}
        self._send_email(to, template_id, subject, merge=merge)

    def send_payment_refused_proof_email(self, to: str, *, message: str) -> None:
        subject = "subject (todo)"
        template_id = 0
        merge = {"msg": message}
        self._send_email(to, template_id, subject, merge=merge)
