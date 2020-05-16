import logging
import os
import random
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.models import Application, Submission, SubmissionType, SubmissionTypes
from payments.domain import Domain as PaymentsDomain
from payments.models import Document, Payment
from profiles.models import Profile, gender_choices, ticket_types_choices
from storage_client import LocalStorageClient
from users.models import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

_assets = os.path.join(".", "commands", "assets")
ASSET_SUBMISSION_FEEDBACK_HTML = os.path.join(_assets, "submission-feedback.html")
ASSET_PAYMENT_PROOF_PNG = os.path.join(_assets, "payment-proof.png")
ASSET_STUDENT_ID_PNG = os.path.join(_assets, "student-id.png")


storage_cli = LocalStorageClient(settings.STORAGE_CLIENT_NAMESPACE, run_server=False)

UserOption = Callable[[User], None]


def with_email_confirmation() -> UserOption:
    def f(u: User) -> None:
        u.email_confirmed = True

    return f


def with_accepted_coc() -> UserOption:
    def f(u: User) -> None:
        with_email_confirmation()(u)
        u.code_of_conduct_accepted = True

    return f


def with_profile(
    *,
    gender: str = "other",
    ticket_type: str = "regular",
    full_name: Optional[str] = None,
    profession: Optional[str] = None,
) -> UserOption:
    def f(u: User) -> None:
        with_accepted_coc()(u)
        Profile.objects.create(
            user=u,
            full_name=full_name or f"default - {gender} - {ticket_type}",
            profession=profession or ticket_type.title(),
            gender=gender,
            ticket_type=ticket_type,
        )

    return f


def with_application(*, coding_test_started_at: Optional[datetime] = None) -> UserOption:
    def f(u: User) -> None:
        if not Profile.objects.filter(user=u).exists():
            with_profile()(u)
        Application.objects.create(user=u, coding_test_started_at=coding_test_started_at)

    return f


def with_submission(
    submission_type: SubmissionType, score: int, feedback_location: str = ASSET_SUBMISSION_FEEDBACK_HTML
) -> UserOption:
    def f(u: User) -> None:
        if not Application.objects.filter(user=u).exists():
            with_application()(u)
        Submission.objects.create(
            application=Application.objects.get(user=u),
            submission_type=submission_type.uname,
            score=score,
            feedback_location=feedback_location,
        )
        storage_cli.copy(feedback_location)

    return f


def with_payment() -> UserOption:
    def f(u: User) -> None:
        if not Profile.objects.filter(user=u).exists():
            with_profile()(u)
        if not Application.objects.filter(user=u).exists():
            with_application(coding_test_started_at=datetime.now())(u)
        with_submission(SubmissionTypes.coding_test, 100)(u)
        with_submission(SubmissionTypes.slu01, 100)(u)
        with_submission(SubmissionTypes.slu02, 100)(u)
        with_submission(SubmissionTypes.slu03, 100)(u)

        PaymentsDomain.create_payment(u.profile)

    return f


def with_document(doc_type: str = "payment_proof", file_location: str = ASSET_PAYMENT_PROOF_PNG) -> UserOption:
    def f(u: User) -> None:
        if not Payment.objects.filter(user=u).exists():
            with_payment()(u)

        PaymentsDomain.add_document(
            Payment.objects.get(user=u), Document(file_location=file_location, doc_type=doc_type)
        )
        storage_cli.copy(file_location)

    return f


def new_user(uid: str, *opts: Callable[[User], None]) -> User:
    u = User.objects.create_user(email=f"{uid}@adm.com", password=uid)
    for opt in opts:
        opt(u)
    u.save()
    logger.info(f"creating user: email={uid}@adm.com; pw={uid}")


class Command(BaseCommand):
    help = "Generates Fixtures for tests"

    @staticmethod
    def summary() -> Dict[str, int]:
        return {
            "users": User.objects.count(),
            "profiles": Profile.objects.count(),
            "applications": Application.objects.count(),
            "submissions": Submission.objects.count(),
        }

    def handle(self, *args, **options) -> None:
        # admin / staff user
        logger.info(f"creating admin user: user=admin; pw=admin")
        User.objects.create_admin_user(email="admin@adm.com", password="admin")

        logger.info(f"creating staff user: user=staff; pw=staff")
        User.objects.create_staff_user(email="staff@adm.com", password="staff")

        # user with nothing
        new_user("nothing")

        # user with confirmed email
        new_user("with_confirmed_email", with_email_confirmation())

        # user with confirmed email
        new_user("with_accepted_coc", with_accepted_coc())

        # user with profiles
        new_user(
            "profile_student",
            with_profile(
                full_name="User With Student Profile", profession="Student", gender="f", ticket_type="student"
            ),
        )
        new_user(
            "profile_regular",
            with_profile(
                full_name="User With Regular Profile", profession="Worker", gender="m", ticket_type="regular"
            ),
        )
        new_user(
            "profile_company",
            with_profile(
                full_name="User With Company Profile", profession="Spotify", gender="other", ticket_type="company"
            ),
        )

        # users with applications
        new_user("with_application_not_started", with_application())
        new_user("with_submissions_ongoing", with_application(coding_test_started_at=datetime.now()))
        new_user(
            "with_submissions_passed",
            with_application(coding_test_started_at=datetime.now()),
            with_submission(SubmissionTypes.coding_test, 85),
            with_submission(SubmissionTypes.slu01, 91),
            with_submission(SubmissionTypes.slu02, 82),
            with_submission(SubmissionTypes.slu03, 76),
        )
        new_user(
            "with_submissions_failed", with_application(coding_test_started_at=datetime.now() - timedelta(hours=4))
        )

        # users with payments
        new_user("with_regular_payment", with_profile(ticket_type="regular"), with_payment())
        new_user(
            "with_regular_payment_with_docs", with_profile(ticket_type="regular"), with_payment(), with_document()
        )
        new_user(
            "with_student_payment_with_docs",
            with_profile(ticket_type="student"),
            with_payment(),
            with_document(),
            with_document(doc_type="student_id", file_location=ASSET_STUDENT_ID_PNG),
        )
        new_user("with_company_payment", with_profile(ticket_type="company"), with_payment(), with_document())

        # randoms (will be bulk created)
        users: List[User] = []
        # random - users
        logger.info(f"creating {_random_n} random users with profiles and applications")
        for i in range(0, _random_n):
            u = User(email=f"random_{i}@adm.com")
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
                s = Submission(application=sub_a, submission_type=s_type, score=score, feedback_location="404")
                submissions.append(s)

        Submission.objects.bulk_create(submissions)

        logger.info(self.summary())


_random_n = 500
