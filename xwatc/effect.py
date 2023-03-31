"""
Verschiedene Funktionen, um MänxFkt zusammenzubauen, ohne selbst Funktionen schreiben zu
müssen. Das ist dann leichter zu speichern.

Created on 31.03.2023
"""
from attrs import define, field
from collections.abc import Sequence
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
class Einmalig:
    id_: str

    def __call__(self, mänx: Mänx) -> bool:
        if mänx.welt.ist(self.id_):
            return False
        mänx.welt.setze(self.id_)
        return True
