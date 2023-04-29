"""
Generelles, um Text zusammenzubauen.
Created on 23.10.2020
"""
from __future__ import annotations
from typing import ParamSpec, Generic, Callable
from typing_extensions import Self
__author__ = "jasper"

P = ParamSpec("P")


class UndPred(Generic[P]):
    """Verunde Prädikate."""

    def __init__(self, *prädikate: Callable[P, bool]):
        self.prädikate: list[Callable[P, bool]] = []
        for p in prädikate:
            if isinstance(p, UndPred):
                self.prädikate.extend(p.prädikate)
            else:
                self.prädikate.append(p)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        return all(p(*args, **kwargs) for p in self.prädikate)

    def __and__(self, other: Callable[P, bool]) -> Self:
        return type(self)(self, other)


def uartikel(geschlecht: str, fall: int = 1) -> str:
    """Der unbestimmte Artikel"""
    if geschlecht == "p":
        return ""
    elif geschlecht == "n" or geschlecht == "m":
        return ["einem", "ein", "eines"][fall % 3]
    elif fall == 1 or fall == 4:
        return "eine"
    else:
        return "einer"


def bartikel(geschlecht: str, fall: int = 1) -> str:
    if geschlecht == "n":
        return ["dem", "das", "des"][fall % 3]
    elif geschlecht == "m":
        return ["den", "der", "des", "dem"][fall % 4]
    elif fall == 1 or fall == 4:
        return "die"
    elif fall == 2 or fall == 3 and geschlecht == "f":
        return "der"
    else:
        return "den"


def adj_endung(schwach: int, geschlecht: str, fall: int = 1) -> str:
    if fall == 2 or fall == 3 or geschlecht == "p":
        return "en"
    elif geschlecht == "m":
        if fall == 4:
            return "en"
        elif schwach:
            return "er"
        return "e"
    elif geschlecht == "n" and schwach:
        return "es"
    return "e"
