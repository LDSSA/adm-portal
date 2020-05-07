from abc import ABC, abstractmethod

from .client import FeatureFlagsClient


class GetSetFlagsInterface(ABC):
    @abstractmethod
    def set(self, *, key: str, value: str, create_by: str = "") -> None:
        pass

    @abstractmethod
    def get(self, *, key: str) -> str:
        pass


class DBFeatureFlagsClient(FeatureFlagsClient):
    def __init__(self, flags: GetSetFlagsInterface) -> None:
        self._flags = flags

    # values
    true = "true"
    false = "false"

    # signup
    signups_are_open_key = "signups_are_open"

    def signups_are_open(self) -> bool:
        return self._flags.get(key=self.signups_are_open_key) == self.true

    def open_signups(self) -> None:
        self._flags.set(key=self.signups_are_open_key, value=self.true)

    def close_signups(self) -> None:
        self._flags.set(key=self.signups_are_open_key, value=self.false)

    # applications
    applications_are_open_key = "applications_are_open"

    def applications_are_open(self) -> bool:
        return self._flags.get(key=self.applications_are_open_key) == self.true

    def open_applications(self) -> None:
        self._flags.set(key=self.applications_are_open_key, value=self.true)

    def close_applications(self) -> None:
        self._flags.set(key=self.applications_are_open_key, value=self.false)

    # payments
    accepting_payment_profs_key = "accepting_payment_profs"

    def accepting_payment_profs(self) -> bool:
        return self._flags.get(key=self.accepting_payment_profs_key) == self.true

    def open_payment_profs(self) -> None:
        self._flags.set(key=self.accepting_payment_profs_key, value=self.true)

    def close_payment_profs(self) -> None:
        self._flags.set(key=self.accepting_payment_profs_key, value=self.false)
