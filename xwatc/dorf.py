"""
Xwatc' Ort- und Menschensystem.

Seit 10.10.2020
"""
from __future__ import annotations
import attrs
from attrs import define, field
from enum import Enum
from collections.abc import Sequence, Callable, Iterable
from typing import List, Tuple, Union, TypeAlias
from typing import TYPE_CHECKING
from dataclasses import dataclass
from xwatc.system import (malp, MenuOption, sprich, MänxFkt, Fortsetzung)
from xwatc import system
from xwatc import weg
if TYPE_CHECKING:
    from xwatc import nsc
from xwatc.utils import UndPred
__author__ = "jasper"


def ort(
        name: str,
        dorf: Dorf | weg.Wegkreuzung | None,
        text: Sequence[str] | None = None) -> weg.Wegkreuzung:
    """
    Konstruiere einen neuen Ort. Das ist eine Wegkreuzung, die zu einem Dorf
    gehört und generell mit Namen statt mit Himmelsrichtung verbunden wird.

    ```
    ort = ort("Taverne Zum Katzenschweif", None, # wird noch hinzugefügt
              "Eine lebhafte Taverne voller Katzen",
              [
                  welt.obj("genshin:mond:diona"),
                  welt.obj("genshin:mond:margaret")
              ])
    ```
    """
    if isinstance(dorf, weg.Wegkreuzung):
        dorf = dorf.dorf
    ans = weg.Wegkreuzung(
        name, {}, immer_fragen=True, dorf=dorf,
        gebiet=dorf.gebiet if dorf else None)
    if text:
        ans.add_beschreibung(text)
    if dorf:
        dorf.orte.append(ans)
        if dorf.hat_draußen and len(dorf.orte) > 1:
            dorf.draußen - ans
    return ans


@define
class Dorf:
    """Ein Dorf besteht aus mehreren Orten, an denen man Menschen treffen kann.
    Ein Dorf kann eine Struktur haben, oder es gibt einfach nur ein draußen
    und Gebäude. Wenn es ein draußen gibt, wird jeder Ort automatisch damit verbunden.
    """
    name: str
    orte: list[weg.Wegkreuzung]
    hat_draußen: bool
    gebiet: weg.Gebiet

    @classmethod
    def mit_draußen(cls, name: str, gebiet: weg.Gebiet) -> 'Dorf':
        """Erzeuge ein Dorf mit einem Standard-Ort (draußen), der wie das Dorf heißt."""
        ans = cls(name, [], hat_draußen=True, gebiet=gebiet)
        ort(name, ans)
        return ans

    @property
    def draußen(self) -> weg.Wegkreuzung:
        return self.orte[0]

    @classmethod
    def mit_struktur(cls, name: str, gebiet: weg.Gebiet, orte: Sequence[weg.Wegkreuzung]
                     ) -> 'Dorf':
        return cls(name, [*orte], hat_draußen=False, gebiet=gebiet)

    def main(self, _mänx) -> Fortsetzung | None:
        malp(f"Du erreichst {self.name}.")
        return self.orte[0]

    def get_ort(self, name: str) -> weg.Wegkreuzung:
        for ort in self.orte:
            if ort.name.casefold() == name.casefold():
                return ort
        raise KeyError(f"In {self.name} unbekannter Ort {name}")
