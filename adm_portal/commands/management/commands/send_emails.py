import re
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from interface import interface

email_client = interface.email_client


class Command(BaseCommand):
    is_email_regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--to", type=str)

    def handle(self, *args, **options) -> None:
        to = options["to"]
        if to is None:
            raise CommandError("--to is required")

        if not re.search(self.is_email_regex, to):
            raise CommandError("--to is not a valid email")

        example_name = "Chicho"
        example_url = "http://admissions.lisbondatascience.org/"
        example_message = "This is a custom message.\nIt even has a new line character!"
        example_value = 500
        example_date_str = datetime.now().strftime("%Y-%m-%d")

        email_client.send_signup_email(to_email=to, email_confirmation_url=example_url)
        email_client.send_reset_password_email(to_email=to, reset_password_url=example_url)
        email_client.send_interview_passed_email(to_email=to, to_name=example_name)
        email_client.send_interview_failed_email(to_email=to, to_name=example_name, message=example_message)
        email_client.send_payment_accepted_proof_email(to_email=to, to_name=example_name, message=example_message)
        email_client.send_payment_need_additional_proof_email(
            to_email=to, to_name=example_name, message=example_message
        )
        email_client.send_payment_refused_proof_email(to_email=to, to_name=example_name, message=example_message)
        email_client.send_application_is_over_passed(to_email=to, to_name=example_name)
        email_client.send_application_is_over_failed(to_email=to, to_name=example_name)
        email_client.send_selected_and_payment_details(
            to_email=to, to_name=example_name, payment_value=example_value, payment_due_date=example_date_str
        )
        email_client.send_selected_interview_details(to_email=to, to_name=example_name)
        email_client.send_admissions_are_over_not_selected(to_email=to, to_name=example_name)
