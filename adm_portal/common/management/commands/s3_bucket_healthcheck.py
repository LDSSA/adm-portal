import boto3
from botocore.errorfactory import ClientError
from django.core.management.base import BaseCommand, CommandError

from applications.domain import Domain


class Command(BaseCommand):
    def add_arguments(self, parser) -> None:
        parser.add_argument("--bucket", type=str)

    def handle(self, *args, **options) -> None:
        bucket = options["bucket"]
        if bucket is None:
            raise CommandError("--bucket is required")

        expected_keys = {
            # "key": "description",
            "public-assets/ldssa_logo.png": "LDSA Logo, displayed in the login/signup pages",
            Domain.get_candidate_release_zip("coding_test"): "Candidate nbgrader `coding_test` release",
            Domain.get_candidate_release_zip("slu01"): "Candidate nbgrader `slu01` release",
            Domain.get_candidate_release_zip("slu02"): "Candidate nbgrader `slu02` release",
            Domain.get_candidate_release_zip("slu03"): "Candidate nbgrader `slu03` release",
        }

        s3 = boto3.client("s3")

        fail = False

        for k, d in expected_keys.items():
            try:
                s3.head_object(Bucket=bucket, Key=k)
                self.stdout.write(f"{k} -> " + self.style.SUCCESS("found."))
            except ClientError:
                self.stdout.write(f"{k} -> " + self.style.ERROR("not found."))
                fail = True

        if fail:
            raise CommandError("At least one key is missing...")
        else:
            self.stdout.write(self.style.SUCCESS("All Good!"))
