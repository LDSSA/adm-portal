from typing import Dict, NamedTuple, Optional

from applications.domain import ApplicationStatus
from applications.domain import Domain as ApplicationsDomain
from applications.domain import SubmissionStatus
from applications.models import Application, SubmissionTypes
from profiles.models import Profile
from selection.domain import SelectionDomain
from selection.models import Selection
from selection.status import SelectionStatusType
from users.models import User


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
    selection_status: Optional[SelectionStatusType] = None


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

        except Application.DoesNotExist:
            pass

        try:
            state["selection_status"] = SelectionDomain.get_status(candidate.selection)

        except Selection.DoesNotExist:
            pass

        return CandidateState(**state)

    @staticmethod
    def candidate_state_readable(candidate_state: CandidateState) -> Dict[str, str]:
        return {k: k.replace("_", " ").title().replace("Slu", "SLU ") for k, _ in candidate_state._asdict().items()}
