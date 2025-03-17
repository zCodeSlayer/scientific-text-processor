from typing import Protocol

from ..models import Term


class BaseExtractor(Protocol):
    def extract(self) -> list[Term]: ...
