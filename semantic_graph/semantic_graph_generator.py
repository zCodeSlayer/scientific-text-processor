import math

from typing import Iterable, NamedTuple
from dataclasses import dataclass, field
from functools import partial
from concurrent.futures import ProcessPoolExecutor

from term import Term
from semantic_graph import SemanticGraph, Node


class TermUsedCount(NamedTuple):
    term: Term
    used_count: int


@dataclass
class TermUsage:
    term: Term
    terms_used_this_term: list[TermUsedCount] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.term)


class SemanticGraphGenerator:
    def __init__(self) -> None:
        self.__semantic_graph: SemanticGraph = SemanticGraph()

    @property
    def semantic_graph(self) -> SemanticGraph:
        return self.__semantic_graph

    def create_semantic_graph(self, terms: list[Term]) -> SemanticGraph:
        prepared_terms: list[Term] = self.__concatenate_terms(terms)
        terms_usages: list[TermUsage] = self.investigate_terms_usages(prepared_terms)
        short_terms_descriptions: list[TermUsage] = self.reverse_terms_usages(
            terms_usages
        )
        self.add_nodes(prepared_terms)
        self.create_links(short_terms_descriptions)

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
            terms_usages = list(executor.map(find_term_usage_parallely, terms))
            return terms_usages

    @staticmethod
    def find_term_usage(term: Term, terms: Iterable[Term]) -> TermUsage:
        term_usage: TermUsage = TermUsage(term)
        term_text: str = " ".join(term.title_lemmas).lower().strip()
        for investigated_term in terms:
            if investigated_term == term:
                continue

            investigated_description_text: str = (
                " ".join(investigated_term.description_lemmas).lower().strip()
            )
            term_used_count: int = investigated_description_text.count(term_text)

            if term_used_count > 0:
                term_usage_count = TermUsedCount(investigated_term, term_used_count)
                term_usage.terms_used_this_term.append(term_usage_count)

        return term_usage

    @staticmethod
    def reverse_terms_usages(terms_usages: list[TermUsage]) -> list[TermUsage]:
        terms: dict[int, TermUsage] = {}
        for term_usage in terms_usages:
            for used_term in term_usage.terms_used_this_term:
                if terms.get(hash(used_term.term)) is None:
                    terms[hash(used_term.term)] = TermUsage(used_term.term)
                terms[hash(used_term.term)].terms_used_this_term.append(
                    TermUsedCount(term=term_usage.term, used_count=used_term.used_count)
                )

        return list(terms.values())

    def create_links(self, terms: list[TermUsage]) -> None:
        all_term_idf: dict[int, float] = self.calc_all_idf(terms)
        for term in terms:
            for used_term in term.terms_used_this_term:
                if used_term == term:  # not create click link in graph
                    continue

                tf: float = used_term.used_count / sum(
                    used.used_count for used in term.terms_used_this_term
                )
                idf: float = all_term_idf[hash(used_term)]
                tf_idf: float = tf * idf

                node_1: Node | None = self.__semantic_graph.get_node_by_hash(
                    hash(used_term)
                )
                node_2: Node | None = self.__semantic_graph.get_node_by_hash(hash(term))
                if node_1 is None or node_2 is None:
                    raise Exception("Not found node for create link in semantic graph")

                self.__semantic_graph.add_link(node_1, node_2, tf_idf)

    @staticmethod
    def calc_all_idf(terms: list[TermUsage]) -> dict[int, float]:
        all_terms_idf: dict[int, float] = {}
        for term in terms:
            term_usage_count: int = 0
            for term_ in terms:
                for usage in term_.terms_used_this_term:
                    if usage.term == term:
                        term_usage_count += 1
                        break

            if term_usage_count == 0:
                term_usage_count = 1

            idf = math.log10(len(terms) / term_usage_count)
            all_terms_idf[hash(term)] = idf

        return all_terms_idf
