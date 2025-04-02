from .normalization import Normalizer
from .lemmatization import Lemmatizer
from .lemmatization.lemmatization_strategies import ILemmatizationStrategy


class TextPreparator:
    def __init__(self, lemmatization_strategy: ILemmatizationStrategy) -> None:
        self.__lemmatization_strategy: ILemmatizationStrategy = lemmatization_strategy

    def prepare_lemmas(self, text: str) -> list[str]:
        normalized_text: str = self.__make_normalization(text)
        lemmas: list[str] = self.__make_lemmatization(normalized_text)
        min_lemma_size = 2
        filtered_lemmas: list[str] = self.__filter_lemmas(lemmas, min_lemma_size)

        return filtered_lemmas

    def __make_normalization(self, text: str) -> str:
        normalized_text: str = Normalizer().normalize_text(text)

        return normalized_text

    def __make_lemmatization(self, text: str) -> list[str]:
        lemmatizer: Lemmatizer = Lemmatizer(self.__lemmatization_strategy)
        lemmas: list[str] = lemmatizer.make_lemmatization(text)

        return lemmas

    def __filter_lemmas(self, lemmas: list[str], min_lemma_size: int) -> list[str]:
        filtered_lemmas: list[str] = [
            lemma for lemma in lemmas if len(lemma) >= min_lemma_size
        ]

        return filtered_lemmas
