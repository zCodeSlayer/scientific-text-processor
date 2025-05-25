import json
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from source_extraction.models import TermModel
from schemas import GraphLink
from models import ScientificCatalogModel, ScientificCatalogProcessingStatus
from background_tasks import generate_graph_task

DBSessionDepends = Annotated[AsyncSession, Depends(get_session)]

router = APIRouter()

@router.get("/scientific-catalog-graph/{catalog_name}")
async def get_scientific_catalog(catalog_name: str, session: DBSessionDepends) -> list[GraphLink]:
    stmt = select(ScientificCatalogModel).where(ScientificCatalogModel.title == catalog_name)
    result = await session.execute(stmt)
    catalog_entry: ScientificCatalogModel = result.unique().scalars().one_or_none()

    if catalog_entry is None:
        raise HTTPException(status_code=404, detail=f"Scientific catalog with title '{catalog_name}' not found")

    response = [
        GraphLink(**dict(
            term_from=dict(title=graph_link.term_from.title, hash=graph_link.term_from.term_hash),
            term_to=dict(title=graph_link.term_to.title, hash=graph_link.term_to.term_hash),
            weight=graph_link.weight,
        ))
        for graph_link in catalog_entry.graph_links
    ]
    return response

@router.post("/generate-graph/{catalog_name}")
async def generate_graph(
    catalog_name: str, file: UploadFile, session: DBSessionDepends, background_tasks: BackgroundTasks
):
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

    background_tasks.add_task(generate_graph_task, raw_terms, catalog_entry.id, session)


@router.get("/scientific-catalogs/titles", response_model=dict[str, list[str]])
async def get_all_scientific_catalog_titles(session: DBSessionDepends):
    """
    Возвращает список всех названий (title) из таблицы ScientificCatalogModel.
    """

    stmt = select(ScientificCatalogModel.title)
    result = await session.execute(stmt)
    titles: list[str] = result.scalars().all()

    response = {
        "catalogsTitles": titles
    }

    return response
