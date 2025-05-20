import enum

from sqlalchemy import Enum
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

    terms = relationship("TermModel", back_populates="catalog")
    graph_links = relationship("SemanticGraphLink", back_populates="catalog")


class TermModel(Base):
    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    term_hash: Mapped[int] = mapped_column(name="hash")

    catalog = relationship("ScientificCatalogModel", back_populates="terms")


class SemanticGraphLink(Base):
    __tablename__ = "semantic_graph_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[float]

    term_from: Mapped["TermModel"] = relationship()
    term_to: Mapped["TermModel"] = relationship()
    catalog = relationship("ScientificCatalogModel", back_populates="graph_links")
