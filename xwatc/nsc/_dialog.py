"""
Untermodul, das die Klasse Dialog enthält.
"""
import attrs
from attrs import define, field
from enum import Enum
from collections.abc import Sequence, Callable, Iterable
from typing import List, Tuple, Union, TypeAlias
from typing import TYPE_CHECKING
from typing_extensions import Self
from dataclasses import dataclass
from xwatc.system import (malp, MenuOption, MänxFkt, Fortsetzung)
from xwatc import system
if TYPE_CHECKING:
    from xwatc import nsc  # @UnusedImport
from xwatc.utils import UndPred

class Rückkehr(Enum):
    """Wie es nach einem Dialog weitergeht. Bei WEITER_REDEN ist man weiter in dem vorherigen
    Menu. Bei ZURÜCK wechselt man eine Ebene nach oben, und bei VERLASSEN verlässt man den NSC.
    """
    WEITER_REDEN = 0
    ZURÜCK = 1
    VERLASSEN = 2

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


@define
class Sprich:
    """Wird in DialogFunktionen gebraucht. Schon Strings werden standardmäßig gesprochen, 
    aber die Verwendung von Sprich erlaubt es, die Art zu setzen.
    `Sprich("Hallo?", "unsicher")` ergibt dann eine Ausgabe wie
    "Martin(unsicher): »Hallo?«.
    """
    text: str
    wie: str = ""


class Zeitpunkt(Enum):
    """Der Zeitpunkt, an dem ein Dialog ausführbar ist bzw. ausgeführt wird.

    - Reden steht für den normalen Zeitpunkt, wenn der Spieler auf eigene Initiative den
    Dialog starten kann.

    - Vorstellen steht für Dialoge, die automatisch noch vor der Auswahl k/r/f abgespielt
    werden.

    - Ansprechen steht für Dialoge, die direkt ausgeführt werden, wenn der Spieler versucht,
    den NSC anzusprechen.

    - Option steht für Dialoge, die zusätzlich zu k/r/f auftauchen. Es gibt nur dann einen
    Unterschied zu Reden, wenn direkt_reden beim NSC nicht an ist.
    """
    Reden = 0
    Vorstellen = 1
    Ansprechen = 2
    Option = 3


DialogFn = Callable[["nsc.NSC", system.Mänx],
                    Rückkehr | Fortsetzung | None | bool]


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
    
    @classmethod
    def ansprechen_neu(cls, geschichte: 'DialogGeschichte', *, name="ansprechen") -> Self:
        if isinstance(geschichte, str):
            geschichte = [Malp(geschichte)]
        return cls(name, name, geschichte, zeitpunkt=Zeitpunkt.Ansprechen)

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


DialogGeschichte = Union[Sequence[Malp | Sprich | str], DialogFn]
DialogErzeugerFn = Callable[[], Iterable[Dialog]]
RunType = MänxFkt | Rückkehr | Dialog

from xwatc import nsc, weg  # @Reimport @UnusedImport
