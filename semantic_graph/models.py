import enum

from sqlalchemy import Enum, BIGINT, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ScientificCatalogProcessingStatus(enum.Enum):
    PROCESSING = "PROCESSING"
    DROPPED = "DROPPED"
    DONE = "DONE"


class ScientificCatalogModel(Base):
    __tablename__ = "scientific_catalogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    status: Mapped[ScientificCatalogProcessingStatus] = mapped_column(
        Enum(ScientificCatalogProcessingStatus)
    )

    terms: Mapped[list["TermModel"]] = relationship(
        "TermModel",
        primaryjoin="ScientificCatalogModel.id == TermModel.catalog_id",
        back_populates="catalog",
        lazy="joined"
    )
    graph_links: Mapped[list["SemanticGraphLink"]] = relationship(
        "SemanticGraphLink",
        primaryjoin="ScientificCatalogModel.id == SemanticGraphLink.catalog_id",
        back_populates="catalog",
        lazy="joined"
    )


class TermModel(Base):
    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    term_hash: Mapped[int] = mapped_column(BIGINT, name="hash")
    catalog_id: Mapped[int] = mapped_column(ForeignKey("scientific_catalogs.id"))

    catalog: Mapped["ScientificCatalogModel"] = relationship(
        "ScientificCatalogModel", back_populates="terms", lazy="joined"
    )


class SemanticGraphLink(Base):
    __tablename__ = "semantic_graph_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[float]
    term_from_id: Mapped[int] = mapped_column(ForeignKey("terms.id"))
    term_to_id: Mapped[int] = mapped_column(ForeignKey("terms.id"))
    catalog_id: Mapped[int] = mapped_column(ForeignKey("scientific_catalogs.id"))

    term_from: Mapped["TermModel"] = relationship(
        foreign_keys=[term_from_id], lazy="joined"
    )
    term_to: Mapped["TermModel"] = relationship(
        foreign_keys=[term_to_id], lazy="joined"
    )
    catalog: Mapped["ScientificCatalogModel"] = relationship(
        "ScientificCatalogModel", back_populates="graph_links", lazy="joined"
    )
