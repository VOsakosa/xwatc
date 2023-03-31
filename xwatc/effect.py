"""
Verschiedene Funktionen, um MänxFkt zusammenzubauen, ohne selbst Funktionen schreiben zu
müssen. Das ist dann leichter zu speichern.

Created on 31.03.2023
"""
from attrs import define
from xwatc.system import MänxPrädikat, Fortsetzung, MänxFkt, Mänx
__author__ = "jasper"


@define
class NurWenn:
    """Diese Geschichte wird nur durchgeführt, wenn eine Variable gesetzt ist."""
    prädikat: MänxPrädikat
    geschichte: MänxFkt[Fortsetzung | None]
    sonst: MänxFkt[Fortsetzung | None] | None = None

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
class Einmalig:
    id_: str

    def __call__(self, mänx: Mänx) -> bool:
        if mänx.welt.ist(self.id_):
            return False
        mänx.welt.setze(self.id_)
        return True


def einmalig(id_: str, geschichte: MänxFkt[Fortsetzung | None]) -> NurWenn:
    return NurWenn(Einmalig(id_), geschichte)
