from typing import Protocol


class ILemmatizationStrategy(Protocol):
    def make_lemmatization(self, text: str) -> list[str]: ...
