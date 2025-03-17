import json
from pathlib import Path

from .base import IExtractor
from ..models import Term


class JSONExtractor(IExtractor):
    def __init__(self, file_path: Path) -> None:
        self.file_path: Path = file_path

    def extract(self) -> list[Term]:
        with open(self.file_path) as file:
            raw_terms: list[dict[str, str]] = json.load(file)

            return [Term(**raw_term) for raw_term in raw_terms]
