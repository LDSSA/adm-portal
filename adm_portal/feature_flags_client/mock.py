from datetime import datetime

from .client import FeatureFlagsClient


class MockFeatureFlagsClient(FeatureFlagsClient):
    def __init__(self) -> None:
        self._signups_are_open = False
        self._applications_opening_date = datetime.now()
        self._applications_closing_date = datetime.now()
        self._coding_test_duration = 60 * 2
        self._accepting_payment_profs = False

    def signups_are_open(self) -> bool:
        return self._signups_are_open

    def open_signups(self) -> None:
        self._signups_are_open = True

    def close_signups(self) -> None:
        self._signups_are_open = False

    # applications
    def get_applications_opening_date(self) -> datetime:
        return self._applications_opening_date

    def set_applications_opening_date(self, d: datetime) -> bool:
        self._applications_opening_date = d
        return True

    def get_applications_closing_date(self) -> datetime:
        return self._applications_closing_date

    def set_applications_closing_date(self, d: datetime) -> bool:
        self._applications_closing_date = d
        return True

    def get_coding_test_duration(self) -> int:
        return self._coding_test_duration

    def set_coding_test_duration(self, d: int) -> None:
        self._coding_test_duration = d

    def accepting_payment_profs(self) -> bool:
        return self._accepting_payment_profs

    def open_payment_profs(self) -> None:
        self._accepting_payment_profs = True

    def close_payment_profs(self) -> None:
        self._accepting_payment_profs = False
