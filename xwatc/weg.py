"""
Wegpunkte für JTGs Wegesystem.
Created on 17.10.2020
"""
from __future__ import annotations
import enum
import random
from dataclasses import dataclass
from xwatc.utils import uartikel, bartikel, adj_endung
import typing
from typing import (List, Any, Optional as Opt, cast, Iterable, Union, Sequence,
                    Collection, Callable, Dict, Tuple, NewType, Mapping,
                    overload)
try:
    from typing import runtime_checkable, Protocol
except ImportError:
    from typing_extensions import runtime_checkable, Protocol
from xwatc.system import Mänx, MenuOption, MänxFkt, InventarBasis, malp, mint
from xwatc import dorf
__author__ = "jasper"

GEBIETE: Dict[str, Callable[[Mänx], Wegpunkt]] = {}
# Die Verbindungen zwischen Gebieten
EINTRITTSPUNKTE: Dict[Tuple[str, str], 'Gebietsende'] = {}
ADAPTER: Dict[str, 'WegAdapter'] = {}


@enum.unique
class Ereignis(enum.Enum):
    KAMPF = enum.auto()
    MORD = enum.auto()
    DIEBSTAHL = enum.auto()


class Context(Protocol):
    def melde(self, mänx: Mänx, ereignis: Ereignis, data: Any) -> Any:
        """Melde ein Ereignis an den Kontext"""


@dataclass
class WegEnde:
    weiter: MänxFkt


@runtime_checkable
class Wegpunkt(Context, Protocol):
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
    ALTE_STRASSE = "alt# Straße", "f"
    WEG = "Weg", "m"
    VERFALLENER_WEG = "verfallen# Weg", "m"
    PFAD = "Pfad", "m"
    TRAMPELPFAD = "Trampelpfad", "m"

    @property
    def geschlecht(self) -> str:
        return self.value[1]  # pylint: disable=unsubscriptable-object

    def text(self, bestimmt: bool, fall: int) -> str:
        nom = self.value[0]  # pylint: disable=unsubscriptable-object
        if "#" in nom:
            nom = nom.replace("#", adj_endung(bestimmt, self.geschlecht, fall))
        return ((bartikel if bestimmt else uartikel)(self.geschlecht, fall)
                + " " + nom)

    def __format__(self, format_spec: str) -> str:
        if 2 <= len(format_spec) <= 3:
            fall = int(format_spec[1])
            if format_spec[0] == "g":
                ans = bartikel(self.geschlecht, fall)
            else:
                bestimmt = format_spec[0] == '1'
                ans = self.text(bestimmt, fall)
            if format_spec[2:] in ("1", "c"):
                return cap(ans)
            else:
                return ans
        else:
            return super().__format__(format_spec)


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


RiIn = Union[None, Wegpunkt, Richtung]
_NotSpecifiedT = NewType("_NotSpecifiedT", object)
_NSpec = _NotSpecifiedT(object())
OpRiIn = Union[RiIn, _NotSpecifiedT]


def _to_richtung(richtung: RiIn) -> Opt[Richtung]:
    if isinstance(richtung, Richtung) or richtung is None:
        return richtung
    else:
        return Richtung(ziel=richtung)


class Wegkreuzung(Wegpunkt, InventarBasis):
    OPTS = [4, 3, 5, 2, 6, 1, 7, 0]

    def __init__(self,
                 n: OpRiIn = _NSpec,
                 nw: OpRiIn = _NSpec,
                 no: OpRiIn = _NSpec,
                 o: OpRiIn = _NSpec,
                 w: OpRiIn = _NSpec,
                 sw: OpRiIn = _NSpec,
                 so: OpRiIn = _NSpec,
                 s: OpRiIn = _NSpec,
                 andere: Opt[Mapping[str, RiIn]] = None,
                 gucken: Opt[MänxFkt] = None,
                 kreuzung_beschreiben: bool = False,
                 immer_fragen: bool = False,
                 menschen: Opt[Sequence[dorf.NSC]] = None):
        # TODO gucken
        super().__init__()
        richtungen = [n, no, o, so, s, sw, w, nw]
        if andere:
            self.nachbarn = {name: _to_richtung(v)
                             for name, v in andere.items()}
        else:
            self.nachbarn = {}
        for richtung, name in zip(richtungen, HIMMELSRICHTUNG_KURZ):
            if richtung is not _NSpec:
                self.nachbarn[name] = _to_richtung(cast(RiIn, richtung))
        for ri in self.nachbarn.values():
            if ri:
                ri.ziel.verbinde(self)
        self.beschreibungen: List[Beschreibung] = []
        if menschen:
            self.menschen = list(menschen)
        else:
            self.menschen = []
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

    @overload
    def __getitem__(self, i: slice) -> List[Opt[Richtung]]: ...

    @overload
    def __getitem__(self, i: int) -> Opt[Richtung]: ...

    @overload
    def __getitem__(self, i: str) -> Richtung: ...

    def __getitem__(self, i):
        if isinstance(i, slice):
            return [self.nachbarn.get(hri) for hri in HIMMELSRICHTUNG_KURZ[i]]
        elif isinstance(i, int):
            return self.nachbarn.get(HIMMELSRICHTUNG_KURZ[i])
        elif isinstance(i, str):
            ans = self.nachbarn[i]
            if ans is None:
                raise ValueError(f"Loses Ende: {i} nicht besetzt")
            return ans
        raise TypeError(i, "must be str, int or slice.")

    def _finde_texte(self, richtung: int) -> List[str]:
        rs = self[richtung:] + self[:richtung]
        ans: List[str] = []
        min_arten = 8
        for flt, txt in WEGPUNKTE_TEXTE:
            typen: Dict[int, Wegtyp] = {}
            art_count = 0
            for stp, tp in zip(rs, flt):
                if tp == 0 and stp is None:
                    continue
                elif tp != 0 and stp is not None:
                    if tp in typen:
                        if typen[tp] != stp.typ:
                            break
                    else:
                        art_count += 1
                        typen[tp] = stp.typ
                else:
                    break
            else:
                if art_count < min_arten:
                    ans.clear()
                elif art_count > min_arten:
                    continue
                ans.append(txt.format(w=typen))
        return ans

    def beschreibe_kreuzung(self, richtung: Opt[int]):  # pylint: disable=unused-argument
        rs = self[:]
        if richtung is not None:
            texte = self._finde_texte(richtung)
            if texte:
                malp(random.choice(texte))
            else:
                malp("Du kommst an eine Kreuzung.")
                for i, ri in enumerate(rs):
                    if ri and i != richtung:
                        malp(cap(ri.typ.text(False, 1)), "führt nach",
                             HIMMELSRICHTUNGEN[i] + ".")

        else:
            malp("Du kommst auf eine Wegkreuzung.")
            for i, ri in enumerate(rs):
                if ri:
                    malp(cap(ri.typ.text(False, 1)), " führt nach ",
                         HIMMELSRICHTUNGEN[i] + ".")

    def optionen(self, mänx: Mänx,  # pylint: disable=unused-argument
                 von: Opt[int]) -> Iterable[MenuOption[
                     Union[Wegpunkt, 'dorf.NSC']]]:
        for mensch in self.menschen:
            yield ("Mit " + mensch.name + " reden", mensch.name.lower(),
                   mensch)
        for rirel in self.OPTS:
            if von is None:
                riabs = rirel
            else:
                riabs = (rirel + von) % 8
            himri = HIMMELSRICHTUNGEN[riabs]
            ri: Opt[Richtung] = self[riabs]
            if not ri:
                continue
            if riabs == von:
                yield ("Umkehren", himri.lower(), ri.ziel)
            else:
                if ri.zielname:
                    ziel = ri.zielname + " im " + himri
                else:
                    ziel = himri
                yield (cap(ri.typ.text(True, 4)) + " nach " + ziel,
                       himri.lower(), ri.ziel)

    def get_nachbarn(self)->List[Wegpunkt]:
        return [ri.ziel for ri in self.nachbarn.values() if ri]

    def main(self, mänx: Mänx, von: Opt[Wegpunkt]) -> Wegpunkt:
        if von != self:
            if von:
                richtung = next((
                    i for i, v in enumerate(self[:]) if v and v.ziel == von
                ), None)
            else:
                richtung = None
            self.beschreibe(mänx, richtung)
        opts = list(self.optionen(mänx, richtung))
        if not self.immer_fragen and ((richtung is None) + len(opts)) <= 2:
            if isinstance(opts[0][2], Wegpunkt):
                return opts[0][2]
        ans = mänx.menu(opts, frage="Welchem Weg nimmst du?")
        if isinstance(ans, Wegpunkt):
            return ans
        elif isinstance(ans, dorf.NSC):
            ans.main(mänx)
        return self

    def verbinde(self,  # pylint: disable=arguments-differ
                 anderer: Wegpunkt, richtung: str = "",
                 typ: Wegtyp = Wegtyp.WEG, ziel: str = ""):
        if richtung:
            anderer.verbinde(self)
            self.nachbarn[richtung] = Richtung(anderer, ziel, typ)
        else:
            for key, val in self.nachbarn.items():
                if val is None:
                    self.nachbarn[key] = Richtung(anderer, ziel, typ)
                    break

    def verbinde_mit_weg(self, nach: Wegkreuzung, länge: float,
                         richtung: str,
                         richtung2: Opt[str] = None,
                         typ: Wegtyp = Wegtyp.WEG,
                         beschriftung_hin: str = "",
                         beschriftung_zurück: str = "",
                         **kwargs):
        """Verbinde zwei Kreuzungen mit einem Weg."""

        if richtung2 is None:
            ri = HIMMELSRICHTUNG_KURZ.index(richtung)
            ri2 = HIMMELSRICHTUNG_KURZ[(ri + 4) % 8]
        else:
            ri2 = richtung2
        weg = Weg(länge, self, nach, **kwargs)
        assert not (self.nachbarn.get(richtung) or nach.nachbarn.get(ri2)
                    ), "Überschreibt bisherigen Weg."
        self.nachbarn[richtung] = Richtung(weg, beschriftung_hin, typ=typ)
        nach.nachbarn[ri2] = Richtung(weg, beschriftung_zurück, typ=typ)


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

    def __init__(self, von: Opt[Wegpunkt],
                 gebiet: str,  # pylint: disable=redefined-outer-name
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
    """Lade ein Gebiet von seinem Namen."""
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


WEGPUNKTE_TEXTE: List[Tuple[List[int], str]] = [

    ([1, 0, 0, 0, 2, 0, 0, 0], "{w[1]:111} wird zu {w[2]:03}"),
    # Kurven
    ([1, 1, 0, 0, 0, 0, 0, 0],
     "{w[1]:111} macht eine scharfe Biegung nach links."),
    ([1, 0, 1, 0, 0, 0, 0, 0],
     "{w[1]:111} biegt nach links ab."),
    ([1, 0, 1, 0, 0, 0, 0, 0],
     "Du biegst nach links ab."),
    ([1, 0, 0, 1, 0, 0, 0, 0],
     "{w[1]:111} macht eine leichte Biegung nach links."),
    ([1, 0, 0, 0, 1, 0, 0, 0], "{w[1]:111} führt weiter geradeaus."),
    ([1, 0, 0, 0, 0, 1, 0, 0],
     "{w[1]:111} macht eine leichte Biegung nach rechts."),
    ([1, 0, 0, 0, 0, 0, 1, 0],
     "{w[1]:111} biegt nach rechts ab."),
    ([1, 0, 0, 0, 0, 0, 0, 1],
     "{w[1]:111} macht eine scharfe Biegung nach rechts."),
    # T-Kreuzungen
    ([1, 0, 2, 0, 0, 0, 2, 0], "{w[1]:111} endet orthogonal an {w[2]:03}."),
    ([1, 2, 0, 0, 0, 2, 0, 0], "{w[1]:111} mündet in {w[2]:04}, {w[2]:g1} von "
     "scharf links nach rechts führt."),
    ([1, 2, 0, 0, 2, 0, 0, 0], "{w[1]:111} vereinigt sich mit {w[2]:03}, der geradeaus "
     "weiterführt."),
    ([1, 0, 2, 0, 1, 0, 2, 0], "{w[2]:011} kreuzt senkrecht."),
    ([1, 0, 0, 0, 0, 0, 0, 0], "Eine Sackgasse.")
]
