"""
Verschiedene Funktionen, um MänxFkt zusammenzubauen, ohne selbst Funktionen schreiben zu
müssen. Das ist dann leichter zu speichern.

Created on 31.03.2023
"""
from attrs import define, field, Factory
from bisect import bisect
from collections.abc import Sequence, Mapping
import random
from typing import Generic, TypeVar
from typing_extensions import Self
from xwatc.system import MänxPrädikat, MänxFkt, Mänx, malp
__author__ = "jasper"


F = TypeVar("F", covariant=True)

@define
class Warten:
    """Signalisiert statt Text Warten."""
    length: float


def _to_geschichte(text: Sequence[str | Warten] | MänxFkt[F]) -> MänxFkt[F | None]:
    """Converter, um Listen von Texten als MänxFkt aufzufassen."""
    match text:
        case str(txt):
            return TextGeschichte([txt])
        case Sequence():
            return TextGeschichte(text)
        case _:
            return text


@define
class TextGeschichte:
    """Eine Geschichte, die nur aus gemalptem Text besteht. Listen von Strings werden zu
    diesem Typ umgewandelt. Am Ende kann der Mänx eine Belohnung erhalten."""
    texte: Sequence[str | Warten]
    schatz: Mapping[str, int] = Factory(dict)

    def __call__(self, mänx: Mänx) -> None:
        for text in self.texte:
            match text:
                case Warten(length=length):
                    mänx.sleep(length)
                case str():
                    malp(text)
                case _:
                    raise TypeError("Wrong type in TextGeschichte", text)
        for schatz, anzahl in self.schatz.items():
            mänx.erhalte(schatz, anzahl)


@define
class NurWenn(Generic[F]):
    """Diese Geschichte wird nur durchgeführt, wenn eine Variable gesetzt ist."""
    prädikat: MänxPrädikat
    geschichte: MänxFkt[F | None] = field(converter=_to_geschichte)
    sonst: MänxFkt[F | None] | None = field(
        converter=_to_geschichte, default=None)

    def __call__(self, mänx: Mänx) -> F | None:
        if self.prädikat(mänx):
            return self.geschichte(mänx)
        elif self.sonst:
            return self.sonst(mänx)
        return None


@define
class SetzeVariable:
    """Effekt, der eine Variable setzt."""
    variablen_name: str

    def __call__(self, mänx: Mänx) -> None:
        mänx.welt.setze(self.variablen_name)


@define
class Cooldown:
    id_: str
    zeit: int  # Die Zeit in Tagen

    def __call__(self, mänx: Mänx) -> bool:
        if self.id_ in mänx.welt.objekte:
            ans = mänx.welt.objekte[self.id_] <= mänx.welt.tag - self.zeit
        else:
            ans = False
        if ans:
            mänx.welt.objekte[self.id_] = mänx.welt.tag
        return ans


@define(frozen=True)
class Zufällig(Generic[F]):
    wahlen: Sequence[MänxFkt[F | None]]
    wkeiten: Sequence[float]

    @classmethod
    def gleichmäßig(cls, *fälle: str | Sequence[str] | MänxFkt[F]) -> Self:
        """Erzeuge eine zufällige Geschichte, wo alle möglichen Geschichten mit gleicher 
        Wahrscheinlichkeit ausgeführt werden."""
        if not fälle:
            raise TypeError("Zufällig braucht min. einen Ausgang")
        wahlen = [_to_geschichte(fall) for fall in fälle]
        len_fälle = len(fälle)
        wkeiten = [i / len_fälle for i in range(1, len_fälle)]
        return cls(wahlen, wkeiten)

    @classmethod
    def ungleichmäßig(cls, *fälle: tuple[float, str | Sequence[str] | MänxFkt[F]]) -> Self:
        """Erzeuge eine zufällige Geschichte, wo die möglichen Geschichten gemäß eines
        Gewichtes gewählt werden."""
        if not fälle:
            raise TypeError("Zufällig braucht min. einen Ausgang")
        if any(wkeit <= 0 for wkeit, _fall in fälle):
            raise ValueError(
                "Wahrscheinlichkeitsgewichte müssen positiv sein.")
        wahlen = [_to_geschichte(fall) for _wkeit, fall in fälle]
        gesamt = sum(wkeit for wkeit, _f in fälle)
        zsum: float = 0  # @UnusedVariable
        wkeiten = [(zsum := zsum + wkeit) / gesamt for wkeit, _f in fälle[:-1]]
        return cls(wahlen, wkeiten)

    def __call__(self, mänx: Mänx) -> F | None:
        return self.wahlen[bisect(self.wkeiten, random.random())](mänx)



@define
class Geschichtsfolge(Generic[F]):
    list_: Sequence[MänxFkt[F]]

    def __call__(self, mänx: Mänx) -> F | None:
        for fn in self.list_:
            if (ans := fn(mänx)) is not None:
                return ans
        return None


def in_folge(*geschichten: Sequence[str | Warten] | MänxFkt[F]) -> Geschichtsfolge[F | None]:
    """Führt mehrere Geschichten hintereinander aus. Gibt eine Geschichte eine Fortsetzung zurück,
    wird diese zurückgegeben und die restlichen Funktionen verworfen.
    """
    return Geschichtsfolge([_to_geschichte(g) for g in geschichten])


@define
class Einmalig:
    id_: str

    def __call__(self, mänx: Mänx) -> bool:
        if mänx.welt.ist(self.id_):
            return False
        mänx.welt.setze(self.id_)
        return True
