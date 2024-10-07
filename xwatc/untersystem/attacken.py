"""Das System von Fähigkeiten und Attacken."""

from collections.abc import Iterator, Sequence
from enum import Enum
from functools import cache
from typing import Protocol

from attrs import define, Factory
import cattrs
import yaml

from xwatc import XWATC_PATH


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

    @staticmethod
    def aus_str(text: str, _typ: object = None) -> "list[Schadenstyp]":
        """Parse den Schadenstyp aus einem String.

        >>> Schadenstyp.aus_str("wucht")
        [<Schadenstyp.Wucht: 3>]
        """
        parts = []
        for part in text.split():
            parts.append(Schadenstyp[part.capitalize()])
        if not parts:
            raise ValueError("Kein Schadenstyp gegeben.")
        if len(parts) > 2:
            raise ValueError("Es gibt nur doppelte Schadenstypen, keine mehrfachen.")
        return parts

    @property
    def magisch(self) -> bool:
        """Ob es einer der magischen Schadenstypen ist.

        >>> Schadenstyp.Stich.magisch
        False
        >>> Schadenstyp.Feuer.magisch
        True
        """
        return self.value >= 10


@define
class Resistenzen:
    _dict: dict[Schadenstyp, int]

    @staticmethod
    def neu_null() -> 'Resistenzen':
        """Gibt neue Resistenzen, die überall 0 sind.

        >>> Resistenzen.neu_null().prozentsatz(Schadenstyp.Feuer)
        0
        >>> Resistenzen.neu_null().multiplikator(Schadenstyp.Stich)
        1.0
        """
        return Resistenzen({typ: 0 for typ in Schadenstyp})

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
    max_lp: int
    resistenzen: Resistenzen
    _fertigkeiten: 'list[Fertigkeit]'
    nutze_std_fertigkeiten: bool

    @staticmethod
    def mänx_default() -> 'Kampfwerte':
        """Gibt Kampfwerte eines normalen Humanoiden."""
        return Kampfwerte(100, Resistenzen.neu_null(), [], nutze_std_fertigkeiten=True)

    @property
    def fertigkeiten(self) -> 'Iterator[Fertigkeit]':
        """Listet alle Fertigkeiten auf, auch die Standard-Fertigkeiten."""
        yield from self._fertigkeiten
        if self.nutze_std_fertigkeiten:
            yield from lade_fertigkeiten()


class Zieltyp(Enum):
    Alle = 0
    Einzel = 1


class MitName(Protocol):
    @property
    def name(self) -> str:
        """Der Name des Objekts."""


class Effekt(Enum):
    Verfluchen = 1
    Selbstentwaffnung = 2
    Blocken = 3
    Selbstverwirrung = 4
    Entflammung = 5


@define
class Fertigkeit:
    """Eine Art von Angriff, die ein Kämpfer besitzt."""
    name: str  #: z.B. normaler Angriff
    name_kurz: str  # : z.B. normal
    schaden: int  # die Menge an Schaden in LP
    typ: list[Schadenstyp]
    mp: int = 0
    abklingzeit: int = 0
    waffe: str | None = None
    zieltyp: Zieltyp = Zieltyp.Einzel
    effekte: list[Effekt] = Factory(list)

    def text(self, angreifer: MitName, verteidiger_liste: Sequence[MitName]) -> str:
        """Der Text, wenn die Attacke eingesetzt wird."""
        verteidiger = [(a.name if a.name != "Du" else "dich")
                       for a in verteidiger_liste]
        if len(verteidiger) == 1:
            vers, = verteidiger
        else:
            vers = ", ".join(verteidiger[:-1]) + " und " + verteidiger[-1]

        return (f"{angreifer.name} setzt {self.name} gegen {vers} ein.")


@cache
def lade_fertigkeiten() -> Sequence[Fertigkeit]:
    path = XWATC_PATH / "fertigkeiten.yaml"
    with path.open("r") as file:
        data = yaml.safe_load(file)
    return [_lade_fertigkeit(fertigkeit) for fertigkeit in data]


_converter = cattrs.Converter()
_converter.register_structure_hook(Fertigkeit, cattrs.gen.make_dict_structure_fn(
    Fertigkeit, _converter, typ=cattrs.gen.override(struct_hook=Schadenstyp.aus_str)))


def _lade_fertigkeit(data: dict) -> Fertigkeit:
    """Lade eine Fertigkeit aus ihrer Serialisierung.

    >>> _lade_fertigkeit({"abklingzeit": 2, "name": "Dreschen", "schaden": 25,
    ...     "waffe": "Morgenstern", "typ": "wucht"})  # doctest:+ELLIPSIS, +NORMALIZE_WHITESPACE
    Fertigkeit(name='Dreschen', name_kurz='dreschen', schaden=25, typ=[<Schadenstyp.Wucht: 3>], 
        mp=0, abklingzeit=2, ...)
    """
    if "name_kurz" not in data:
        data["name_kurz"] = data["name"].lower()
    data["mp"] = data.get("mana", data.get("stamina", 0))
    return _converter.structure(data, Fertigkeit)
