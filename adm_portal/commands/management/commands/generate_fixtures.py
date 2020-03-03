import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List

from django.core.management.base import BaseCommand

from applications.models import Application, Submission, SubmissionTypes
from payments.domain import Domain as PaymentsDomain
from payments.models import Document
from profiles.models import Profile, gender_choices, ticket_types_choices
from users.models import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Command(BaseCommand):
    help = "Generates Fixtures for tests"

    def _user(self, uid: str) -> User:
        logger.info(f"creating user: email={uid}@adm.com; pw={uid}")
        return User.objects.create_user(email=f"{uid}@adm.com", password=uid)

    @staticmethod
    def summary() -> Dict[str, int]:
        return {
            "users": User.objects.count(),
            "profiles": Profile.objects.count(),
            "applications": Application.objects.count(),
            "submissions": Submission.objects.count(),
        }

    def handle(self, *args, **options) -> None:
        # staff user
        logger.info(f"creating staff user: user=staff; pw=staff")
        User.objects.create_staff_user(email="staff@adm.com", password="staff")

        # user with nothing
        self._user("nothing")

        # user with profiles
        Profile.objects.create(
            user=self._user("profile_student"),
            full_name="User With Student Profile",
            profession="Student",
            gender="f",
            ticket_type="student",
        )
        Profile.objects.create(
            user=self._user("profile_regular"),
            full_name="User With Regular Profile",
            profession="Worker",
            gender="m",
            ticket_type="regular",
        )
        Profile.objects.create(
            user=self._user("profile_company"),
            full_name="User With Company Profile",
            profession="Spotify",
            gender="other",
            ticket_type="company",
        )

        # users with applications
        a0 = Application.objects.create(user=self._user("application_success"), coding_test_started_at=datetime.now())
        Submission.objects.create(
            application=a0,
            submission_type=SubmissionTypes.coding_test.uname,
            score=85,
            feedback_location=_feedback_location,
        )
        Submission.objects.create(
            application=a0, submission_type=SubmissionTypes.slu01.uname, score=91, feedback_location=_feedback_location
        )
        Submission.objects.create(
            application=a0, submission_type=SubmissionTypes.slu02.uname, score=82, feedback_location=_feedback_location
        )
        Submission.objects.create(
            application=a0, submission_type=SubmissionTypes.slu03.uname, score=75, feedback_location=_feedback_location
        )

        a1 = Application.objects.create(
            user=self._user("application_failed"), coding_test_started_at=datetime.now() - timedelta(hours=4)
        )
        Submission.objects.create(
            application=a1,
            submission_type=SubmissionTypes.coding_test.uname,
            score=40,
            feedback_location=_feedback_location,
        )

        Application.objects.create(user=self._user("application_coding_not_started"))

        # users with payments
        prof0 = Profile.objects.create(
            user=self._user("user_with_docs"), full_name="User With Pay docs", ticket_type="regular", gender="f"
        )
        pay0 = PaymentsDomain.create_payment(prof0)
        doc_proof0 = Document(file_location=_payment_proof_location, doc_type="payment_proof")
        PaymentsDomain.add_document(pay0, doc_proof0)

        prof1 = Profile.objects.create(
            user=self._user("user_with_docs_student"),
            full_name="User With Pay docs",
            ticket_type="student",
            gender="other",
        )
        pay1 = PaymentsDomain.create_payment(prof1)
        PaymentsDomain.add_document(pay1, Document(file_location=_payment_proof_location, doc_type="payment_proof"))
        PaymentsDomain.add_document(pay1, Document(file_location=_student_id_proof_location, doc_type="student_id"))

        prof2 = Profile.objects.create(
            user=self._user("user_without_docs"), full_name="User Without Pay docs", ticket_type="company", gender="m"
        )
        PaymentsDomain.create_payment(prof2)

        prof3 = Profile.objects.create(
            user=self._user("user_with_updated_profile"),
            full_name="User With New Profile",
            ticket_type="company",
            gender="m",
        )
        pay3 = PaymentsDomain.create_payment(prof3)
        PaymentsDomain.add_document(pay3, Document(file_location=_payment_proof_location, doc_type="payment_proof"))
        prof3.ticket_type = "student"
        prof3.save()

        # randoms (will be bulk created)
        users: List[User] = []
        # random - users
        logger.info(f"creating {_random_n} random users with profiles and applications")
        for i in range(0, _random_n):
            u = User(email=f"random_{i}")
            users.append(u)

        User.objects.bulk_create(users)
        users = User.objects.filter(email__in=[u.email for u in users])

        # random - profiles
        profiles: List[Profile] = []
        for prof_u in users:
            gender = random.choice(gender_choices)[0]
            ticket_type = random.choice(ticket_types_choices)[0]
            p = Profile(
                user=prof_u,
                full_name=f"Random User {prof_u.id}",
                profession=f"Random Profession {prof_u.id}",
                gender=gender,
                ticket_type=ticket_type,
            )
            profiles.append(p)
        Profile.objects.bulk_create(profiles)

        # random - applications
        applications: List[Application] = []
        for app_u in users:
            minutes_delta = random.randrange(0, 300, 20)
            a = Application(user=app_u, coding_test_started_at=datetime.now() - timedelta(minutes=minutes_delta))
            applications.append(a)
        Application.objects.bulk_create(applications)
        applications = Application.objects.filter(user__in=users)

        # random - submissions
        submissions: List[Submission] = []
        for sub_a in applications:
            for j in range(0, 15):
                s_type = random.choice(
                    [
                        SubmissionTypes.coding_test.uname,
                        SubmissionTypes.slu01.uname,
                        SubmissionTypes.slu02.uname,
                        SubmissionTypes.slu03.uname,
                    ]
                )
                score = random.randrange(60, 100, 2)
                s = Submission(
                    application=sub_a, submission_type=s_type, score=score, feedback_location=_feedback_location
                )
                submissions.append(s)

        Submission.objects.bulk_create(submissions)

        logger.info(self.summary())


_random_n = 500
_namespace = "fixtures/"
_feedback_location = os.path.join(_namespace, "submission_feedback.html")
_payment_proof_location = os.path.join(_namespace, "payment_proof.jpg")
_student_id_proof_location = os.path.join(_namespace, "student_id_proof.png")
