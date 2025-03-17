from typing import Protocol

from ..models import Term


class IExtractor(Protocol):
    def extract(self) -> list[Term]: ...
