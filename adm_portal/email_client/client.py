from abc import ABC, abstractmethod


class EmailClient(ABC):
    @abstractmethod
    def send_example_email(self, email_to: str, username: str) -> None:
        pass
