"""
Verschiedene Funktionen, um MänxFkt zusammenzubauen, ohne selbst Funktionen schreiben zu
müssen. Das ist dann leichter zu speichern.

Created on 31.03.2023
"""
from attrs import define, field
from bisect import bisect
from collections.abc import Sequence
import random
from xwatc.system import MänxPrädikat, Fortsetzung, MänxFkt, Mänx, malp
__author__ = "jasper"


def _to_geschichte(text: str | Sequence[str] | MänxFkt[Fortsetzung | None]
                   ) -> MänxFkt[Fortsetzung | None]:
    match text:
        case str(txt):
            return TextGeschichte([txt])
        case Sequence():
            return TextGeschichte(text)
        case _:
            return text


@define
class TextGeschichte:
    texte: Sequence[str]

    def __call__(self, _mänx: Mänx) -> None:
        for text in self.texte:
            malp(text)


@define
class NurWenn:
    """Diese Geschichte wird nur durchgeführt, wenn eine Variable gesetzt ist."""
    prädikat: MänxPrädikat
    geschichte: MänxFkt[Fortsetzung | None] = field(converter=_to_geschichte)
    sonst: MänxFkt[Fortsetzung | None] | None = field(
        converter=_to_geschichte, default=None)

    def __call__(self, mänx: Mänx) -> Fortsetzung | None:
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
class Zufällig:
    wahlen: Sequence[MänxFkt]
    wkeiten: Sequence[float]

    @classmethod
    def gleichmäßig(cls, *fälle: str | Sequence[str] | MänxFkt[Fortsetzung | None]
                    ) -> 'Zufällig':
        if not fälle:
            raise TypeError("Zufällig braucht min. einen Ausgang")
        wahlen = [_to_geschichte(fall) for fall in fälle]
        len_fälle = len(fälle)
        wkeiten = [i / len_fälle for i in range(1, len_fälle)]
        return cls(wahlen, wkeiten)

    @classmethod
    def ungleichmäßig(cls, *fälle: tuple[str | Sequence[str] | MänxFkt[Fortsetzung | None], float]):
        if not fälle:
            raise TypeError("Zufällig braucht min. einen Ausgang")
        if any(wkeit <= 0 for _fall, wkeit in fälle):
            raise ValueError("Wahrscheinlichkeitsgewichte müssen positiv sein.")
        wahlen = [_to_geschichte(fall) for fall, _wkeit in fälle]
        gesamt = sum(wkeit for _f, wkeit in fälle)
        zsum = 0.  # @UnusedVariable
        wkeiten = [(zsum := zsum + wkeit) / gesamt for _f, wkeit in fälle[:-1]]
        return cls(wahlen, wkeiten)

    def __call__(self, mänx: Mänx) -> MänxFkt:
        return self.wahlen[bisect(self.wkeiten, random.random())]


@define
class Einmalig:
    id_: str

    def __call__(self, mänx: Mänx) -> bool:
        if mänx.welt.ist(self.id_):
            return False
        mänx.welt.setze(self.id_)
        return True
