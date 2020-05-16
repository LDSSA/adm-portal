import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional


class EmailClient(ABC):
    # account
    @abstractmethod
    def send_signup_email(self, to: str, email_confirmation_url: str) -> None:
        pass

    @abstractmethod
    def send_reset_password_email(self, to: str, reset_pw_url: str) -> None:
        pass

    # payments
    @abstractmethod
    def send_payment_accepted_proof_email(self, to: str, msg: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def send_payment_need_additional_proof_email(self, to: str, msg: str) -> None:
        pass

    @abstractmethod
    def send_payment_refused_proof_email(self, to: str, msg: str) -> None:
        pass

    # bulk emails
    # application is over
    def send_application_is_over_passed(self, to: str) -> None:
        pass

    def send_application_is_over_failed(self, to: str) -> None:
        pass

    # admissions are over
    def send_admissions_are_over_not_selected(self, to: str) -> None:
        pass


class LocalEmailClient(EmailClient):
    def __init__(self, root: str) -> None:
        os.makedirs(root, exist_ok=True)
        self.root = root

    def _dump_locally(self, f_name: str, **kwargs: Any) -> None:
        directory = os.path.join(self.root, f_name)
        os.makedirs(directory, exist_ok=True)
        filename = datetime.now().strftime("%d@%H_%M_%S__%f")

        with open(os.path.join(directory, filename), "w") as file:
            json.dump(kwargs, file, indent=4, separators=(",", ": "))

    def send_signup_email(self, to: str, email_confirmation_url: str) -> None:
        self._dump_locally("send_signup_email", to=to, email_confirmation_url=email_confirmation_url)

    def send_reset_password_email(self, to: str, reset_pw_url: str) -> None:
        self._dump_locally("send_signup_email", to=to, reset_pw_url=reset_pw_url)

    def send_payment_accepted_proof_email(self, to: str, msg: Optional[str] = None) -> None:
        self._dump_locally("send_payment_accepted_proof_email", to=to, msg=msg or "default")

    def send_payment_need_additional_proof_email(self, to: str, msg: str) -> None:
        self._dump_locally("send_payment_need_additional_proof_email", to=to, msg=msg)

    def send_payment_refused_proof_email(self, to: str, msg: str) -> None:
        self._dump_locally("send_payment_refused_proof_email", to=to, msg=msg)

    def send_application_is_over_passed(self, to: str) -> None:
        self._dump_locally("send_application_is_over_passed", to=to)

    def send_application_is_over_failed(self, to: str) -> None:
        self._dump_locally("send_application_is_over_failed", to=to)

    # admissions are over
    def send_admissions_are_over_not_selected(self, to: str) -> None:
        self._dump_locally("send_admissions_are_over_not_selected", to=to)
