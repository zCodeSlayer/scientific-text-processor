from pydantic import BaseModel, Field


class Term(BaseModel):
    title: str = Field(alias="term")
    description: str = Field(alias="description")
