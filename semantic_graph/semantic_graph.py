from dataclasses import dataclass, field

from .term import Term


@dataclass
class Node:
    term: Term
    links: list["Link"] = field(default_factory=list)
    weight: float = 0.0

    def __hash__(self) -> int:
        return hash(self.term)


@dataclass
class Link:
    next_node: "Node"
    weight: float = 0.0


class SemanticGraph:
    pass
