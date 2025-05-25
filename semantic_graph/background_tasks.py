from sqlalchemy.ext.asyncio import AsyncSession

from source_extraction.models import TermModel
from text_preparation import TextPreparator
from text_preparation.lemmatization.lemmatization_strategies import (
    MyStemLemmatizationStrategy,
)
from term import Term
from semantic_graph_generator import SemanticGraph, SemanticGraphGenerator
from models import (
    ScientificCatalogModel,
    TermModel as TermDBModel,
    SemanticGraphLink,
)

async def generate_graph_task(raw_terms: list[TermModel], catalog_id: int, session: AsyncSession):
    terms: list[Term] = []
    text_preparator: TextPreparator = TextPreparator(MyStemLemmatizationStrategy())
    for raw_term in raw_terms:
        title_lemmas: list[str] = text_preparator.prepare_lemmas(raw_term.title)
        description_lemmas: list[str] = text_preparator.prepare_lemmas(
            raw_term.description
        )
        term: Term = Term(
            title=raw_term.title,
            description=raw_term.description,
            title_lemmas=title_lemmas,
            description_lemmas=description_lemmas,
        )
        terms.append(term)

    semantic_graph_generator: SemanticGraphGenerator = SemanticGraphGenerator()
    semantic_graph: SemanticGraph = semantic_graph_generator.create_semantic_graph(
        terms
    )
    await insert_graph_into_database(session, semantic_graph, catalog_id)

async def insert_graph_into_database(
        session: AsyncSession, semantic_graph: SemanticGraph, catalog_id: int
):
    catalog = await session.get(ScientificCatalogModel, catalog_id)

    term_db_map: dict[int, TermDBModel] = {}
    for node in semantic_graph.nodes:
        term_db = TermDBModel(title=node.term.title, term_hash=hash(node.term))
        term_db_map[hash(node.term)] = term_db
        catalog.terms.append(term_db)
    await session.flush()

    for node in semantic_graph.nodes:
        first_term_hash: int = hash(node.term)
        for link in node.links:
            second_term_hash: int = hash(link.next_node.term)
            weight: float = link.weight

            catalog.graph_links.append(
                SemanticGraphLink(
                    term_from=term_db_map[first_term_hash],
                    term_to=term_db_map[second_term_hash],
                    weight=weight
                )
            )

    await session.flush()
    await session.commit()
