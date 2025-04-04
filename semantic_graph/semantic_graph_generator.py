from typing import Iterable
from dataclasses import dataclass, field
from functools import partial
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor

from term import Term
from semantic_graph import SemanticGraph, Node


TERM_USED_COUNT = namedtuple(
    "TERM_USED_COUNT",
    [
        "term",
        "used_count",
    ],
)


@dataclass
class TermUsage:
    term: Term
    terms_used_this_term: list[TERM_USED_COUNT] = field(default_factory=list)


class SemanticGraphGenerator:
    def __init__(self) -> None:
        self.__semantic_graph: SemanticGraph = SemanticGraph()

    @property
    def semantic_graph(self) -> SemanticGraph:
        return self.__semantic_graph

    def create_semantic_graph(self, terms: list[Term]) -> SemanticGraph:
        prepared_terms: list[Term] = self.__concatenate_terms(terms)
        self.add_nodes(prepared_terms)
        terms_usages: list[TermUsage] = self.investigate_terms_usages(prepared_terms)

        return self.__semantic_graph

    @staticmethod
    def __concatenate_terms(terms: list[Term]) -> list[Term]:
        terms_collection: dict[int, Term] = {}
        for term in terms:
            term_hash: int = hash(term)
            if term_hash not in terms_collection.keys():
                terms_collection[term_hash] = term
                continue

            terms_collection[term_hash].description += f" {term.description}".strip()
            terms_collection[term_hash].description_lemmas += term.description_lemmas

        return list(terms_collection.values())

    def add_nodes(self, terms: Iterable[Term]) -> None:
        for term in terms:
            self.add_node(term)

    def add_node(self, term: Term) -> None:
        node: Node = Node(term=term)
        self.__semantic_graph.add_node(node)

    def investigate_terms_usages(self, terms: Iterable[Term]) -> list[TermUsage]:
        with ProcessPoolExecutor(max_workers=None) as executor:
            find_term_usage_parallely = partial(self.find_term_usage, terms=terms)
            terms_usages = list(executor.map(find_term_usage_parallely, terms[:11]))
            return terms_usages

    @staticmethod
    def find_term_usage(term: Term, terms: Iterable[Term]) -> TermUsage:
        term_usage: TermUsage = TermUsage(term)
        for investigated_term in terms:
            if investigated_term == term:
                continue

            term_size: int = len(term.title_lemmas)
            investigated_description_size: int = len(
                investigated_term.description_lemmas
            )
            term_used_count: int = 0
            for text_position in range(investigated_description_size - term_size + 1):
                description_slice: list[str] = investigated_term.description_lemmas[
                    text_position : text_position + term_size
                ]
                if hash(term) == hash(frozenset(description_slice)):
                    term_used_count += 1

            if term_used_count > 0:
                term_usage_count = TERM_USED_COUNT(investigated_term, term_used_count)
                term_usage.terms_used_this_term.append(term_usage_count)

        return term_usage
