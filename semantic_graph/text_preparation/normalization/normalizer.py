import re


class Normalizer:
    @classmethod
    def normalize_text(cls, text: str) -> str:
        processing_text: str = text

        processing_text = processing_text.lower()
        processing_text = processing_text.strip()
        processing_text = re.sub(r"\s+", " ", processing_text)

        return processing_text
