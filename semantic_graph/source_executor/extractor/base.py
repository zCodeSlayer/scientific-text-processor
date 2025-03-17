from typing import Protocol

from semantic_graph.models import Term


class IExtractor(Protocol):
    def extract(self) -> list[Term]: ...
