from django.core.management.base import BaseCommand, CommandError

from users.models import User


class Command(BaseCommand):
    domain = "lisbondatascience.org"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--email", type=str)
        parser.add_argument("--password", type=str)

    def handle(self, *args, **options) -> None:
        email = options["email"]
        if email is None:
            raise CommandError("--email is required")

        password = options["password"]
        if password is None:
            raise CommandError("--password is required")

        if not email.endswith(self.domain):
            raise CommandError(f"email not valid, must end with `{self.domain}`")

        User.objects.create_admin_user(email=email, password=password)
        self.stdout.write(self.style.SUCCESS("Done"))
