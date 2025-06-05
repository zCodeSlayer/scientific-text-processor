from pydantic import BaseModel, Field


class TermModel(BaseModel):
    title: str = Field(alias="term")
    description: str = Field(alias="description")
