"""
Xwatc' Ort- und Menschensystem.

Seit 10.10.2020
"""
from __future__ import annotations
import attrs
from attrs import define, field, Factory
from enum import Enum
from collections.abc import Sequence, Callable, Iterable
from typing import List, Tuple, Optional as Opt, Union, TypeAlias
from typing import TYPE_CHECKING
from dataclasses import dataclass
from xwatc.system import (malp, MenuOption, sprich, MänxFkt, Welt, Fortsetzung)
from xwatc import system
from xwatc import weg
if TYPE_CHECKING:
    from xwatc import nsc
from xwatc.utils import UndPred
from xwatc.weg import Himmelsrichtung
__author__ = "jasper"


class Rückkehr(Enum):
    WEITER_REDEN = 0
    ZURÜCK = 1
    VERLASSEN = 2


NSCOptionen: TypeAlias = Iterable[MenuOption[MänxFkt]]


# Vorherige Dialoge, nur str für Name, sonst (name, mindestanzahl)
VorList: TypeAlias = Sequence[str | Tuple[str, int]]


@dataclass
class Malp:
    """Objekt, oft statt str zurückgegeben werden kann, um den String als Malp auszugeben,
    und nicht, wie bei Dialogen üblich, mit Sprich."""
    text: str
    warte: bool = False

    def __call__(self, *__):
        malp(self.text, warte=self.warte)

    def __str__(self) -> str:
        return self.text


class Zeitpunkt(Enum):
    """Der Zeitpunkt, an dem ein Dialog ausführbar ist bzw. ausgeführt wird.

    Reden steht für den normalen Zeitpunkt, wenn der Spieler auf eigene Initiative den
    Dialog starten kann.

    Vorstellen steht für Dialoge, die automatisch noch vor der Auswahl k/r/f abgespielt
    werden.

    Ansprechen steht für Dialoge, die direkt ausgeführt werden, wenn der Spieler versucht,
    den NSC anzusprechen.

    Option steht für Dialoge, die zusätzlich zu k/r/f auftauchen. Es gibt nur dann einen
    Unterschied zu Reden, wenn direkt_reden beim NSC nicht an ist.
    """
    Reden = 0
    Vorstellen = 1
    Ansprechen = 2
    Option = 3


DialogFn = Callable[["nsc.NSC", system.Mänx],
                    Union[None, bool, Fortsetzung, Rückkehr]]


def _vorherige_converter(value: VorList | str) -> VorList:
    if isinstance(value, str):
        return [value]
    return value

# TODO move to NSC


@define
class Dialog:
    """Ein einzelner Gesprächsfaden beim Gespräch mit einem NSC.
    ```
    Dialog("halloli", "Halloli",
            ["Du bist ein Totenbeschwörer", Malp("Der Mensch weicht zurück")],
           effekt=lambda n,m:m.welt.setze("totenbeschwörer")))
    Dialog("geld", "Gib mir Geld", "Hilfe!", "halloli",
            effekt=lambda n,m: m.erhalte("Gold", n.gold, n))
    ```

    :param name: Der kurze Name des Dialogs
    :param text: Der lange Text in der Option
    :param geschichte: Das, was beim Dialog passiert. Kann DialogFn sein
        oder eine Liste von Strings und Malps, die dann gesagt werden.
    :param effekt: Passiert zusätzlich noch nach Geschichte.
    :param vorherige: Liste von Dialogen, die schon gesagt sein müssen
    :param min_freundlich: Mindestfreundlichkeit für den Dialog
    :param direkt: Wenn wahr, redet der Mänx dich an, statt du ihn.
    :param gruppe: Nur ein Dialog einer gruppe darf gewählt werden.
    """
    name: str
    text: str
    geschichte: 'DialogGeschichte'
    vorherige: VorList = field(converter=_vorherige_converter, factory=tuple)
    _wiederhole: int = field(validator=attrs.validators.ge(0), default=0)
    min_freundlich: int | None = None
    zeitpunkt: Zeitpunkt = Zeitpunkt.Reden
    effekt: DialogFn | None = None
    gruppe: str | None = None
    wenn_fn: DialogFn | None = None

    def wenn(self, fn: DialogFn) -> 'Dialog':
        """Dieser Dialog soll nur aufrufbar sein, wenn die Funktion fn
        erfüllt ist."""
        if self.wenn_fn:
            self.wenn_fn = UndPred(self.wenn_fn, fn)
        else:
            self.wenn_fn = fn
        return self

    def wenn_var(self, *welt_variabeln: str) -> 'Dialog':
        """Dieser Dialog soll nur aufrufbar sein, wenn die Weltvariable
        gesetzt ist."""
        return self.wenn(lambda _n, m: all(m.welt.ist(v) for v in welt_variabeln))

    def wiederhole(self, anzahl: int) -> 'Dialog':
        """Füge eine maximale Anzahl von Wiederholungen hinzu"""
        self._wiederhole = anzahl
        return self

    def verfügbar(self, nsc: 'nsc.NSC', mänx: system.Mänx) -> bool:
        """Prüfe, ob der Dialog als Option verfügbar ist."""
        # Keine Wiederholungen mehr
        if self._wiederhole and nsc.dialog_anzahl.get(self.name, 0) >= self._wiederhole:
            return False
        # Gruppe
        if self.gruppe and nsc.dialog_anzahl.get(self.gruppe, 0) >= 1:
            return False
        # vorherige Dialoge
        for bed in self.vorherige:
            if isinstance(bed, str):
                if not nsc.dialog_anzahl.get(bed, 0):
                    return False
            else:
                bed_name, anzahl = bed
                if nsc.dialog_anzahl.get(bed_name, 0) < anzahl:
                    return False
        if (self.min_freundlich is not None and
                nsc.freundlich < self.min_freundlich):
            return False
        if self.wenn_fn:
            return bool(self.wenn_fn(nsc, mänx))
        return True

    def zu_option(self) -> MenuOption['Dialog']:
        return (self.text, self.name, self)


DialogGeschichte = Union[Sequence[Malp | str], DialogFn]
DialogErzeugerFn = Callable[[], Iterable[Dialog]]
RunType = MänxFkt | Rückkehr | Dialog
_MainOpts = List[MenuOption[RunType]]


def hallo(n, _m):
    sprich(n.name, f"Hallo, ich bin {n.name}. "
           "Freut mich, dich kennenzulernen.")
    return True


def hallo2(n, _m):
    sprich(n.name, "Hallo nochmal!")
    return True


HalloDialoge = [
    Dialog("hallo", "Hallo", hallo).wiederhole(1),
    Dialog("hallo2", "Hallo", hallo2, "hallo")
]


def ort(
        name: str,
        dorf: Union[None, Dorf, weg.Wegkreuzung],
        text: Opt[Sequence[str]] = None,
        menschen: Sequence[nsc.NSC] = ()) -> weg.Wegkreuzung:
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
    ans = weg.Wegkreuzung(name, {}, menschen=[
                          *menschen], immer_fragen=True, dorf=dorf)
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
    
    @classmethod
    def mit_draußen(cls, name: str) -> 'Dorf':
        """Erzeuge ein Dorf mit einem Standard-Ort (draußen), der wie das Dorf heißt."""
        ans = cls(name, [], hat_draußen=True)
        ort(name, ans)
        return ans
    
    @property
    def draußen(self) -> weg.Wegkreuzung:
        return self.orte[0]
    
    @classmethod
    def mit_struktur(cls, name: str, orte: Sequence[weg.Wegkreuzung]) -> 'Dorf':
        return cls(name, [*orte], hat_draußen=False)

    def main(self, _mänx) -> Fortsetzung | None:
        malp(f"Du erreichst {self.name}.")
        return self.orte[0]

    def get_ort(self, name: str) -> weg.Wegkreuzung:
        for ort in self.orte:
            if ort.name.casefold() == name.casefold():
                return ort
        raise KeyError(f"In {self.name} unbekannter Ort {name}")
