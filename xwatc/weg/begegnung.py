"""Untersystem des Wegsystems, dass einem zufällige Monster entgegenschmeißt.

Als Grundidee gelten drei Prototypen:

1. Die Kachel wie in lg.süden. Du triffst eine Menge von Monstern in jedem Punkt und musst dich
durchkämpfen
2. Wege wie in jtg. Wege sind unterschiedlich lang, und je nachdem, wie lange du läufst, triffst du
mehr Monster. Normalerweise triffst du nichts.
3. Dörfer wie Grökrakchöl. Mit einer sehr geringen Chance passiert etwas besonderes.

"""

from typing import TypeVar
from attrs import define, field

from xwatc.nsc import StoryChar
from xwatc.system import Welt, Mänx, MänxFkt
from xwatc.weg import WegEnde, Wegpunkt


Wrapped = TypeVar("Wrapped", bound=MänxFkt[None | Wegpunkt | WegEnde])


@define
class Begegnungsliste:
    """Eine Liste von Begegnungen, die einen an einem Ort treffen können.
    (wird nicht abgespeichert)"""
    id_: str

    def add_begegnung(self, fkt: Wrapped) -> Wrapped:
        """Füge eine Begegnung hinzu, die eine Funktion ist."""
        return fkt

    def add_monster(self, template: StoryChar) -> None:
        """Füge ein Monster hinzu."""


@define
class Monstergebiet:
    """Ein Gebiet, in dem Monster spawnen und innerhalb des Gebiets umherziehen.
    (wird abgespeichert)

    Das Besiegen von Monstern innerhalb des Gebiets verringert die Gesamtanzahl von Monstern im
    Gebiet (Monsterpegel)
    """
    begegnungen: Begegnungsliste
    monsterspiegel = field(kw_only=True)

    def betrete(self, mänx: Mänx) -> None:
        """Betrete das Monstergebiet und regeneriere die Monster."""
