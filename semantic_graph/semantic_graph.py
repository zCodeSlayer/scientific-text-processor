from dataclasses import dataclass, field


@dataclass(frozen=True)
class Term:
    title: str
    description: str
    title_lemmas: list[str]
    description_lemmas: list[str]

    def __hash__(self) -> int:
        return frozenset(self.title_lemmas).__hash__()


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
