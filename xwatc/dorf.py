"""
Xwatc' Ort- und Menschensystem.

Seit 10.10.2020
"""
from __future__ import annotations
import attrs
from attrs import define, field
from enum import Enum
from collections.abc import Sequence, Callable, Iterable
from typing import List, Tuple, Optional as Opt, Union
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


NSCOptionen = Iterable[MenuOption[MänxFkt]]


# Vorherige Dialoge, nur str für Name, sonst (name, mindestanzahl)
VorList = Sequence[str | Tuple[str, int]]


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
    vorherige: VorList = field(converter=_vorherige_converter, factory=list)
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


class Ort(weg.Wegkreuzung):
    """Ein Ort im Dorf, wo sich Menschen aufhalten können"""

    def __init__(self,
                 name: str,
                 dorf: Union[None, Dorf, Ort],
                 text: Opt[Sequence[str]] = None,
                 menschen: Sequence[nsc.NSC] = ()):
        """
        ```
        ort = Ort("Taverne Zum Katzenschweif", None, # wird noch hinzugefügt
                  "Eine lebhafte Taverne voller Katzen",
                  [
                      welt.obj("genshin:mond:diona"),
                      welt.obj("genshin:mond:margaret")
                  ])
        ```
        """
        super().__init__(name, menschen=menschen, immer_fragen=True)
        if text:
            if isinstance(text, str):
                text = [text]
            self.add_beschreibung(text)
        if isinstance(dorf, Ort):
            self.dorf: Dorf | None = dorf.dorf
        else:
            self.dorf = dorf
        if self.dorf:
            self.dorf.orte.append(self)

    def __sub__(self, anderer: Ort) -> Ort:
        anderer.nachbarn[Himmelsrichtung.from_kurz(
            self.name)] = weg.Richtung(self)
        self.nachbarn[Himmelsrichtung.from_kurz(
            anderer.name)] = weg.Richtung(anderer)
        return anderer

    def verbinde(self,
                 anderer: weg.Wegpunkt, richtung: str = "",
                 typ: weg.Wegtyp = weg.Wegtyp.WEG, ziel: str = ""):
        if isinstance(anderer, Ort) and not richtung:
            anderer.nachbarn[Himmelsrichtung.from_kurz(
                self.name)] = weg.Richtung(self)
            self.nachbarn[Himmelsrichtung.from_kurz(
                anderer.name)] = weg.Richtung(anderer)
        else:
            super().verbinde(anderer, richtung=richtung, typ=typ, ziel=ziel)

    def add_nsc(self, welt: Welt, name: str, fkt: Callable[..., nsc.NSC],
                *args, **kwargs):
        welt.get_or_else(name, fkt, *args, **kwargs).ort = self

    def __repr__(self):
        if self.dorf:
            return f"Ort {self.name} von {self.dorf.name}"
        else:
            return f"Ort {self.name}, Teil keines Dorfes"


class Dorf:
    """Ein Dorf besteht aus mehreren Orten, an denen man Menschen treffen kann.
    Es gibt einen Standard-Ort, nämlich "draußen".
    """

    def __init__(self, name: str, orte: Opt[List[Ort]] = None) -> None:
        if orte:
            self.orte = orte
        else:
            self.orte = []
            Ort("draußen", self, "Du bist draußen.")
        self.name = name

    def main(self, mänx) -> Fortsetzung | None:
        malp(f"Du bist in {self.name}. Möchtest du einen der Orte betreten oder "
             "draußen bleiben?")
        orte: list[MenuOption[Ort | None]] = [
            (ort.name, ort.name.lower(), ort) for ort in self.orte[1:]]
        orte.append(("Bleiben", "", self.orte[0]))
        orte.append((f"{self.name} verlassen", "v", None))
        loc = mänx.menu(orte, frage="Wohin? ", save=self)
        while isinstance(loc, Ort):
            loc = self.ort_main(mänx, loc)
        return loc

    def get_ort(self, name: str) -> Ort:
        for ort in self.orte:
            if ort.name.casefold() == name.casefold():
                return ort
        raise KeyError(f"In {self.name} unbekannter Ort {name}")

    def ort_main(self, mänx, ort: Ort) -> Ort | Fortsetzung | None:
        ort.menschen[:] = filter(lambda m: not m.tot, ort.menschen)
        ort.beschreibe(mänx, None)
        if ort.menschen:
            malp("Hier sind:")
            for mensch in ort.menschen:
                malp(f"{mensch.name}, {mensch.art}")
        else:
            malp("Hier ist niemand.")
        optionen: list[MenuOption[nsc.NSC | Ort | None]]  # @UnusedVariable
        optionen = [("Mit " + mensch.name + " reden", mensch.name.lower(),
                     mensch) for mensch in ort.menschen]
        optionen.extend((f"Nach {o.name} gehen", o.name.lower(), o)
                        for o in self.orte if o != ort)
        optionen.append(("Ort verlassen", "fliehen", None))
        opt = mänx.menu(optionen, save=self)  # TODO: Den Ort speichern
        if isinstance(opt, nsc.NSC):
            ans = opt.main(mänx)
            if isinstance(ans, Ort):
                return ans
            elif ans:
                return ans
            return ort
        else:
            return opt


from xwatc import nsc  # @Reimport
NSC = nsc.OldNSC
