"""Untersystem des Wegsystems, dass einem zufällige Monster entgegenschmeißt.

Als Grundidee gelten drei Prototypen:

1. Die Kachel wie in lg.süden. Du triffst eine Menge von Monstern in jedem Punkt und musst dich
durchkämpfen
2. Wege wie in jtg. Wege sind unterschiedlich lang, und je nachdem, wie lange du läufst, triffst du
mehr Monster. Normalerweise triffst du nichts.
3. Dörfer wie Grökrakchöl. Mit einer sehr geringen Chance passiert etwas besonderes.

"""

from typing import Sequence
from attrs import define

from xwatc import nsc
from xwatc.system import Mänx, MänxFkt
from xwatc.weg import WegEnde, Wegpunkt


@define
class Begegnungsliste:
    """Eine Liste von Begegnungen, die einen an einem Ort treffen können.
    (wird nicht abgespeichert)"""
    id_: str

    def add_begegnung[T: MänxFkt[None | Wegpunkt | WegEnde] | Sequence[str]](self, fkt: T) -> T:
        """Füge eine Begegnung hinzu, die eine Funktion ist."""
        return fkt

    def add_monster(self, template: "nsc.StoryChar") -> None:
        """Füge ein Monster hinzu."""


@define
class Begegnungsausgang:
    """Der Ausgang einer Begegnung, wird zurückgegeben, nachdem eine Begegnung fertig durchgeführt
    wurde."""
    ausgang: WegEnde | Wegpunkt | None


@define(kw_only=True)
class Monstergebiet:
    """Ein Gebiet, in dem Monster spawnen und innerhalb des Gebiets umherziehen.
    (wird abgespeichert)

    Das Besiegen von Monstern innerhalb des Gebiets verringert die Gesamtanzahl von Monstern im
    Gebiet (Monsterpegel)
    """
    begegnungen: Begegnungsliste
    monsterspiegel: int
    herkunft: "kreuzung.NachbarKey | None" = None

    def betrete(self, mänx: Mänx) -> None:
        """Betrete das Monstergebiet und regeneriere die Monster."""

    def nächste_begegnung(self, mänx: Mänx) -> Begegnungsausgang | None:
        """Führe eine Begegnung mit einem Monster aus."""
        return None


from xwatc.weg import _kreuzung as kreuzung  # noqa
