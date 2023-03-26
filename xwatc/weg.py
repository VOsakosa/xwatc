"""
Wegpunkte für JTGs Wegesystem.
Created on 17.10.2020
"""
from __future__ import annotations
from collections.abc import Collection, Callable, Iterable, Iterator, Mapping, Sequence
import enum
import random
from dataclasses import dataclass
from xwatc.utils import uartikel, bartikel, adj_endung, UndPred
import typing
from typing import (Any, Optional as Opt, cast, Union, NewType,
                    overload, TYPE_CHECKING,
                    runtime_checkable, Protocol)
from xwatc.system import (Mänx, MenuOption, MänxFkt, InventarBasis, malp, mint,
                          MänxPrädikat)
if TYPE_CHECKING:
    from xwatc import nsc
    from xwatc import dorf

__author__ = "jasper"

GEBIETE: dict[str, Callable[[Mänx], 'Wegpunkt']] = {}
# Die Verbindungen zwischen Gebieten
EINTRITTSPUNKTE: dict[tuple[str, str], 'Gebietsende'] = {}
ADAPTER: dict[str, 'WegAdapter'] = {}


@dataclass
class WegEnde:
    """Wird vom Wegpunkt zurückgegeben und markiert, dass das
    Wegsystem hier zu Ende ist und in das alte, MänxFkt-basierte
    System übergegangen wird.
    """
    weiter: MänxFkt


@runtime_checkable
class Wegpunkt(Protocol):
    """Wegpunkte sind die Einheiten im Wegegraph.
    """

    def get_nachbarn(self) -> list[Wegpunkt]:
        """Gebe eine Liste von Nachbarn aus, sprich Wegpunkte, die von
        hier aus erreichbar sind."""
        return []

    def main(self, _mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt | WegEnde:
        """Betrete den Wegpunkt mit mänx aus von."""

    def verbinde(self, _anderer: Wegpunkt):
        """Verbinde den Wegpunkt mit anderen. Nur für Wegpunkte mit nur einer
        Seite."""


class _Strecke(Wegpunkt):
    """Abstrakte Basisklasse für Wegpunkte, die zwei Orte verbinden."""

    def __init__(self, p1: Wegpunkt | None, p2: Wegpunkt | None = None):
        super().__init__()
        self.p1 = self._verbinde(p1)
        self.p2 = self._verbinde(p2)

    def _verbinde(self, anderer: Wegpunkt | None) -> Wegpunkt | None:
        """Ruft anderer.verbinde(self) auf."""
        if anderer:
            anderer.verbinde(self)
        return anderer

    def get_nachbarn(self) -> list[Wegpunkt]:
        return [a for a in (self.p1, self.p2) if a]

    def verbinde(self, anderer: Wegpunkt) -> None:
        if not self.p1:
            self.p1 = anderer
        elif self.p1 != anderer and not self.p2:
            self.p2 = anderer

    def __repr__(self):
        return (f"{type(self).__name__} von {type(self.p1).__name__} "
                f"nach {type(self.p2).__name__}")


class MonsterChance:
    """Eine Möglichkeit eines Monster-Zusammenstoßes."""

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

    def __init__(self, länge: float,
                 p1: Wegpunkt | None = None,
                 p2: Wegpunkt | None = None,
                 monster_tag: Opt[list[MonsterChance]] = None,
                 monster_nachts: Opt[list[MonsterChance]] = None):
        """
        :param länge: Länge in Stunden
        :param p1: Startpunkt
        :param p2: Endpunkt
        :param monster_tag: Monster, die am Tag auftauchen
        """
        super().__init__(p1, p2)
        self.länge = länge / 24
        self.monster_tag = monster_tag
        self.monster_nachts = monster_nachts

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

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt:
        tagrest = mänx.welt.tag % 1.0
        if tagrest < 0.5 and tagrest + self.länge >= 0.5:
            if von and mänx.ja_nein("Du wirst nicht vor Ende der Nacht ankommen. "
                                    "Willst du umkehren?"):
                return von
        ruhen = True
        richtung = von == self.p1
        weg_rest = self.länge
        while weg_rest > 0:
            mänx.welt.tick(1 / 24)
            if self.monster_check(mänx):
                # umkehren
                richtung = not richtung
                weg_rest = self.länge - weg_rest
            if ruhen and mänx.welt.is_nacht():
                if mänx.ja_nein("Es ist Nacht. Willst du ruhen?"):
                    mänx.welt.nächster_tag()
                else:
                    ruhen = False
            weg_rest -= 1 / 48 if mänx.welt.is_nacht() else 1 / 24

        if richtung:
            assert self.p2, "Loses Ende!"
            return self.p2
        else:
            assert self.p1, "Loses Ende!"
            return self.p1


class Wegtyp(enum.Enum):
    """Ein Typ von Weg, mit entsprechenden auto-generierten Meldungen an
    Kreuzungen."""
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
        """Formattierung mit (Bestimmtheit)(Fall)[Großschreibung]"""
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
    """Stellt eine wählbare Richtung an einem Wegpunkt dar."""
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
_StrAsHimmelsrichtung = NewType("_StrAsHimmelsrichtung", str)



class Himmelsrichtung:
    """Himmelsrichtungen sind besondere Richtungen an Kreuzungen."""

    def __init__(self, kurz: str, nr: int) -> None:
        self.kurz = kurz
        self.nr = nr

    @classmethod
    def from_kurz(cls, kurz: str) -> 'NachbarKey':
        try:
            nr = HIMMELSRICHTUNG_KURZ.index(kurz)
            return cls(kurz, nr)
        except ValueError:
            return _StrAsHimmelsrichtung(kurz)

    @classmethod
    def from_nr(cls, nr: int) -> Himmelsrichtung:
        return cls(HIMMELSRICHTUNG_KURZ[nr], nr)

    def __add__(self, other: int | Himmelsrichtung) -> Himmelsrichtung:
        if isinstance(other, Himmelsrichtung):
            other = other.nr
        return self.from_nr((self.nr + other) % 8)

    def __format__(self, spec):
        return format(HIMMELSRICHTUNGEN[self.nr], spec)

    def __hash__(self):
        return hash(self.kurz)

    def __eq__(self, other):
        if isinstance(other, Himmelsrichtung):
            return other.nr == self.nr
        return self.kurz == other

    def __str__(self):
        return self.kurz

NachbarKey = _StrAsHimmelsrichtung | Himmelsrichtung


class Beschreibung:
    """Das Äquivalent von Dialogen für Wegpunkte.

    Eine Beschreibung besteht aus einer Geschichte und Richtungseinschränkungen.
    Wenn der Mänx den Wegpunkt aus einer der genannten Richtungen betritt, wird
    die Beschreibung abgespielt.
    """
    geschichte: Sequence[str] | MänxFkt

    def __init__(self,
                 geschichte: Sequence[str] | MänxFkt,
                 nur: Collection[str | None] | None = None,
                 außer: Collection[str | None] | None = None,
                 warten: bool = False):
        if isinstance(geschichte, str):
            self.geschichte = [geschichte]
        else:
            self.geschichte = geschichte
        if nur and außer:
            raise TypeError("Nur und außer können nicht gleichzeitig gegeben "
                            "sein.")
        self.nur = self._nur(nur)
        self.außer = self._nur(außer)
        self.warten = warten

    def beschreibe(self, mänx: Mänx, von: str | None) -> Any | None:
        """Führe die Beschreibung aus."""
        if (not self.nur or von in self.nur) and (
                not self.außer or von not in self.außer):
            if callable(self.geschichte):
                return self.geschichte(mänx)
            else:
                for g in self.geschichte[:-1]:
                    malp(g)
                if self.warten:
                    mint(self.geschichte[-1])
                else:
                    malp(self.geschichte[-1])
        return None

    @staticmethod
    def _nur(nur: Opt[Collection[str | None]]) -> Opt[Collection[str | None]]:
        """Macht einen String zu einer Liste von Strings"""
        if isinstance(nur, str):
            return [nur]
        else:
            return nur


def cap(a: str) -> str:
    """Macht den ersten Buchstaben groß."""
    return a[:1].upper() + a[1:]


RiIn = Union[None, Wegpunkt, Richtung]
_NotSpecifiedT = NewType("_NotSpecifiedT", object)
_NSpec = _NotSpecifiedT(object())
OpRiIn = Union[RiIn, _NotSpecifiedT]


def _to_richtung(richtung: RiIn) -> Richtung | None:
    if isinstance(richtung, Richtung) or richtung is None:
        return richtung
    else:
        return Richtung(ziel=richtung)


class Wegkreuzung(Wegpunkt, InventarBasis):
    """Eine Wegkreuzung enthält ist ein Punkt, wo
    1) mehrere Wege fortführen
    2) NSCs herumstehen, mit denen interagiert werden kann.

    Hier passiert etwas.
    """
    OPTS = [4, 3, 5, 2, 6, 1, 7]
    nachbarn: dict[NachbarKey, Richtung | None]

    def __init__(self,
                 name: str,
                 n: OpRiIn = _NSpec,
                 nw: OpRiIn = _NSpec,
                 no: OpRiIn = _NSpec,
                 o: OpRiIn = _NSpec,
                 w: OpRiIn = _NSpec,
                 sw: OpRiIn = _NSpec,
                 so: OpRiIn = _NSpec,
                 s: OpRiIn = _NSpec,
                 andere: Opt[Mapping[str, RiIn]] = None,
                 gucken: MänxFkt | None = None,
                 kreuzung_beschreiben: bool = False,
                 immer_fragen: bool = False,
                 menschen: Sequence[dorf.NSC | nsc.NSC] = ()):
        """Erzeuge eine neue Wegkreuzung
        :param n,nw,no,o,w,sw,s,so: Nachbarn nach Himmelsrichtungen
        :param andere: weitere Nachbarn
        :param gucken: das passiert beim gucken
        :param kreuzung_beschreiben: Ob die Kreuzung sich anhand ihrer
        angrenzenden Wege beschreiben soll.
        :param immer_fragen: immer fragen, wie weitergegangen werden soll, auch
        wenn es keine Abzweigung ist
        :param menschen: Menschen, die an der Wegkreuzung stehen und angesprochen werden können.
        """
        # TODO gucken
        super().__init__()
        self.name = name
        richtungen = [n, no, o, so, s, sw, w, nw]
        if andere:
            self.nachbarn = {Himmelsrichtung.from_kurz(name): _to_richtung(v)
                             for name, v in andere.items()}
        else:
            self.nachbarn = {}
        for richtung, nr in zip(richtungen, range(8)):
            if richtung is not _NSpec:
                self.nachbarn[Himmelsrichtung.from_nr(
                    nr)] = _to_richtung(cast(RiIn, richtung))
        for ri in self.nachbarn.values():
            if ri:
                ri.ziel.verbinde(self)
        self.beschreibungen: list[Beschreibung] = []
        self.menschen = list(menschen)
        self.gucken = gucken
        self.immer_fragen = immer_fragen
        self.kreuzung_beschreiben = kreuzung_beschreiben
        self._gebiet: str | None = None
        self._wenn_fn: dict[str, MänxPrädikat] = {}

    def add_beschreibung(self,
                         geschichte: Sequence[str] | MänxFkt,
                         nur: Sequence[str | None] | None = None,
                         außer: Sequence[str | None] | None = None,
                         warten: bool = False):
        """Füge eine Beschreibung hinzu, die immer abgespielt wird, wenn
        der Wegpunkt betreten wird."""
        self.beschreibungen.append(
            Beschreibung(geschichte, nur, außer, warten))

    def add_effekt(self,
                   geschichte: Sequence[str] | MänxFkt,
                   nur: Sequence[str | None] | None = None,
                   außer: Sequence[str | None] | None = None,
                   warten: bool = True):
        """Füge eine Geschichte hinzu, die passiert, wenn der Ort betreten
        wird."""
        self.beschreibungen.append(
            Beschreibung(geschichte, nur, außer, warten))

    def wenn(self, richtung: str, fn: MänxPrädikat) -> None:
        """Erlaube eine Richtung nur, wenn die folgende Funktion wahr ist.
        Mehrere Funktionen werden verundet.
        """
        if richtung in self._wenn_fn:
            self._wenn_fn[richtung] = UndPred(self._wenn_fn[richtung], fn)
        else:
            self._wenn_fn[richtung] = fn

    def beschreibe(self, mänx: Mänx, ri_name: str | Himmelsrichtung | None):
        """Beschreibe die Kreuzung von richtung kommend.

        Beschreibe muss idempotent sein, das heißt, mehrfache Aufrufe verändern
        die Welt nicht anders als ein einfacher Aufruf. Denn beim Laden wird
        die Beschreibung mehrfach durchgeführt.
        """
        for beschreibung in self.beschreibungen:
            beschreibung.beschreibe(mänx, str(ri_name))
        if ri_name and (self.kreuzung_beschreiben or not self.beschreibungen):
            if isinstance(ri_name, Himmelsrichtung):
                self.beschreibe_kreuzung(ri_name.nr)
            else:
                self.beschreibe_kreuzung(None)
        # for mensch in self.menschen:
        #    mensch.vorstellen(mänx)

    @overload
    def __getitem__(
        self, i: slice) -> list[Richtung | None]: ...  # @UnusedVariable

    @overload
    def __getitem__(self, i: int) -> Richtung | None: ...  # @UnusedVariable

    @overload
    def __getitem__(self, i: str) -> Richtung: ...  # @UnusedVariable

    def __getitem__(self, i):
        match i:
            case slice() as i:
                return [self.nachbarn.get(Himmelsrichtung.from_nr(hri)) for hri in range(8)[i]]
            case int(i):
                return self.nachbarn.get(Himmelsrichtung.from_nr(i))
            case str() | Himmelsrichtung():
                if isinstance(i, str):
                    i = _StrAsHimmelsrichtung(i)
                ans = self.nachbarn[i]
                if ans is None:
                    raise KeyError(f"Loses Ende: {i} nicht besetzt")
                return ans
        raise TypeError(i, "must be str, int or slice.")

    def _finde_texte(self, richtung: int) -> list[str]:
        """Finde die Beschreibungstexte, die auf die Kreuzung passen."""
        rs = self[richtung:] + self[:richtung]
        ans: list[str] = []
        min_arten = 8
        for flt, txt in WEGPUNKTE_TEXTE:
            typen: dict[int, Wegtyp] = {}
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

    def beschreibe_kreuzung(self, richtung: int | None):  # pylint: disable=unused-argument
        """Beschreibe die Kreuzung anhand ihrer Form."""
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

    def optionen(self, mänx: Mänx,
                 von: NachbarKey | None) -> Iterable[MenuOption[
                     Union[Wegpunkt, 'dorf.NSC', 'nsc.NSC']]]:
        """Sammelt Optionen, wie der Mensch sich verhalten kann."""
        for mensch in self.menschen:
            yield ("Mit " + mensch.name + " reden", mensch.name.lower(),
                   mensch)
        for ri, himri in self._richtungen(mänx, von):
            if himri == von:
                if ri.zielname:
                    yield (f"Zurück ({ri.zielname})", "f", ri.ziel)
                else:
                    yield ("Umkehren", "f", ri.ziel)
            else:
                if ri.zielname:
                    ziel = ri.zielname
                elif isinstance(himri, Himmelsrichtung):
                    ziel = f"Nach {himri}"
                    # ziel = cap(ri.typ.text(True, 4)) + f" nach {himri}"
                else:
                    ziel = himri
                yield (ziel, format(himri).lower(), ri.ziel)

    def _richtungen(self, mänx: Mänx, von: NachbarKey | None
                    ) -> Iterator[tuple[Richtung, NachbarKey]]:
        """Liste alle möglichen Richtungen in der richtigen Reihenfolge auf.

        Zuerst kommen die Himmelsrichtungen, je gerader desto besser.
        Dann kommen die speziellen Orte.
        """
        def inner() -> Iterator[tuple[NachbarKey, Richtung | None]]:
            if isinstance(von, Himmelsrichtung):
                for rirel in self.OPTS:
                    riabs = von + rirel
                    if riabs in self.nachbarn:
                        yield riabs, self.nachbarn[riabs]
                for name, richtung in self.nachbarn.items():
                    if not isinstance(name, Himmelsrichtung):
                        yield name, richtung
                yield von, self.nachbarn[von]
            else:
                for name, richtung in self.nachbarn.items():
                    yield name, richtung

        for himri_oder_name, richtung in inner():
            assert richtung, f"Loses Ende: {richtung}"
            name = str(himri_oder_name)
            if name not in self._wenn_fn or self._wenn_fn[name](mänx):
                yield richtung, himri_oder_name

    def get_nachbarn(self) -> list[Wegpunkt]:
        return [ri.ziel for ri in self.nachbarn.values() if ri]

    def main(self, mänx: Mänx, von: Wegpunkt | None = None) -> Wegpunkt:
        """Fragt nach allen Richtungen."""
        from xwatc.nsc import NSC
        von_key = None
        if von is not self:
            for key, value in self.nachbarn.items():
                assert value, f"Loses Ende: {key}"
                if value.ziel is von:
                    von_key = key
                    break
        self.beschreibe(mänx, von_key)
        opts = list(self.optionen(mänx, von_key))
        if not self.immer_fragen and ((von is None) + len(opts)) <= 2:
            if isinstance(opts[0][2], Wegpunkt):
                return opts[0][2]
        ans = mänx.menu(opts, frage="Welchem Weg nimmst du?", save=self)
        if isinstance(ans, Wegpunkt):
            return ans
        elif isinstance(ans, NSC):
            ans.main(mänx)
        return self

    def verbinde(self,  # pylint: disable=arguments-differ
                 anderer: Wegpunkt, richtung: str = "",
                 typ: Wegtyp = Wegtyp.WEG, ziel: str = ""):
        if richtung:
            anderer.verbinde(self)
            hiri = Himmelsrichtung.from_kurz(richtung)
            self.nachbarn[hiri] = Richtung(anderer, ziel, typ)
        else:
            for key, val in self.nachbarn.items():
                if val is None:
                    self.nachbarn[key] = Richtung(anderer, ziel, typ)
                    break

    def verbinde_mit_weg(self,
                         nach: Wegkreuzung,
                         länge: float,
                         richtung: str,
                         richtung2: str | None = None,
                         typ: Wegtyp = Wegtyp.WEG,
                         beschriftung_hin: str = "",
                         beschriftung_zurück: str = "",
                         **kwargs):
        """Verbinde zwei Kreuzungen mit einem Weg.

        :param nach: Zielpunkt
        :param länge: Die Länge des Wegs in Stunden
        """
        ri1 = Himmelsrichtung.from_kurz(richtung)
        if richtung2 is not None:
            ri2 = Himmelsrichtung.from_kurz(richtung2)
        elif isinstance(ri1, Himmelsrichtung):
            ri2 = ri1 + 4
        else:
            raise ValueError("richtung2 muss angegeben werden, wenn "
                             "richtung keine Himmelsrichtung ist.")

        weg = Weg(länge, self, nach, **kwargs)
        assert not (self.nachbarn.get(ri1) or nach.nachbarn.get(ri2)
                    ), "Überschreibt bisherigen Weg."
        self.nachbarn[ri1] = Richtung(weg, beschriftung_hin, typ=typ)
        nach.nachbarn[ri2] = Richtung(weg, beschriftung_zurück, typ=typ)

    def get_state(self):
        """Wenn der Wegpunkt Daten hat, die über die Versionen behalten
        werden sollen."""
        return None


class WegAdapter(_Strecke):
    """Ein Übergang von Wegesystem zum normalen System."""

    def __init__(self, nächster: Wegpunkt | None, zurück: MänxFkt,
                 name: str = ""):
        super().__init__(nächster, None)
        self.zurück = zurück
        self.name = name
        if name:
            ADAPTER[name] = self

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Union[Wegpunkt, WegEnde]:
        if von:
            return WegEnde(self.zurück)
        assert self.p1, "Loses Ende"
        return self.p1


class WegSperre(_Strecke):
    """Eine Stelle, wo der Mänx nur manchmal vorbeikommt. Der Weg ist aber
    sichtbar. Soll der Weg nicht sichtbar sein, so nutze stattdessen die
    wenn-Funktion eines Wegpunkts.

    ## Beispiel
    ```
        def durchgang(mänx):
            malp("Eine kleine Klippe versperrt dir den Weg.")
            if mänx.hat_fertigkeit("Klettern"):
                malp("Du kletterst hoch")
                return True
            malp("Ohne klettern zu können, kommst du nicht hoch.")

        def runter(mänx):
            malp("Du springst eine kleine Klippe herunter.")
            return True
        WegSperre(None, None, runter, durchgang)
    ```
    """

    def __init__(self, start: Wegpunkt | None, ende: Wegpunkt | None,
                 hin: Opt[MänxPrädikat] = None,
                 zurück: Opt[MänxPrädikat] = None):
        super().__init__(start, ende)
        self.hin = hin
        self.zurück = zurück

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Union[Wegpunkt, WegEnde]:
        assert self.p2
        assert self.p1
        if von is self.p1:
            if self.hin and self.hin(mänx):
                return self.p2
            return self.p1
        elif von is self.p2:
            if self.zurück and self.zurück(mänx):
                return self.p1
            return self.p2
        else:
            # Strecke einfach so betreten?
            return self.p1


class Gebietsende(_Strecke):
    """Das Ende eines Gebietes ist der Anfang eines anderen."""

    def __init__(self, von: Wegpunkt | None,
                 gebiet: str,  # pylint: disable=redefined-outer-name
                 port: str, nach: str):
        """Erzeuge ein Gebietsende.

        >>> Gebietsende(None, "jtg:mitte", "mit-gkh", "jtg:gkh")
        """
        super().__init__(von, None)
        self.gebiet = gebiet
        self.nach = nach
        self.port = port
        assert ((self.gebiet, self.port) not in EINTRITTSPUNKTE
                ), "Eintrittspunkt existiert schon!"
        EINTRITTSPUNKTE[self.gebiet, self.port] = self
        assert self.gebiet in GEBIETE, f"Unbekanntes Gebiet: {self.gebiet}"
        assert nach in GEBIETE, f"Unbekanntes Gebiet: {nach}"

    @property
    def von(self) -> Wegpunkt | None:
        return self.p1

    @von.setter
    def von(self, wegpunkt: Wegpunkt | None):
        self.p1 = wegpunkt

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt:
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
    """Dekorator für Gebietserzeugungsfunktionen.

    >>>@gebiet("jtg:banane")
    >>>def erzeuge_banane(mänx: Mänx)-> Wegpunkt:
    >>>    ...
    """
    def wrapper(funk: MänxFkt[Wegpunkt]):
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
    typing.cast(WegEnde, wp).weiter(mänx)


WEGPUNKTE_TEXTE: list[tuple[list[int], str]] = [

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
