from datetime import datetime
from logging import getLogger

from applications.domain import Domain as ApplicationDomain
from applications.domain import DomainException as ApplicationDomainException
from applications.domain import DomainQueries as ApplicationDomainQueries
from interface import interface
from selected.domain import Domain as SelectedDomain
from selected.domain import DomainQueries as SelectedDomainQueries
from selected.models import PassedCandidateStatus

logger = getLogger(__name__)


class EventsException(Exception):
    pass


class Events:
    @staticmethod
    def applications_are_over_sent_emails() -> int:
        return ApplicationDomainQueries.applications_with_sent_emails_count()

    @staticmethod
    def applications_are_over_total_emails() -> int:
        return ApplicationDomainQueries.applications_count()

    @staticmethod
    def trigger_applications_are_over() -> None:
        if datetime.now() < interface.feature_flag_client.get_applications_closing_date():
            logger.error("trying to trigger `applications over` event but applications are still open")
            raise EventsException("Can't trigger `applications over` event")

        sent_count = 0
        q = ApplicationDomainQueries.all()
        for a in q:
            try:
                ApplicationDomain.application_over(a)
                sent_count += 1
            except ApplicationDomainException:
                pass  # means that email was already sent

            a.refresh_from_db()
            if a.application_over_email_sent == "passed":
                SelectedDomain.new_candidate(a.user)

        logger.info(f"sent {sent_count} `application_over` emails")

    @staticmethod
    def admissions_are_over_sent_emails() -> int:
        return SelectedDomainQueries.get_by_status_in(
            [PassedCandidateStatus.accepted, PassedCandidateStatus.rejected, PassedCandidateStatus.not_selected]
        ).count()

    @staticmethod
    def admissions_are_over_total_emails() -> int:
        return SelectedDomainQueries.get_all().count()

    @staticmethod
    def trigger_admissions_are_over() -> None:
        if datetime.now() < interface.feature_flag_client.get_applications_closing_date():
            logger.error("trying to trigger `admissions over` event but applications are still open")
            raise EventsException("Can't trigger `admissions over` event (applications open)")

        if SelectedDomainQueries.get_drawn().exists():
            logger.error("trying to trigger `admissions over` event but drawn candidates exist")
            raise EventsException("Can't trigger `admissions over` event (drawn candidates)")

        if SelectedDomainQueries.get_selected().exists():
            logger.error("trying to trigger `admissions over` event but selected candidates exist")
            raise EventsException("Can't trigger `admissions over` event (selected candidates)")

        sent_count = 0
        for candidate in SelectedDomainQueries.get_all():
            if candidate.status == PassedCandidateStatus.passed_test:
                # this candidate was never selected
                SelectedDomain.update_status(candidate, PassedCandidateStatus.not_selected)
                interface.email_client.send_admissions_are_over_not_selected(candidate.user.email)

            sent_count += 1

        logger.info(f"sent {sent_count} `admissions_over` emails")
