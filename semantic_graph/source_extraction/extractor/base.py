from typing import Protocol

from ..models import TermModel


class IExtractor(Protocol):
    def extract(self) -> list[TermModel]: ...
