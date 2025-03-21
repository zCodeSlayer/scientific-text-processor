from typing import Protocol


class ILemmatizationStrategy(Protocol):
    @classmethod
    def make_lemmatization(self, text: str) -> list[str]: ...
