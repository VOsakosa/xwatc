"""
Wegpunkte für JTGs Wegesystem.
Created on 17.10.2020
"""
from __future__ import annotations

from attrs import define, field, Factory
from collections.abc import Collection, Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
import enum
from functools import wraps
from logging import getLogger
import random
from typing import (Any, ClassVar, NewType, TYPE_CHECKING, runtime_checkable,
                    Protocol, TypeAlias)
import typing
from typing_extensions import Self

from xwatc.system import (Fortsetzung, Mänx, MenuOption, MänxFkt, malp, mint,
                          MänxPrädikat, Welt, MissingID)
from xwatc.utils import uartikel, bartikel, adj_endung, UndPred
from itertools import repeat


if TYPE_CHECKING:
    from xwatc import nsc
    from xwatc import dorf

__author__ = "jasper"


@dataclass
class WegEnde:
    """Wird vom Wegpunkt zurückgegeben und markiert, dass das
    Wegsystem hier zu Ende ist und in das alte, MänxFkt-basierte
    System übergegangen wird.
    """
    weiter: MänxFkt[Fortsetzung]


@runtime_checkable
class Wegpunkt(Protocol):
    """Wegpunkte sind die Einheiten im Wegegraph.
    """

    def get_nachbarn(self) -> list[Wegpunkt]:
        """Gebe eine Liste von Nachbarn aus, sprich Wegpunkte, die von
        hier aus erreichbar sind."""
        return []

    def main(self, __mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt | WegEnde:
        """Betrete den Wegpunkt mit mänx aus von."""


@runtime_checkable
class Ausgang(Protocol):
    """Ein Wegpunkt mit festen losen Enden."""

    def verbinde(self, __anderer: Wegpunkt):
        """Verbinde diesen Wegpunkt mit anderen."""

    @property
    def wegpunkt(self) -> Wegpunkt:
        """Der Wegpunkt, der zu einem Ausgang gehört."""


class WegpunktAusgang(Wegpunkt, Ausgang):
    """Mixin für Wegpunkte, die selbst Ausgänge sind."""
    @property
    def wegpunkt(self) -> Self:
        return self


class _Strecke(WegpunktAusgang):
    """Abstrakte Basisklasse für Wegpunkte, die zwei Orte verbinden."""

    def __init__(self, p1: Ausgang | None,
                 p2: Ausgang | None = None):
        super().__init__()
        self.p1 = self._verbinde(p1)
        self.p2 = self._verbinde(p2)

    def _verbinde(self, anderer: Ausgang | None) -> Wegpunkt | None:
        """Ruft anderer.verbinde(self) auf."""
        if anderer is None:
            return anderer
        else:
            return anderer.verbinde(self)

    def get_nachbarn(self) -> list[Wegpunkt]:
        return [a for a in (self.p1, self.p2) if a]

    def verbinde(self, anderer: Wegpunkt) -> Wegpunkt:
        if not self.p1:
            self.p1 = anderer
        elif self.p1 != anderer and not self.p2:
            self.p2 = anderer
        return self

    def __repr__(self):
        def name(pk: Wegpunkt | None):
            match pk:
                case None:  # @UnusedVariable
                    return "Leeres Ende"
                case object(name=str(ans)) if ans:  # type: ignore
                    return ans
                case _:
                    return type(pk).__name__
        return (f"{type(self).__name__} von {name(self.p1)} "
                f"nach {name(self.p2)}")


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

    # TODO: Wegkrezung als Argument verbieten
    def __init__(self, länge: float,
                 p1: Ausgang | None = None,
                 p2: Ausgang | None = None,
                 monster_tag: list[MonsterChance] | None = None,
                 monster_nachts: list[MonsterChance] | None = None):
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
        """Verwendet Zeit und bringt den Spieler an die gegenüberliegende Seite."""
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

    @property
    def gegenrichtung(self) -> Himmelsrichtung:
        return self + 4

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


@define
class Richtungsoption:
    """Stellt eine wählbare Richtung an einem Wegpunkt dar."""
    zielname: str = ""
    name_kurz: str = ""
    typ: Wegtyp = Wegtyp.WEG


NachbarKey = _StrAsHimmelsrichtung | Himmelsrichtung
BeschreibungFn = MänxFkt[None | Wegpunkt | WegEnde]


def _geschichte(geschichte: Sequence[str] | BeschreibungFn) -> Sequence[str] | BeschreibungFn:
    """Converter for `Beschreibung.geschichte`, um Strings als Liste aus einem String zu behandeln.
    """
    if isinstance(geschichte, str):
        return (geschichte,)
    return geschichte


def _nur(nur: Collection[str | None]) -> Sequence[str | None]:
    """Macht einen String zu einer Liste von Strings"""
    if isinstance(nur, str):
        return [nur]
    else:
        return [*nur]


@define
class Beschreibung:
    """Das Äquivalent von Dialogen für Wegpunkte.

    Eine Beschreibung besteht aus einer Geschichte und Richtungseinschränkungen.
    Wenn der Mänx den Wegpunkt aus einer der genannten Richtungen betritt, wird
    die Beschreibung abgespielt.
    """
    geschichte: Sequence[str] | BeschreibungFn = field(converter=_geschichte)
    nur: Sequence[str | None] = field(converter=_nur, default=())
    außer: Sequence[str | None] = field(converter=_nur, default=())
    warten: bool = field(default=False)

    @nur.validator  # type: ignore
    def _check_nur(self, _attr, _value) -> None:
        if self.nur and self.außer:
            raise ValueError(
                "nur und außer können nicht beide gesetzt werden.")

    def beschreibe(self, mänx: Mänx, von: str | None) -> Wegpunkt | WegEnde | None:
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


def cap(a: str) -> str:
    """Macht den ersten Buchstaben groß."""
    return a[:1].upper() + a[1:]


def kreuzung(
    name: str,
    gucken: BeschreibungFn | Sequence[str] = (),
    kreuzung_beschreiben: bool = False,
    immer_fragen: bool = False,
    menschen: Sequence[dorf.NSC | nsc.NSC] = (),
    **kwargs: Ausgang
) -> 'Wegkreuzung':
    """Konstruktor für Wegkreuzungen ursprünglichen Typs, die nicht auf einem Gitter liegen,
    aber hauptsächlich Himmelsrichtungen für Richtungen verwenden.
    :param gucken: Füge eine Option gucken hinzu.
    :param nachbarn: Nachbarn der Kreuzung, nach Richtung oder Ziel
    :param immer_fragen: Wenn False, läuft der Mensch automatisch weiter, wenn es nur eine
        Fortsetzung gibt.
    """
    nb = {Himmelsrichtung.from_kurz(
        key): value.wegpunkt for key, value in kwargs.items()}
    ans = Wegkreuzung(name, nb, kreuzung_beschreiben=kreuzung_beschreiben,
                      immer_fragen=immer_fragen, menschen=[*menschen])
    if gucken:
        ans.add_option("Umschauen", "gucken", gucken)
    for ausgang in kwargs.values():
        ausgang.verbinde(ans)
    return ans


@define
class Wegkreuzung(Wegpunkt):
    """Eine Wegkreuzung enthält ist ein Punkt, wo
    1) mehrere Wege fortführen
    2) NSCs herumstehen, mit denen interagiert werden kann.

    :param nachbarn: Nachbarn der Kreuzung, nach Richtung oder Ziel
    :param kreuzung_beschreiben: Ob die Kreuzung sich anhand ihrer
    angrenzenden Wege beschreiben soll.
    :param immer_fragen: immer fragen, wie weitergegangen werden soll, auch
    wenn es keine Abzweigung ist
    :param menschen: Menschen, die an der Wegkreuzung stehen und angesprochen werden können.
    """
    OPTS: ClassVar[Sequence[int]] = [
        4, 3, 5, 2, 6, 1, 7]  # Reihenfolge des Fragens
    name: str
    nachbarn: dict[NachbarKey, Wegpunkt] = field(repr=False)
    _optionen: dict[NachbarKey, Richtungsoption] = field(
        repr=False, factory=dict)
    menschen: list[nsc.NSC] = field(factory=list, repr=False)
    immer_fragen: bool = True
    kreuzung_beschreiben: bool = False
    _gebiet: 'Gebiet | None' = None
    dorf: 'dorf.Dorf | None' = None
    beschreibungen: list[Beschreibung] = field(factory=list)
    _wenn_fn: dict[str, MänxPrädikat] = field(factory=dict)

    def __attrs_pre_init__(self):
        super().__init__()

    def add_beschreibung(self,
                         geschichte: Sequence[str] | BeschreibungFn,
                         nur: Sequence[str | None] = (),
                         außer: Sequence[str | None] = (),
                         warten: bool = False) -> Self:
        """Füge eine Beschreibung hinzu, die immer abgespielt wird, wenn
        der Wegpunkt betreten wird. Das kann ein Text sein, aber auch eine MänxFkt.
        Die Funktion kann einen Wegpunkt oder ein WegEnde zurückgeben, um
        das Wegsystem zu verlassen."""
        self.beschreibungen.append(
            Beschreibung(geschichte, nur, außer, warten))
        return self

    add_effekt = add_beschreibung
    bschr = add_beschreibung

    def wenn(self, richtung: str, fn: MänxPrädikat) -> None:
        """Erlaube eine Richtung nur, wenn die folgende Funktion wahr ist.
        Mehrere Funktionen werden verundet.
        """
        if richtung in self._wenn_fn:
            self._wenn_fn[richtung] = UndPred(self._wenn_fn[richtung], fn)
        else:
            self._wenn_fn[richtung] = fn

    def setze_zielname(self, richtung: str, ziel_name: str, ziel_kurz: str = "",
                       typ=Wegtyp.WEG):
        """Setze den Zielnamen für eine Richtung. Dieser wird"""
        ziel_kurz = ziel_kurz or ziel_name.lower()
        if not ziel_kurz or " " in ziel_kurz:
            raise ValueError(
                "Aus dem Ziel lässt sich keine sinnvolle Option machen.")
        self._optionen[Himmelsrichtung.from_kurz(richtung)] = (
            Richtungsoption(ziel_name, ziel_kurz, typ)
        )

    def beschreibe(self, mänx: Mänx, ri_name: str | Himmelsrichtung | None
                   ) -> WegEnde | Wegpunkt | None:
        """Beschreibe die Kreuzung von `richtung` kommend.

        Beschreibe muss idempotent sein, das heißt, mehrfache Aufrufe verändern
        die Welt nicht anders als ein einfacher Aufruf. Denn beim Laden wird
        die Beschreibung mehrfach durchgeführt.
        """
        for beschreibung in self.beschreibungen:
            ans = beschreibung.beschreibe(mänx, str(ri_name))
            if isinstance(ans, (Wegpunkt, WegEnde)):
                getLogger("xwatc.weg").info(
                    f"Springe aus Beschreibung von {self.name} nach {ans}.")
                return ans
            elif ans is not None:
                getLogger("xwatc.weg").warning(
                    f"Beschreibung von {self.name} hat {ans} zurückgegeben. Das wird ignoriert.")
        if ri_name and (self.kreuzung_beschreiben or not self.beschreibungen):
            from xwatc.vorlagen.kreuzung_beschreiben import beschreibe_kreuzung
            if isinstance(ri_name, Himmelsrichtung):
                beschreibe_kreuzung(self, ri_name.nr)
            else:
                beschreibe_kreuzung(self, None)
        # for mensch in self.menschen:
        #    mensch.vorstellen(mänx)
        return None

    def optionen(self, mänx: Mänx,
                 von: NachbarKey | None) -> Iterable[MenuOption[Wegpunkt | 'nsc.NSC']]:
        """Sammelt Optionen, wie der Mensch sich verhalten kann."""
        for mensch in self.menschen:
            yield (f"Mit {mensch.name} reden", mensch.name.lower(),
                   mensch)
        for pt, himri in self._richtungen(mänx, von):
            ri = self._optionen.setdefault(himri, Richtungsoption())
            if himri == von:
                if ri.zielname:
                    yield (f"Zurück ({ri.zielname})", "f", pt)
                else:
                    yield ("Umkehren", "f", pt)
            else:
                if ri.zielname:
                    yield (ri.zielname, ri.name_kurz or ri.zielname.lower(), pt)
                elif isinstance(himri, Himmelsrichtung):
                    yield (f"Nach {himri}", format(himri).lower(), pt)
                    # ziel = cap(ri.typ.text(True, 4)) + f" nach {himri}"
                else:
                    yield (himri, himri.lower(), pt)

    def _richtungen(self, mänx: Mänx, von: NachbarKey | None
                    ) -> Iterator[tuple[Wegpunkt, NachbarKey]]:
        """Liste alle möglichen Richtungen in der richtigen Reihenfolge auf.

        Zuerst kommen die Himmelsrichtungen, je gerader desto besser.
        Dann kommen die speziellen Orte.
        """
        def inner() -> Iterator[tuple[NachbarKey, Wegpunkt]]:
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
            name = str(himri_oder_name)
            if name not in self._wenn_fn or self._wenn_fn[name](mänx):
                yield richtung, himri_oder_name

    def get_nachbarn(self) -> list[Wegpunkt]:
        return [pt for pt in self.nachbarn.values()]

    def main(self, mänx: Mänx, von: Wegpunkt | None = None) -> Wegpunkt | WegEnde:
        """Fragt nach allen Richtungen."""
        from xwatc.nsc import NSC
        von_key = None
        if von is not self:
            for key, value in self.nachbarn.items():
                if value is von:
                    von_key = key
                    break
        schnell_austritt = self.beschreibe(mänx, von_key)
        if schnell_austritt is not None:
            return schnell_austritt
        opts = list(self.optionen(mänx, von_key))
        if not opts:
            raise ValueError(f"Keine Optionen, um aus {self} zu entkommen.")
        if not self.immer_fragen and ((von is None) + len(opts)) <= 2:
            if isinstance(opts[0][2], Wegpunkt):
                return opts[0][2]
        ans = mänx.menu(opts, frage="Welchen Weg nimmst du?", save=self)
        if isinstance(ans, Wegpunkt):
            return ans
        elif isinstance(ans, NSC):
            mänx_ans = ans.main(mänx)
            match mänx_ans:
                case None:  # @UnusedVariable
                    pass
                case Wegpunkt():
                    return mänx_ans
                case _ if callable(mänx_ans):
                    return WegEnde(mänx_ans)
                case _:
                    return WegEnde(mänx_ans.main)

        return self

    def __sub__(self, anderer: 'Wegkreuzung') -> 'Wegkreuzung':
        anderer.nachbarn[Himmelsrichtung.from_kurz(
            self.name)] = self
        self.nachbarn[Himmelsrichtung.from_kurz(
            anderer.name)] = anderer
        return anderer

    def verbinde(self,
                 anderer: Ausgang,
                 richtung: str,
                 ziel: str = "",
                 kurz: str = "",
                 typ: Wegtyp = Wegtyp.WEG,
                 ):
        if not richtung:
            raise ValueError("Die Richtung kann nicht leer sein.")
        anderer.verbinde(self)
        hiri = Himmelsrichtung.from_kurz(richtung)
        self.nachbarn[hiri] = anderer.wegpunkt
        self._optionen[hiri] = Richtungsoption(ziel, ziel or kurz, typ)

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

        weg = Weg(länge, None, None, **kwargs)
        assert not (self.nachbarn.get(ri1) or nach.nachbarn.get(ri2)
                    ), "Überschreibt bisherigen Weg."
        self.nachbarn[ri1] = weg
        self._optionen[ri1] = Richtungsoption(beschriftung_hin, typ=typ)
        nach.nachbarn[ri2] = weg
        self._optionen[ri2] = Richtungsoption(beschriftung_zurück, typ=typ)
        weg.p1 = self
        weg.p2 = nach

    def add_option(self, name: str, name_kurz: str,
                   effekt: Sequence[str] | BeschreibungFn) -> Self:
        """Füge eine Option an dem Wegpunkt hinzu. Beim Wählen wird dann eine Geschichte
        abgespielt."""
        # Die Option wird durch eine Wegkreuzung mit immer_fragen=False abgewickelt.
        effekt_punkt = Wegkreuzung(
            name=self.name + ":" + name_kurz,
            nachbarn={_StrAsHimmelsrichtung("zurück"): self},
            immer_fragen=False,  # Nach der Beschreibung wird umgekehrt
            gebiet=self._gebiet,
            beschreibungen=[Beschreibung(effekt)]
        )
        himri = Himmelsrichtung.from_kurz(name_kurz)
        self.nachbarn[himri] = effekt_punkt
        self._optionen[himri] = Richtungsoption(name, name_kurz)
        return self

    def add_nsc(self, welt: Welt, name: str, fkt: Callable[..., nsc.NSC],
                *args, **kwargs):
        welt.get_or_else(name, fkt, *args, **kwargs).ort = self


@define
class Gebiet:
    """Fasst mehrere Wegkreuzungen zusammen. Wegkreuzung können als Punkte auf einem Gitter
    erzeugt werden und werden dann automatisch mit ihren Nachbarn verbunden."""
    name: str
    gitterlänge: float = 5 / 64
    _punkte: list[list[Wegkreuzung | None]] = field(factory=list, repr=False)
    eintrittspunkte: dict[str, Wegpunkt] = field(factory=dict, repr=False)

    def neuer_punkt(self, koordinate: tuple[int, int], name: str, immer_fragen: bool = True
                    ) -> Wegkreuzung:
        """Erzeuge einen neuen Gitterpunkt und verbinde ihn entsprechend seiner Position."""
        return self.setze_punkt(koordinate, Wegkreuzung(
            name=name, nachbarn={}, gebiet=self, immer_fragen=immer_fragen))

    def setze_punkt(self, koordinate: tuple[int, int], pkt: Wegkreuzung) -> Wegkreuzung:
        """Setze einen Punkt auf das Gitter und verbinde ihn mit seinen Nachbarn."""
        x, y = koordinate
        if alter_pkt := self.get_punkt_at(x, y):
            raise ValueError(f"Kann keinen neuen Punkt {pkt.name} bei {x},{y} erstellen, da durch "
                             "{alter_pkt.name} besetzt.")
        pkt._gebiet = self
        self._put_punkt(x, y, pkt)
        # Verbinden
        größe_x, größe_y = self.größe
        for ri_x, ri_y, ri_name in (
            (1, 0, "o"),
            (0, 1, "s"),
            (-1, 0, "w"),
            (0, -1, "n"),
        ):
            vbind_x, vbind_y = x, y
            lg = 1
            while True:
                vbind_x += ri_x
                vbind_y += ri_y
                if vbind_x < 0 or vbind_y < 0 or vbind_x >= größe_x or vbind_y >= größe_y:
                    break
                if vbind := self.get_punkt_at(vbind_x, vbind_y):
                    self._verbind(pkt, vbind, ri_name, lg)
                    break
                lg += 1
        return pkt

    def _put_punkt(self, x: int, y: int, wegpunkt: Wegkreuzung) -> None:
        if self._punkte and y >= (ylen := len(self._punkte[0])):
            for row in self._punkte:
                row.extend(repeat(None, y - ylen + 1))
        if x >= len(self._punkte):
            self._punkte.extend([None for __ in range(y + 1)]
                                for __ in range(len(self._punkte), x + 1))
        self._punkte[x][y] = wegpunkt

    def _verbind(self, pkt1: Wegkreuzung, pkt2: Wegkreuzung, ri_name: str, länge: int) -> None:
        ri1 = Himmelsrichtung.from_kurz(ri_name)
        assert isinstance(ri1, Himmelsrichtung)
        ri2 = ri1.gegenrichtung

        weg = Weg(länge * self.gitterlänge)
        pkt1.nachbarn[ri1] = weg
        pkt2.nachbarn[ri2] = weg
        weg.p1 = pkt1
        weg.p2 = pkt2

    @property
    def größe(self) -> tuple[int, int]:
        """Die Größe des Gebiets als Tuple Breite, Länge."""
        if self._punkte:
            return len(self._punkte), len(self._punkte[0])
        return 0, 0

    def get_punkt_at(self, x: int, y: int) -> Wegkreuzung | None:
        """Gebe den Gitterpunkt an der Stelle (x|y), wenn existent, zurück."""
        if x >= 0 and y >= 0:
            try:
                return self._punkte[x][y]
            except IndexError:
                return None
        return None

    def main(self, _mänx: Mänx) -> Wegpunkt:
        """Das Gebiet als HatMain gibt einfach den Punkt namens "start" zurück."""
        return self.eintrittspunkte["start"]

    def ende(self, name: Eintritt, ziel: Eintritt | MänxFkt[Fortsetzung]
             ) -> Gebietsende | WegAdapter:
        """Erzeugt ein Ende von diesem Gebiet, dass unter dem Namen `name` von außen betreten
        werden kann.
        :param name: Ein Eintritt von **diesem** Gebiet mit einem Namen. Das soll dafür sorgen,
        dass alle Eintritte im Modul definiert werden.
        :param ziel: Ein Eintritt von einem anderen Gebiet oder aber eine MänxFkt.
        """
        match name:
            case Eintritt(name_or_gebiet=[self.name, str(port)]):
                pass
            case _:
                raise ValueError(
                    "Das erste Argument muss ein Eintritt zu diesem Gebiet sein.")
        match ziel:
            case Eintritt(name_or_gebiet=[str(nach), str(nach_port)]):
                return Gebietsende(None, self, port, nach, nach_port)
            case Eintritt(name_or_gebiet=str(nach)):
                return Gebietsende(None, self, port, nach, "start")
            case Eintritt():
                raise ValueError(
                    "Der zweite Eintritt darf kein Wegpunkt-Eintritt sein.")
            case zurück:
                return WegAdapter(zurück, port, self)


@define(init=False)
class WegAdapter(WegpunktAusgang):
    """Ein Übergang von Wegesystem zum normalen System."""
    zurück: MänxFkt
    punkt: Wegpunkt | None = None

    def __init__(self, zurück: MänxFkt,
                 name: str = "", gebiet: Gebiet | None = None) -> None:
        self.__attrs_init__(zurück)
        if gebiet and name:
            assert name not in gebiet.eintrittspunkte, f"Eintrittspunkt {name} schon in Gebiet"
            gebiet.eintrittspunkte[name] = self

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt | WegEnde:
        assert self.punkt, f"Looses Ende bei {self}"
        if von is self.punkt:
            return WegEnde(self.zurück)
        return self.punkt

    def get_nachbarn(self) -> list[Wegpunkt]:
        return [self.punkt] if self.punkt else []

    def verbinde(self, anderer: Wegpunkt) -> None:
        if not self.punkt:
            self.punkt = anderer
        else:
            getLogger("xwatc.weg").warning(f"WegAdapter sollte mit {anderer} verbunden werden, "
                                           f"ist aber schon mit {self.punkt} verbunden.")

    def __repr__(self):
        def name(pk: Wegpunkt | None):
            match pk:
                case None:  # @UnusedVariable
                    return "Leeres Ende"
                case object(name=str(ans)) if ans:  # type: ignore
                    return ans
                case _:
                    return type(pk).__name__
        return f"WegAdapter von {name(self.punkt)} nach {self.zurück}"


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

    def __init__(self, start: Ausgang | None, ende: Ausgang | None,
                 hin: MänxPrädikat | None = None,
                 zurück: MänxPrädikat | None = None):
        super().__init__(start, ende)
        self.hin = hin
        self.zurück = zurück

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt | WegEnde:
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
            getLogger("xwatc.weg").warning(
                f"{self} von unverbundenem Punkt betreten, gehe zu Punkt 1")
            return self.p1


class Gebietsende(_Strecke):
    """Das Ende eines Gebietes ist der Anfang eines anderen."""

    def __init__(self, von: Ausgang | None,
                 gebiet: Gebiet,  # pylint: disable=redefined-outer-name
                 port: str,
                 nach: str,
                 nach_port: str = ""):
        """Erzeuge ein Gebietsende.

        >>> Gebietsende(None, "jtg:mitte", "mit-gkh", "jtg:gkh")
        """
        super().__init__(von, None)
        self.gebiet = gebiet
        self.nach = nach
        self.port = port
        self.nach_port = nach_port or port
        assert self.port not in self.gebiet.eintrittspunkte, (
            f"Doppelt registrierter Port: {self.port} in {self.gebiet.name}")
        self.gebiet.eintrittspunkte[self.port] = self
        assert nach in GEBIETE, f"Unbekanntes Gebiet: {nach}"

    @property
    def von(self) -> Wegpunkt | None:
        return self.p1

    @von.setter
    def von(self, wegpunkt: Wegpunkt | None):
        self.p1 = wegpunkt

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt:
        assert self.p1, "Loses Ende"
        if von is not self.p1:
            return self.p1
        if self.p2:
            return self.p2
        else:
            try:
                self.p2 = get_eintritt(mänx, (self.nach, self.nach_port))
            except KeyError:
                raise MissingID(
                    f"Gebietsende {self.gebiet}:{self.port} ist lose.")
            else:
                return self.p2

    def __str__(self) -> str:
        return f"Gebietsende {self.gebiet.name}:{self.port} - {self.nach}:{self.nach_port}"


def get_gebiet(mänx: Mänx, name: str) -> Gebiet:
    """Hole oder erzeuge das Gebiet `name` in `mänx`."""
    if name not in GEBIETE:
        raise MissingID(f"Unbekanntes Gebiet {name}")
    return mänx.welt.get_or_else(f"weg:{name}", GEBIETE[name], mänx)


def get_eintritt(mänx: Mänx, name_or_gebiet: Wegpunkt | str | tuple[str, str]) -> Wegpunkt:
    """Lade einen Eintrittspunkt mit seiner ID.

    :param name_or_gebiet:
        Entweder
        1. ein Wegpunkt: dieser wird so zurückgegeben
        2. ein Tupel Gebiet, Port
        3. ein String Gebiet:Port
        4. ein Name eines Gebiets, dann Gebiet:"start"
    :raises MissingID: Wenn kein solcher Punkt registriert ist.
    """
    if isinstance(name_or_gebiet, (str, tuple)):
        if isinstance(name_or_gebiet, tuple):
            gebiet_name, port = name_or_gebiet
        elif name_or_gebiet in GEBIETE:
            gebiet_name = name_or_gebiet
            port = "start"
        else:
            gebiet_name, _sep, port = name_or_gebiet.rpartition(":")
        gebiet: Gebiet = get_gebiet(mänx, gebiet_name)
        if port not in gebiet.eintrittspunkte:
            raise MissingID(f"Gebiet {gebiet_name} hat keinen Eingang {port}!")
        return gebiet.eintrittspunkte[port]
        return mänx.welt.get_or_else(
            "weg:" + name_or_gebiet, GEBIETE[name_or_gebiet], mänx)
    else:
        return name_or_gebiet


@define
class Eintritt:
    """Mache eine Gebiets- oder Eintritts-ID zu einer Fortsetzung.

    Definiert ein Modul z.B.::

        MITTE = weg.Eintritt("lg:mitte")

    Dann kann eine andere Mänx-Fkt einfach::

        return MITTE

    schreiben, um eine Fortsetzung in MITTE zu erwirken.

    """
    name_or_gebiet: Wegpunkt | str | tuple[str, str]

    def __call__(self, mänx: Mänx) -> Wegpunkt:
        return get_eintritt(mänx, self.name_or_gebiet)


GebietsFn: TypeAlias = Callable[[Mänx, Gebiet], Wegpunkt | None]


def gebiet(name: str) -> Callable[[GebietsFn], MänxFkt[Gebiet]]:
    """Dekorator für Gebietserzeugungsfunktionen.

    >>>@gebiet("jtg:banane")
    >>>def erzeuge_banane(mänx: Mänx, gebiet: weg.Gebiet) -> Wegpunkt:
    >>>    ...
    """
    def wrapper(funk: GebietsFn) -> MänxFkt[Gebiet]:
        @wraps(funk)
        def wrapped(mänx: Mänx) -> Gebiet:
            gebiet = Gebiet(name)
            if start := funk(mänx, gebiet):
                gebiet.eintrittspunkte.setdefault("start", start)
            return gebiet

        GEBIETE[name] = wrapped
        return wrapped
    return wrapper


def wegsystem(mänx: Mänx, start: Wegpunkt | str | tuple[str, str], return_fn: bool = False
              ) -> MänxFkt[Fortsetzung]:
    """Startet das Wegsystem mit mänx am Wegpunkt start.

    :param return_fn: Wenn false, wird die Fortsetzung ausgeführt, bevor sie zurückgegeben wird.
    """
    wp: Wegpunkt | WegEnde = get_eintritt(mänx, start)
    last = None
    while not isinstance(wp, WegEnde):
        getLogger("xwatc.weg").info(f"Betrete {wp}")
        try:
            mänx.context = wp
            last, wp = wp, wp.main(mänx, von=last)
            mänx.welt.tick(1 / 96)
        finally:
            mänx.context = None
    ans = typing.cast(WegEnde, wp).weiter
    if not return_fn:
        ans(mänx)
    return ans


GEBIETE: dict[str, MänxFkt[Gebiet]] = {}
