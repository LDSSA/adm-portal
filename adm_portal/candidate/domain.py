from enum import Enum
from typing import Dict, NamedTuple, Optional

from applications.domain import ApplicationStatus
from applications.domain import Domain as ApplicationsDomain
from applications.domain import SubmissionStatus
from applications.models import Application, SubmissionTypes
from payments.models import Payment
from profiles.models import Profile
from users.models import User


class SelectedStatus(Enum):
    selected = "Selected"
    awaiting = "Awaiting Selection"
    not_selected = "Not Selected"


class AdmissionStatus(Enum):
    ongoing = "Ongoing"
    accepted = "Accepted"
    rejected = "Rejected"


class CandidateState(NamedTuple):
    signed_up: bool = False
    confirmed_email: bool = False
    created_profile: bool = False
    accepted_coc: bool = False
    application_status: Optional[ApplicationStatus] = None
    coding_test_status: Optional[SubmissionStatus] = None
    slu01_status: Optional[SubmissionStatus] = None
    slu02_status: Optional[SubmissionStatus] = None
    slu03_status: Optional[SubmissionStatus] = None
    selected_status: Optional[SelectedStatus] = None
    payment_status: Optional[str] = None
    admission_status: AdmissionStatus = AdmissionStatus.ongoing


class DomainException(Exception):
    pass


class Domain:
    @staticmethod
    def get_candidate_state(candidate: User) -> CandidateState:
        state = CandidateState()._asdict()
        if candidate.id is not None:
            state["signed_up"] = True
        if candidate.email_confirmed:
            state["confirmed_email"] = True

        try:
            _ = candidate.profile
            state["created_profile"] = True
        except Profile.DoesNotExist:
            pass

        if candidate.code_of_conduct_accepted:
            state["accepted_coc"] = True

        try:
            application = candidate.application
            status = ApplicationsDomain.get_application_detailed_status(application)
            state["application_status"] = status["application"]
            state["coding_test_status"] = status[SubmissionTypes.coding_test.uname]
            state["slu01_status"] = status[SubmissionTypes.slu01.uname]
            state["slu02_status"] = status[SubmissionTypes.slu02.uname]
            state["slu03_status"] = status[SubmissionTypes.slu03.uname]

            if state["application_status"] == ApplicationStatus.passed:
                state["selected_status"] = SelectedStatus.awaiting

            if state["application_status"] == ApplicationStatus.failed:
                state["admission_status"] = AdmissionStatus.rejected

        except Application.DoesNotExist:
            pass

        try:
            payment = candidate.payment
            state["selected_status"] = SelectedStatus.selected
            state["payment_status"] = payment.status

            if state["payment_status"] == "accepted":
                state["admission_status"] = AdmissionStatus.accepted

        except Payment.DoesNotExist:
            pass

        # todo: set state["selected_status"] = SelectedStatus.not_selected when admissions are over
        # todo: set state["admission_status"] = AdmissionStatus.rejected when admissions are over

        return CandidateState(**state)

    @staticmethod
    def candidate_state_readable(candidate_state: CandidateState) -> Dict[str, str]:
        return {k: k.replace("_", " ").title().replace("Slu", "SLU ") for k, _ in candidate_state._asdict().items()}
