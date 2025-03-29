from typing import Iterable

from .term import Term
from .semantic_graph import SemanticGraph, Node


class SemanticGraphGenerator:
    def __init__(self) -> None:
        self.__semantic_graph: SemanticGraph = SemanticGraph()

    @property
    def semantic_graph(self) -> SemanticGraph:
        return self.__semantic_graph

    def create_semantic_graph(self, terms: list[Term]) -> SemanticGraph:
        prepared_terms: list[Term] = self.__concatenate_terms(terms)
        self.add_nodes(prepared_terms)

        return self.__semantic_graph

    @staticmethod
    def __concatenate_terms(terms: list[Term]) -> list[Term]:
        terms_collection: dict[int, Term] = {}
        for term in terms:
            term_hash: int = hash(term)
            if term_hash not in terms_collection.keys():
                terms_collection[term_hash] = term
                continue

            terms_collection[term_hash].description += term.description
            terms_collection[term_hash].description_lemmas += term.description_lemmas

        return list(terms_collection.values())

    def add_nodes(self, terms: Iterable[Term]) -> None:
        for term in terms:
            self.add_node(term)

    def add_node(self, term: Term) -> None:
        node: Node = Node(term=term)
        self.__semantic_graph.add_node(node)
