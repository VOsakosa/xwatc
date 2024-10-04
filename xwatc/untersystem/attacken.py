"""Das System von Fähigkeiten und Attacken."""

from enum import Enum
from typing import Protocol, Self, Sequence

from attrs import define

from xwatc.untersystem.itemverzeichnis import Fähigkeit


class Schadenstyp(Enum):
    """Die acht Schadenstypen im Spiel."""
    Stich = 1
    Klinge = 2
    Wucht = 3
    Explosion = 4

    Feuer = 10
    Arkan = 11
    Kälte = 12
    Blitz = 13

    @property
    def magisch(self) -> bool:
        """Ob es einer der magischen Schadenstypen ist.

        >>> 
        """


@define
class Resistenzen:
    _dict: dict[Schadenstyp, int]

    @staticmethod
    def aus_str(liste: str) -> 'Resistenzen':
        """Parse Resistenzen aus einer Liste von Resistenzen, mit 0 als voller Schaden, 100 als
        kein Schaden.

        >>> Resistenzen.aus_str("0,0,0,0,-20,-30,10,0")
        Resistenzen(0,0,0,0,-20,-30,10,0)
        """
        werte = liste.split(",")
        if not len(werte) == len(Schadenstyp):
            raise ValueError(f"Resistenzen-Liste hat nicht Länge {len(Schadenstyp)}")
        return Resistenzen({typ: int(wert) for typ, wert in zip(Schadenstyp, werte)})

    def __str__(self) -> str:
        return f"""Resistenzen({",".join(str(self._dict[typ]) for typ in Schadenstyp)})"""

    __repr__ = __str__

    def multiplikator(self, typ: Schadenstyp) -> float:
        """Gebe den Schadensmultiplikator eines Schadentyps aus.

        >>> res = Resistenzen.aus_str("0,100,-100,150,-20,-30,10,0")
        >>> res.multiplikator(Schadenstyp.Stich)
        1.0
        >>> res.multiplikator(Schadenstyp.Klinge)
        0.0
        >>> res.multiplikator(Schadenstyp.Wucht)
        2.0
        >>> res.multiplikator(Schadenstyp.Explosion)
        -0.5
        """
        return (100 - self._dict[typ]) / 100

    def prozentsatz(self, typ: Schadenstyp) -> int:
        """Gebe den Resistenz-Prozentsatz eines Schadenstyps aus.
        >>> res = Resistenzen.aus_str("0,100,-100,150,-20,-30,10,0")
        >>> res.prozentsatz(Schadenstyp.Stich)
        0
        """
        return self._dict[typ]


@define
class Kampfwerte:
    max_hp: int
    resistenzen: Resistenzen
    fertigkeiten: 'list[Fertigkeit]'


class Zieltyp(Enum):
    Alle = 0
    Einzel = 1


class MitName(Protocol):
    @property
    def name(self) -> str:
        """Der Name des Objekts."""


@define
class Fertigkeit:
    """Eine Art von Angriff, die ein Kämpfer besitzt."""
    name: str  #: z.B. normaler Angriff
    name_kurz: str  # : z.B. normal
    schaden: int  # die Menge an Schaden in LP
    typ: list[Schadenstyp]
    zieltyp: Zieltyp = Zieltyp.Einzel

    @classmethod
    def aus_fähigkeit(cls, fähigkeit: Fähigkeit) -> Self:
        return cls(fähigkeit.name, fähigkeit.name.lower(), fähigkeit.schaden)

    def text(self, angreifer: MitName, verteidiger_liste: Sequence[MitName]) -> str:
        """Der Text, wenn die Attacke eingesetzt wird."""
        verteidiger = [(a.name if a.name != "Du" else "dich")
                       for a in verteidiger_liste]
        if len(verteidiger) == 1:
            vers, = verteidiger
        else:
            vers = ", ".join(verteidiger[:-1]) + " und " + verteidiger[-1]

        return (f"{angreifer.name} setzt {self.name} gegen {vers} ein.")
