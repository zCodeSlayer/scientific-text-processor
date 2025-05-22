import uvicorn
import json
from contextlib import asynccontextmanager
from pathlib import Path

from typing import Annotated
from fastapi import FastAPI, Depends, UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from source_extraction.models import TermModel
from source_extraction import JSONExtractor
from text_preparation import TextPreparator
from text_preparation.lemmatization.lemmatization_strategies import (
    MyStemLemmatizationStrategy,
)
from term import Term
from semantic_graph_generator import SemanticGraph, SemanticGraphGenerator
from database import db_engine, get_session
from models import (
    Base,
    ScientificCatalogModel,
    TermModel as TermDBModel,
    SemanticGraphLink,
    ScientificCatalogProcessingStatus
)


DBSessionDepends = Annotated[AsyncSession, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_engine.begin() as engine:
        await engine.run_sync(Base.metadata.create_all)
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/scientific-catalog-graph/{catalog_name}")
async def get_scientific_catalog(catalog_name: str, session: DBSessionDepends):
    stmt = select(ScientificCatalogModel).where(ScientificCatalogModel.title == catalog_name)
    result = await session.execute(stmt)
    catalog_entry: ScientificCatalogModel = result.unique().scalars().one_or_none()

    if catalog_entry is None:
        raise HTTPException(status_code=404, detail=f"Scientific catalog with title '{catalog_name}' not found")

    response = [
        {
            "from": graph_link.term_from.title,
            "to": graph_link.term_to.title,
            "weight": graph_link.weight,
        } for graph_link in catalog_entry.graph_links
    ]
    return response


@app.post("/generate-graph/{catalog_name}")
async def generate_graph(catalog_name: str, file: UploadFile, session: DBSessionDepends):
    catalog_file_content: bytes = await file.read()
    # raw_terms: list[TermModel] = JSONExtractor(file.file).extract()
    raw_content: list[dict[str, str]] = json.loads(catalog_file_content)
    raw_terms: list[TermModel] = [TermModel(**term) for term in raw_content]

    async with session.begin(): 
        catalog_entry = ScientificCatalogModel(
            title=catalog_name,
            status=ScientificCatalogProcessingStatus.PROCESSING
        )
        session.add(catalog_entry)

    await session.refresh(catalog_entry)
    catalog_id: int = catalog_entry.id

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
    await insert_graph_into_db(session, semantic_graph, catalog_entry.id)


async def insert_graph_into_db(session: AsyncSession, semantic_graph: SemanticGraph, catalog_id: int):
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



def main() -> None:
    file_path: Path = Path(
        "/Users/kirillmiltsev/Magistracy/Diplom/physical-encyclopaedia-parser/physical-encyclopedia-terms.json"
    )
    raw_terms: list[TermModel] = JSONExtractor(file_path).extract()

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
    print()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # main()
