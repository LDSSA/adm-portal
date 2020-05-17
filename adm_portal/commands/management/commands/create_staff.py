from django.core.management.base import BaseCommand, CommandError

from users.models import User


class Command(BaseCommand):
    domain = ""

    def add_arguments(self, parser) -> None:
        parser.add_argument("email", type=str)
        parser.add_argument("password", type=str)

    def handle(self, *args, **options) -> None:
        email = options["email"]
        password = options["password"]

        if self.domain not in email:
            raise CommandError("email not valid")

        User.objects.create_staff_user(email=email, password=password)
        self.stdout.write(self.style.SUCCESS("Done"))