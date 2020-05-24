import json
import os
from datetime import datetime
from typing import Any, Optional

from .client import EmailClient


class LocalEmailClient(EmailClient):
    def __init__(self, root: str) -> None:
        os.makedirs(root, exist_ok=True)
        self.root = root

    def _dump_locally(self, f_name: str, *, to: str, **kwargs: Any) -> None:
        directory = os.path.join(self.root, f_name)
        os.makedirs(directory, exist_ok=True)
        filename = f"{to}_{datetime.now().strftime('%d@%H_%M_%S__%f')}"

        with open(os.path.join(directory, filename), "w") as file:
            json.dump({"to": to, **kwargs}, file, indent=4, separators=(",", ": "))

    def send_signup_email(self, to: str, *, email_confirmation_url: str) -> None:
        self._dump_locally("send_signup_email", to=to, email_confirmation_url=email_confirmation_url)

    def send_reset_password_email(self, to: str, *, reset_password_url: str) -> None:
        self._dump_locally("send_reset_password_email", to=to, reset_password_url=reset_password_url)

    def send_interview_passed_email(self, to: str) -> None:
        self._dump_locally("send_interview_passed_email", to=to)

    def send_interview_failed_email(self, to: str, *, message: str) -> None:
        self._dump_locally("send_interview_failed_email", to=to)

    def send_payment_accepted_proof_email(self, to: str, *, message: Optional[str] = None) -> None:
        self._dump_locally("send_payment_accepted_proof_email", to=to, msg=message or "default")

    def send_payment_need_additional_proof_email(self, to: str, *, message: str) -> None:
        self._dump_locally("send_payment_need_additional_proof_email", to=to, msg=message)

    def send_payment_refused_proof_email(self, to: str, *, message: str) -> None:
        self._dump_locally("send_payment_refused_proof_email", to=to, msg=message)

    def send_application_is_over_passed(self, to: str) -> None:
        self._dump_locally("send_application_is_over_passed", to=to)

    def send_application_is_over_failed(self, to: str) -> None:
        self._dump_locally("send_application_is_over_failed", to=to)

    def send_selected_and_payment_details(self, to: str, *, payment_value: int, payment_due_date: str) -> None:
        self._dump_locally(
            "send_selected_and_payment_details", to=to, payment_value=payment_value, payment_due_date=payment_due_date
        )

    def send_selected_interview_details(self, to: str) -> None:
        self._dump_locally("send_selected_interview_details", to=to)

    def send_admissions_are_over_not_selected(self, to: str) -> None:
        self._dump_locally("send_admissions_are_over_not_selected", to=to)
