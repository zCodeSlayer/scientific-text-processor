import pymystem3

from .base import ILemmatizationStrategy


class MyStemLemmatizationStrategy(ILemmatizationStrategy):
    def __init__(self):
        self.__mystem_object = pymystem3.Mystem()

    def make_lemmatization(self, text: str) -> list[str]:
        return self.__mystem_object.lemmatize(text)
