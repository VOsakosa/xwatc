"""
Wegpunkte für JTGs Wegesystem.
Created on 17.10.2020
"""
from __future__ import annotations
import enum
import random
from dataclasses import dataclass
from xwatc.utils import uartikel, bartikel
__author__ = "jasper"
import typing
from typing import List, Any, Optional as Opt, cast, Iterable, Union, Sequence,\
    Collection, Callable, Dict, Tuple
from xwatc.system import Mänx, MenuOption, MänxFkt, InventarBasis, malp, mint


GEBIETE: Dict[str, Callable[[Mänx], Wegpunkt]] = {}
# Die Verbindungen zwischen Gebieten
EINTRITTSPUNKTE: Dict[Tuple[str, str], 'Gebietsende'] = {}
ADAPTER: Dict[str, 'WegAdapter'] = {}


@enum.unique
class Ereignis(enum.Enum):
    KAMPF = enum.auto()
    MORD = enum.auto()
    DIEBSTAHL = enum.auto()


class Context(typing.Protocol):
    def melde(self, mänx: Mänx, ereignis: Ereignis, data: Any) -> Any:
        """Melde ein Ereignis an den Kontext"""


@dataclass
class WegEnde:
    weiter: MänxFkt


class Wegpunkt(Context, typing.Protocol):
    def get_nachbarn(self) -> List[Wegpunkt]:
        return []

    def main(self, mänx: Mänx, von: Opt[Wegpunkt]) -> Union[Wegpunkt, WegEnde]:
        """Betrete den Wegpunkt mit mänx aus von."""

    def verbinde(self, anderer: Wegpunkt):
        """Verbinde den Wegpunkt mit anderer. Nur für Wegpunkte mit nur einer
        Seite"""


class _Strecke(Wegpunkt):
    def __init__(self, p1: Opt[Wegpunkt], p2: Opt[Wegpunkt] = None):
        super().__init__()
        self.p1 = self._verbinde(p1)
        self.p2 = self._verbinde(p2)

    def _verbinde(self, anderer: Opt[Wegpunkt]) -> Opt[Wegpunkt]:
        """Ruft anderer.verbinde(self) auf."""
        if anderer:
            anderer.verbinde(self)
        return anderer

    def get_nachbarn(self) -> List[Wegpunkt]:
        return [a for a in (self.p1, self.p2) if a]

    def verbinde(self, anderer: Wegpunkt):
        if not self.p1:
            self.p1 = anderer
        elif self.p1 != anderer and not self.p2:
            self.p2 = anderer


class MonsterChance:
    """Eine Möglichkeit eines Monsterzusammenstoßes."""

    def __init__(self, wahrscheinlichkeit: float, geschichte: MänxFkt) -> None:
        super().__init__()
        self.wkeit = wahrscheinlichkeit
        self.geschichte = geschichte

    def main(self, mänx: Mänx):
        # Hier in den Kampf einsteigen
        self.geschichte(mänx)


class Weg(_Strecke):
    """Ein Weg hat zwei Enden und dient dazu, die Länge der Reise darzustellen.
    Zwei Menschen auf dem Weg zählen als nicht benachbart."""

    def __init__(self, länge: float, p1: Opt[Wegpunkt], p2: Opt[Wegpunkt],
                 monster_tag: Opt[List[MonsterChance]] = None,
                 monster_nachts: Opt[List[MonsterChance]] = None):
        """
        :param länge: Länge in Minuten
        :param p1: Startpunkt
        :param p2: Endpunkt
        :param monster_tag: Monster, die am Tag auftauchen
        """
        super().__init__(p1, p2)
        self.länge = länge / 24
        self.monster_tag = monster_tag
        self.monster_nachts = monster_nachts

    def melde(self, mänx: Mänx, ereignis: Ereignis,
              data: Any) -> None:  # pylint: disable=unused-argument
        if ereignis == Ereignis.KAMPF:
            self.monster_check(mänx)
        # super().melde(mänx, ereignis, data)

    def monster_check(self, mänx: Mänx) -> bool:
        """Checkt, ob ein Monster getroffen wird.

        :return:
            True, wenn der Spieler sich entscheidet umzukehren.
        """
        if mänx.welt.is_nacht():
            ms = self.monster_nachts
        else:
            ms = self.monster_tag
        if ms:
            r = random.random()
            for mon in ms:
                r -= mon.wkeit
                if r < 0:
                    return mon.main(mänx)
        return False

    def main(self, mänx: Mänx, von: Opt[Wegpunkt]) -> Wegpunkt:
        tagrest = mänx.welt.tag % 1.0
        if tagrest < 0.5 and tagrest + self.länge >= 0.5:
            if von and mänx.ja_nein("Du wirst nicht vor Ende der Nacht ankommen. "
                                    "Willst du umkehren?"):
                return von
        # frage_nacht = False
        richtung = von == self.p1
        weg_rest = self.länge
        while weg_rest > 0:
            mänx.welt.tick(1 / 24)
            if self.monster_check(mänx):
                # umkehren
                richtung = not richtung
                weg_rest = self.länge - weg_rest
            if mänx.welt.is_nacht():
                if mänx.ja_nein("Willst du ruhen?"):
                    # TODO Monster beim Schlafen!
                    mänx.welt.nächster_tag()
            weg_rest -= 1 / 48 if mänx.welt.is_nacht() else 1 / 24

        if richtung:
            assert self.p2, "Loses Ende!"
            return self.p2
        else:
            assert self.p1, "Loses Ende!"
            return self.p1


class Wegtyp(enum.Enum):
    STRASSE = "Straße", "f"
    ALTE_STRASSE = "alte Straße", "f"
    WEG = "Weg", "m"
    VERFALLENER_WEG = "verfallener Weg", "m"
    PFAD = "Pfad", "m"
    TRAMPELPFAD = "Trampelpfad", "m"

    @property
    def geschlecht(self) -> str:
        return self.value[1]  # pylint: disable=unsubscriptable-object

    def text(self, bestimmt: bool, fall: int) -> str:
        # TODO Kasus der Adjektive
        return ((bartikel if bestimmt else uartikel)(self.geschlecht, fall)
                + " " + self.value[0])  # pylint: disable=unsubscriptable-object


@dataclass
class Richtung:
    ziel: Wegpunkt
    zielname: str = ""
    typ: Wegtyp = Wegtyp.WEG


HIMMELSRICHTUNGEN = [a + "en" for a in (
    "Nord",
    "Nordost",
    "Ost",
    "Südost",
    "Süd",
    "Südwest",
    "West",
    "Nordwest"
)]
HIMMELSRICHTUNG_KURZ = ["n", "no", "o", "so", "s", "sw", "w", "nw"]


class Beschreibung:
    geschichte: Union[Sequence[str], MänxFkt]

    def __init__(self,
                 geschichte: Union[Sequence[str], MänxFkt],
                 nur: Opt[Collection[Opt[str]]] = None,
                 außer: Opt[Collection[Opt[str]]] = None):
        if isinstance(geschichte, str):
            self.geschichte = [geschichte]
        else:
            self.geschichte = geschichte
        if nur and außer:
            raise TypeError("Nur und außer können nicht gleichzeitig gegeben "
                            "sein.")
        self.nur = self._nur(nur)
        self.außer = self._nur(außer)

    def beschreibe(self, mänx: Mänx, von: Opt[str]):
        if (not self.nur or von in self.nur) and (
                not self.außer or von not in self.außer):
            if callable(self.geschichte):
                return self.geschichte(mänx)
            else:
                for g in self.geschichte[:-1]:
                    malp(g)
                mint(self.geschichte[-1])
        return None

    @staticmethod
    def _nur(nur: Opt[Collection[Opt[str]]]) -> Opt[Collection[Opt[str]]]:
        if isinstance(nur, str):
            return [nur]
        else:
            return nur

def cap(a: str) -> str:
    return a[:1].upper() + a[1:]

class Wegkreuzung(Wegpunkt, InventarBasis):
    OPTS = [4, 3, 5, 2, 6, 1, 7, 0]

    def __init__(self,
                 n: Opt[Richtung] = None,
                 nw: Opt[Richtung] = None,
                 no: Opt[Richtung] = None,
                 o: Opt[Richtung] = None,
                 w: Opt[Richtung] = None,
                 sw: Opt[Richtung] = None,
                 so: Opt[Richtung] = None,
                 s: Opt[Richtung] = None,
                 gucken: Opt[MänxFkt] = None,
                 kreuzung_beschreiben: bool = False,
                 immer_fragen: bool = False):
        # TODO gucken
        super().__init__()
        self.richtungen = [n, no, o, so, s, sw, w, nw]
        for ri in self.richtungen:
            if ri:
                ri.ziel.verbinde(self)
        self.beschreibungen: List[Beschreibung] = []
        self.menschen: List['xwatc.dorf.NSC'] = []
        self.gucken = gucken
        self.immer_fragen = immer_fragen
        self.kreuzung_beschreiben = kreuzung_beschreiben

    def add_beschreibung(self,
                         geschichte: Union[Sequence[str], MänxFkt],
                         nur: Opt[Sequence[Opt[str]]] = None,
                         außer: Opt[Sequence[Opt[str]]] = None):
        self.beschreibungen.append(Beschreibung(geschichte, nur, außer))

    def add_effekt(self,
                         geschichte: Union[Sequence[str], MänxFkt],
                         nur: Opt[Sequence[Opt[str]]] = None,
                         außer: Opt[Sequence[Opt[str]]] = None):
        self.beschreibungen.append(Beschreibung(geschichte, nur, außer))

    def beschreibe(self, mänx: Mänx, richtung: Opt[int]):
        ri_name = HIMMELSRICHTUNG_KURZ[richtung] if richtung is not None else None
        for beschreibung in self.beschreibungen:
            beschreibung.beschreibe(mänx, ri_name)
        if self.kreuzung_beschreiben or not self.beschreibungen:
            self.beschreibe_kreuzung(richtung)

    def beschreibe_kreuzung(self, richtung: Opt[int]):  # pylint: disable=unused-argument
        rs = self.richtungen
        if richtung is not None:
            rit = cast(Richtung, rs[richtung]).typ
            gegen = (richtung + 4) % 8
            iri = sum(map(bool, rs))
            if iri == 1:
                print("Sackgasse.")
            elif iri == 2:
                andere = next(i for i, v in enumerate(rs)
                              if v and i != richtung)
                atyp = cast(Richtung, rs[andere]).typ
                if andere == gegen:
                    if rit != atyp:
                        print(cap(rit.text(True, 1)),
                              "wird zu", atyp.text(False, 3))
                else:
                    print(cap(rit.text(True, 1)), "biegt nach",
                          HIMMELSRICHTUNGEN[andere], "ab", end="")
                    if rit != atyp:
                        print(" und wird zu", atyp.text(False, 3))
                    else:
                        print(".")
            else:
                print("Du kommst an eine Kreuzung.")
                for i, ri in enumerate(rs):
                    if ri and i != richtung:
                        print(cap(ri.typ.text(False, 1)), "führt nach",
                              HIMMELSRICHTUNGEN[i] + ".")

        else:
            print("Du kommst auf eine Wegkreuzung.")
            for i, ri in enumerate(rs):
                if ri:
                    print(cap(ri.typ.text(False, 1)), "führt nach",
                          HIMMELSRICHTUNGEN[i] + ".")

    def optionen(self, mänx: Mänx,  # pylint: disable=unused-argument
                 von: Opt[int]) -> Iterable[MenuOption[Wegpunkt]]:
        for rirel in self.OPTS:
            if von is None:
                riabs = rirel
            else:
                riabs = (rirel + von) % 8
            himri = HIMMELSRICHTUNGEN[riabs]
            ri = self.richtungen[riabs]
            if not ri:
                continue
            if riabs == von:
                yield ("Umkehren", "fliehen", ri.ziel)
            else:
                if ri.zielname:
                    ziel = ri.zielname + " im " + himri
                else:
                    ziel = himri
                yield (cap(ri.typ.text(True, 4)) + " nach " + ziel,
                       himri.lower(), ri.ziel)

    def get_nachbarn(self)->List[Wegpunkt]:
        return [ri.ziel for ri in self.richtungen if ri]

    def main(self, mänx: Mänx, von: Opt[Wegpunkt]) -> Wegpunkt:
        if von != self:
            if von:
                richtung = next((
                    i for i, v in enumerate(self.richtungen) if v and v.ziel == von
                ), None)
            else:
                richtung = None
            self.beschreibe(mänx, richtung)
        opts = list(self.optionen(mänx, richtung))
        if not self.immer_fragen and ((richtung is None) + len(opts)) <= 2:
            return opts[0][2]
        return mänx.menu(opts, frage="Welchem Weg nimmst du?")

    def verbinde(self,  # pylint: disable=arguments-differ
                 anderer: Wegpunkt, richtung: str = "",
                 typ: Wegtyp = Wegtyp.WEG, ziel: str = ""):
        if richtung:
            ri = HIMMELSRICHTUNG_KURZ.index(richtung)
            anderer.verbinde(self)
            self.richtungen[ri] = Richtung(anderer, ziel, typ)

    def verbinde_mit_weg(self, nach: Wegkreuzung, länge: float,
                         richtung: str,
                         richtung2: Opt[str] = None,
                         typ: Wegtyp = Wegtyp.WEG,
                         beschriftung_hin: str = "",
                         beschriftung_zurück: str = "",
                         **kwargs):
        """Verbinde zwei Kreuzungen mit einem Weg."""
        ri = HIMMELSRICHTUNG_KURZ.index(richtung)
        if richtung2 is None:
            ri2 = (ri + 4) % 8
        else:
            ri2 = HIMMELSRICHTUNG_KURZ.index(richtung2)
        weg = Weg(länge, self, nach, **kwargs)
        assert not (self.richtungen[ri] or nach.richtungen[ri2]
                    ), "Überschreibt bisherigen Weg."
        self.richtungen[ri] = Richtung(weg, beschriftung_hin, typ=typ)
        nach.richtungen[ri2] = Richtung(weg, beschriftung_zurück, typ=typ)


class WegAdapter(_Strecke):
    """Ein Übergang von Wegesystem zum normalen System."""

    def __init__(self, nächster: Opt[Wegpunkt], zurück: MänxFkt,
                 name: str = ""):
        super().__init__(nächster, None)
        self.zurück = zurück
        self.name = name
        if name:
            ADAPTER[name] = self

    def main(self, mänx: Mänx, von: Opt[Wegpunkt]) -> Union[Wegpunkt, WegEnde]:
        if von:
            return WegEnde(self.zurück)
        assert self.p1, "Loses Ende"
        return self.p1


class Gebietsende(_Strecke):
    """Das Ende eines Gebietes ist der Anfang eines anderen."""

    def __init__(self, von: Opt[Wegpunkt], gebiet: str,
                 port: str, nach: str):
        """Erzeuge ein Gebietsende.

        >>> Gebietsende(None, "jtg:mitte", "mit-gkh", "jtg:gkh")
        """
        super().__init__(von, None)
        self.gebiet = gebiet
        self.nach = nach
        self.port = port
        self.von = von
        assert ((self.gebiet, self.port) not in EINTRITTSPUNKTE
                ), "Eintrittspunkt existiert schon!"
        EINTRITTSPUNKTE[self.gebiet, self.port] = self
        assert self.gebiet in GEBIETE, f"Unbekanntes Gebiet: {self.gebiet}"
        assert nach in GEBIETE, f"Unbekanntes Gebiet: {nach}"

    def main(self, mänx: Mänx, von: Opt[Wegpunkt]) -> Wegpunkt:
        if self.p2:
            return self.p2
        else:
            get_gebiet(mänx, self.nach)
            try:
                self.p2 = EINTRITTSPUNKTE[self.nach, self.port].von
                assert self.p2, "Loses Ende!"
            except KeyError:
                raise KeyError("Erstellen des Gebietes ")
            else:
                return self.p2


def get_gebiet(mänx: Mänx, name_or_gebiet: Union[Wegpunkt, str]) -> Wegpunkt:
    if isinstance(name_or_gebiet, str):
        if name_or_gebiet in ADAPTER:
            return ADAPTER[name_or_gebiet]
        return mänx.welt.get_or_else(
            "weg:" + name_or_gebiet, GEBIETE[name_or_gebiet], mänx)
    else:
        return name_or_gebiet


def gebiet(name: str):
    """Dekorator für Gebietserzeugungsfunktionen."""
    def wrapper(funk):
        GEBIETE[name] = funk
        return funk
    return wrapper


def wegsystem(mänx: Mänx, start: Union[Wegpunkt, str]) -> None:
    """Startet das Wegsystem mit mänx am Wegpunkt start."""
    wp: Union[Wegpunkt, WegEnde] = get_gebiet(mänx, start)
    last = None
    while not isinstance(wp, WegEnde):
        try:
            mänx.context = wp
            last, wp = wp, wp.main(mänx, von=last)
            mänx.welt.tick(1 / 96)
        finally:
            mänx.context = None
    wp.weiter(mänx)  # type: ignore
