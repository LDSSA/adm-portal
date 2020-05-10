from abc import ABC, abstractmethod
from datetime import datetime
from logging import getLogger

from .client import FeatureFlagsClient

logger = getLogger(__name__)


class GetSetFlagsInterface(ABC):
    @abstractmethod
    def set(self, *, key: str, value: str, create_by: str = "") -> None:
        pass

    @abstractmethod
    def get(self, *, key: str) -> str:
        pass


class DBFeatureFlagsClient(FeatureFlagsClient):
    # values
    true = "true"
    false = "false"

    # signup
    signups_are_open_key = "signups_are_open"

    # applications
    applications_opening_date = "applications_opening_date"
    applications_closing_date = "applications_closing_date"
    datetime_fmt = "%Y/%m/%d %H:%M:%S"
    default_opening_date_s = default_closing_date_s = datetime(year=2021, month=1, day=1).strftime(datetime_fmt)
    coding_test_duration = "coding_test_duration"
    default_coding_test_duration_s = str(60 * 2)

    # payments
    accepting_payment_profs_key = "accepting_payment_profs"

    def __init__(self, flags: GetSetFlagsInterface) -> None:
        self._flags = flags

        # set defaults
        if self._flags.get(key=self.applications_opening_date) == "":
            logger.info(f"setting {self.applications_opening_date} default")
            self._flags.set(key=self.applications_opening_date, value=self.default_opening_date_s)

        if self._flags.get(key=self.applications_closing_date) == "":
            logger.info(f"setting {self.applications_closing_date} default")
            self._flags.set(key=self.applications_closing_date, value=self.default_closing_date_s)

        if self._flags.get(key=self.coding_test_duration) == "":
            logger.info(f"setting {self.coding_test_duration} default")
            self._flags.set(key=self.coding_test_duration, value=self.default_coding_test_duration_s)

    # signup
    def signups_are_open(self) -> bool:
        return self._flags.get(key=self.signups_are_open_key) == self.true

    def open_signups(self) -> None:
        self._flags.set(key=self.signups_are_open_key, value=self.true)

    def close_signups(self) -> None:
        self._flags.set(key=self.signups_are_open_key, value=self.false)

    # applications
    def get_applications_opening_date(self) -> datetime:
        s = self._flags.get(key=self.applications_opening_date)
        return datetime.strptime(s, self.datetime_fmt)

    def set_applications_opening_date(self, d: datetime) -> bool:
        if d <= self.get_applications_closing_date():
            s = d.strftime(self.datetime_fmt)
            self._flags.set(key=self.applications_opening_date, value=s)
            return True
        return False

    def get_applications_closing_date(self) -> datetime:
        s = self._flags.get(key=self.applications_closing_date)
        return datetime.strptime(s, self.datetime_fmt)

    def set_applications_closing_date(self, d: datetime) -> bool:
        if d >= self.get_applications_opening_date():
            s = d.strftime(self.datetime_fmt)
            self._flags.set(key=self.applications_closing_date, value=s)
            return True
        return False

    def get_coding_test_duration(self) -> int:
        s = self._flags.get(key=self.coding_test_duration)
        return int(s)

    def set_coding_test_duration(self, d: int) -> None:
        s = str(d)
        self._flags.set(key=self.coding_test_duration, value=s)

    # payments
    def accepting_payment_profs(self) -> bool:
        return self._flags.get(key=self.accepting_payment_profs_key) == self.true

    def open_payment_profs(self) -> None:
        self._flags.set(key=self.accepting_payment_profs_key, value=self.true)

    def close_payment_profs(self) -> None:
        self._flags.set(key=self.accepting_payment_profs_key, value=self.false)
