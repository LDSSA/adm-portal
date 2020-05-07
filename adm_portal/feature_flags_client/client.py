from abc import ABC, abstractmethod

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
    def applications_are_open(self) -> bool:
        """controls whether or not the candidates can submit exercise solutions"""
        pass

    @abstractmethod
    def open_applications(self) -> None:
        """opens applications. candidates will be able to submit exercise solutions"""
        pass

    @abstractmethod
    def close_applications(self) -> None:
        """closes applications. candidates will NOT be able to submit exercise solutions"""
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
