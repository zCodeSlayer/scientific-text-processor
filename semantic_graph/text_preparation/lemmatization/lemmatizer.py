from .lemmatization_strategies import ILemmatizationStrategy


class Lemmatizer:
    def __init__(self, lemmatization_strategy: ILemmatizationStrategy) -> None:
        self.__lemmatization_strategy = lemmatization_strategy

    def make_lemmatization(self, text: str) -> list[str]:
        return self.__lemmatization_strategy.make_lemmatization(text)

    def change_strategy(self, lemmatization_strategy: ILemmatizationStrategy) -> None:
        self.__lemmatization_strategy = lemmatization_strategy
