import json
import os
from datetime import datetime
from typing import Any, Optional

from .client import EmailClient


class LocalEmailClient(EmailClient):
    def __init__(self, root: str, sender: str = "admin@admissions.org") -> None:
        os.makedirs(root, exist_ok=True)
        self.root = root
        self.sender = sender

    def _dump_locally(self, f_name: str, *, to_email: str, **kwargs: Any) -> None:
        directory = os.path.join(self.root, f_name)
        os.makedirs(directory, exist_ok=True)
        filename = f"{to_email}_{datetime.now().strftime('%d@%H_%M_%S__%f')}"

        with open(os.path.join(directory, filename), "w") as file:
            json.dump({"to_email": to_email, **kwargs}, file, indent=4, separators=(",", ": "))

    def send_signup_email(self, to_email: str, *, email_confirmation_url: str) -> None:
        self._dump_locally("send_signup_email", to_email=to_email, email_confirmation_url=email_confirmation_url)

    def send_reset_password_email(self, to_email: str, *, reset_password_url: str) -> None:
        self._dump_locally("send_reset_password_email", to_email=to_email, reset_password_url=reset_password_url)

    def send_interview_passed_email(self, to_email: str, to_name: str) -> None:
        self._dump_locally("send_interview_passed_email", to_email=to_email, to_name=to_name)

    def send_interview_failed_email(self, to_email: str, to_name: str, *, message: str) -> None:
        self._dump_locally("send_interview_failed_email", to_email=to_email, to_name=to_name)

    def send_payment_accepted_proof_email(self, to_email: str, to_name: str, *, message: Optional[str] = None) -> None:
        self._dump_locally(
            "send_payment_accepted_proof_email", to_email=to_email, to_name=to_name, msg=message or "default"
        )

    def send_payment_need_additional_proof_email(self, to_email: str, to_name: str, *, message: str) -> None:
        self._dump_locally("send_payment_need_additional_proof_email", to_email=to_email, to_name=to_name, msg=message)

    def send_payment_refused_proof_email(self, to_email: str, to_name: str, *, message: str) -> None:
        self._dump_locally("send_payment_refused_proof_email", to_email=to_email, to_name=to_name, msg=message)

    def send_application_is_over_passed(self, to_email: str, to_name: str) -> None:
        self._dump_locally("send_application_is_over_passed", to_email=to_email, to_name=to_name)

    def send_application_is_over_failed(self, to_email: str, to_name: str) -> None:
        self._dump_locally("send_application_is_over_failed", to_email=to_email, to_name=to_name)

    def send_selected_and_payment_details(
        self, to_email: str, to_name: str, *, payment_value: int, payment_due_date: str
    ) -> None:
        self._dump_locally(
            "send_selected_and_payment_details",
            to_email=to_email,
            to_name=to_name,
            payment_value=payment_value,
            payment_due_date=payment_due_date,
        )

    def send_selected_interview_details(self, to_email: str, to_name: str) -> None:
        self._dump_locally("send_selected_interview_details", to_email=to_email, to_name=to_name)

    def send_admissions_are_over_not_selected(self, to_email: str, to_name: str) -> None:
        self._dump_locally("send_admissions_are_over_not_selected", to_email=to_email, to_name=to_name)

    def send_contact_us_email(self, from_email: str, user_name: str, user_url: str, message: str) -> None:
        self._dump_locally(
            "send_contact_us_email",
            to_email=self.sender,
            from_email=from_email,
            user_name=user_name,
            user_url=user_url,
            message=message,
        )
