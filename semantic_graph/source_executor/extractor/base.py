from typing import Protocol

from semantic_graph.models import Term


class BaseExtractor(Protocol):
    def extract(self) -> list[Term]: ...
