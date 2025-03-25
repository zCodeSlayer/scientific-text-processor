import re


class Normalizer:
    def __init__(self, text: str) -> None:
        self.__raw_text: str = text

    @property
    def raw_text(self) -> str:
        return self.__raw_text

    def normalize_text(self) -> str:
        processing_text: str = self.__raw_text

        processing_text = processing_text.lower()
        processing_text = processing_text.strip()
        processing_text = re.sub(r"\s+", " ", processing_text)

        return processing_text
