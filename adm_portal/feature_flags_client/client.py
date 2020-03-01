from abc import ABC, abstractmethod
from datetime import datetime


class FeatureFlagsClient(ABC):
    @abstractmethod
    def applications_are_open(self) -> bool:
        pass

    @abstractmethod
    def accepting_payment_profs(self) -> bool:
        pass


class InCodeFeatureFlagsClient(FeatureFlagsClient):
    applications_open_date = datetime(day=1, month=1, year=2020)
    applications_close_date = datetime(day=21, month=6, year=2020)

    def applications_are_open(self) -> bool:
        return self.applications_open_date < datetime.now() < self.applications_close_date

    def accepting_payment_profs(self) -> bool:
        return True


class MockFeatureFlagsClient(FeatureFlagsClient):
    def __init__(self, accepting_test_submissions: bool, accepting_payment_profs: bool) -> None:
        self._accepting_test_submissions = accepting_test_submissions
        self._accepting_payment_profs = accepting_payment_profs

    def applications_are_open(self) -> bool:
        return self._accepting_test_submissions

    def accepting_payment_profs(self) -> bool:
        return self._accepting_payment_profs


# https://configcat.com/#pricing
