from abc import ABC, abstractmethod
from datetime import datetime

# https://configcat.com/#pricing


class FeatureFlagsClient(ABC):
    # signup
    @abstractmethod
    def signups_are_open(self) -> bool:
        """controls whether or not new signups are allowed"""
        pass

    @abstractmethod
    def open_signups(self) -> None:
        """opens signups. new users will be allowed to signup"""
        pass

    @abstractmethod
    def close_signups(self) -> None:
        """closes signups. new users will be NOT allowed to signup"""
        pass

    # applications
    @abstractmethod
    def get_applications_opening_date(self) -> datetime:
        pass

    @abstractmethod
    def set_applications_opening_date(self, d: datetime) -> bool:
        pass

    @abstractmethod
    def get_applications_closing_date(self) -> datetime:
        pass

    @abstractmethod
    def set_applications_closing_date(self, d: datetime) -> bool:
        pass

    @abstractmethod
    def get_coding_test_duration(self) -> int:
        """coding test duration in minutes"""
        pass

    @abstractmethod
    def set_coding_test_duration(self, d: int) -> None:
        """coding test duration in minutes"""
        pass

    # payments
    @abstractmethod
    def accepting_payment_profs(self) -> bool:
        """controls whether or not the candidates can upload new payment profs"""
        pass

    @abstractmethod
    def open_payment_profs(self) -> None:
        """opens payment prof uploads. candidates will be able to upload new payment profs"""
        pass

    @abstractmethod
    def close_payment_profs(self) -> None:
        """closes payment prof uploads. candidates will NOT be able to upload new payment profs"""
        pass
