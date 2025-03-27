from .term import Term
from .semantic_graph import SemanticGraph


class SemanticGraphGenerator:
    def __init__(self) -> None:
        self.__semantic_graph: SemanticGraph = SemanticGraph()

    @property
    def semantic_graph(self) -> SemanticGraph:
        return self.__semantic_graph

    def create_semantic_graph(self, terms: list[Term]) -> SemanticGraph:
        prepared_terms: list[terms] = self.__concatenate_terms(terms)

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
