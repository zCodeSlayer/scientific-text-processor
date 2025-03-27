from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Term:
    title: str
    description: str
    title_lemmas: list[str]
    description_lemmas: list[str]

    def __hash__(self) -> int:
        return frozenset(self.title_lemmas).__hash__()
