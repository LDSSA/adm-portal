import os

import boto3
from botocore.errorfactory import ClientError
from django.core.management.base import BaseCommand, CommandError

from applications.domain import Domain


class Command(BaseCommand):
    def add_arguments(self, parser) -> None:
        parser.add_argument("--bucket", type=str)
        parser.add_argument("--dir", type=str)

    def handle(self, *args, **options) -> None:
        bucket = options["bucket"]
        directory = options["dir"]

        if bucket is None and directory is None:
            raise CommandError("you need to specify --bucket or --dir")

        expected_keys = {
            # "key": "description",
            "public-assets/ldssa_logo.png": "this is LDSA Logo, displayed in the login/signup pages",
            Domain.get_candidate_release_zip(
                "coding_test"
            ): "this is the candidate nbgrader `coding_test` release, the one candidates can donwload",
            Domain.get_candidate_release_zip(
                "slu01"
            ): "this is the candidate nbgrader `slu01` release, the one candidates can donwload",
            Domain.get_candidate_release_zip(
                "slu02"
            ): "this is the candidate nbgrader `slu02` release, the one candidates can donwload",
            Domain.get_candidate_release_zip(
                "slu03"
            ): "this is the candidate nbgrader `slu03` release, the one candidates can donwload",
        }

        fail = False
        if bucket is not None:
            s3 = boto3.client("s3")

            for k, d in expected_keys.items():
                try:
                    s3.head_object(Bucket=bucket, Key=k)
                    self.stdout.write(f"{k} -> " + self.style.SUCCESS("found."))
                except ClientError:
                    self.stdout.write(f"{k} -> " + self.style.ERROR("not found."))
                    fail = True

        elif directory is not None:
            for k, d in expected_keys.items():
                if os.path.isfile(os.path.join(directory, k)):
                    self.stdout.write(f"{k} -> " + self.style.SUCCESS("found."))
                else:
                    self.stdout.write(f"{k} -> " + self.style.ERROR("not found."))
                    self.stdout.write(self.style.WARNING(d))
                    fail = True
        else:
            raise Exception

        if fail:
            raise CommandError("At least one key is missing...")
        else:
            self.stdout.write(self.style.SUCCESS("All Good!"))
