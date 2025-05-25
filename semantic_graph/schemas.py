from pydantic import BaseModel, Field

class Term(BaseModel):
    title: str
    term_hash: int = Field(alias="hash")

class GraphLink(BaseModel):
    term_from: Term
    term_to: Term
    weight: float
