from dataclasses import dataclass


@dataclass
class Term:
    title: str
    description: str
    title_lemmas: list[str]
    description_lemmas: list[str]

    def __eq__(self, other: "Term") -> bool:
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        hashes: list[int] = [hash(lemma) for lemma in self.title_lemmas]
        hashes.sort()
        return hash(tuple(hashes))
