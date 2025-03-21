from typing import Protocol


class LemmatizationStrategy(Protocol):
    @classmethod
    def make_lemmatization(self, text: str) -> list[str]: ...
