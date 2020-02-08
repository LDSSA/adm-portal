from abc import ABC, abstractmethod


class FeatureFlagsClient(ABC):
    @abstractmethod
    def accepting_test_submissions(self) -> bool:
        pass

    @abstractmethod
    def accepting_payment_profs(self) -> bool:
        pass


class InCodeFeatureFlagsClient(FeatureFlagsClient):
    def accepting_test_submissions(self) -> bool:
        return True

    def accepting_payment_profs(self) -> bool:
        return True


class MockFeatureFlagsClient(FeatureFlagsClient):
    def __init__(self, accepting_test_submissions: bool, accepting_payment_profs: bool) -> None:
        self._accepting_test_submissions = accepting_test_submissions
        self._accepting_payment_profs = accepting_payment_profs

    def accepting_test_submissions(self) -> bool:
        return self._accepting_test_submissions

    def accepting_payment_profs(self) -> bool:
        return self._accepting_payment_profs
