from .lemmatization_strategies import LemmatizationStrategy


class Lemmatizer:
    def __init__(
        self, text: str, lemmatization_strategy: LemmatizationStrategy
    ) -> None:
        self.__text: str = text
        self.__lemmatization_strategy = lemmatization_strategy

    def make_lemmatization(self) -> list[str]:
        return self.__lemmatization_strategy.make_lemmatization(self.__text)

    def change_strategy(self, lemmatization_strategy: LemmatizationStrategy) -> None:
        self.__lemmatization_strategy = lemmatization_strategy
