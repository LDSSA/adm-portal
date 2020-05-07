from .client import FeatureFlagsClient


class MockFeatureFlagsClient(FeatureFlagsClient):
    def __init__(self) -> None:
        self._signups_are_open = False
        self._applications_are_open = False
        self._accepting_payment_profs = False

    def signups_are_open(self) -> bool:
        return self._signups_are_open

    def open_signups(self) -> None:
        self._signups_are_open = True

    def close_signups(self) -> None:
        self._signups_are_open = False

    def applications_are_open(self) -> bool:
        return self._applications_are_open

    def open_applications(self) -> None:
        self._applications_are_open = True

    def close_applications(self) -> None:
        self._applications_are_open = False

    def accepting_payment_profs(self) -> bool:
        return self._accepting_payment_profs

    def open_payment_profs(self) -> None:
        self._accepting_payment_profs = True

    def close_payment_profs(self) -> None:
        self._accepting_payment_profs = False
