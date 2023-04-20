"""
Enthält die Wegkreuzung, der zentrale Punkt des Wegsystems, an dem die meisten Dinge passieren.
"""
from __future__ import annotations

from attrs import define, field
from collections.abc import Collection, Iterable, Iterator, Sequence
import enum
from logging import getLogger
from typing import (ClassVar, NewType, TYPE_CHECKING)
from typing_extensions import Self

from xwatc import _
from xwatc.system import (Mänx, MenuOption, MänxFkt, malp, mint,
                          MänxPrädikat, Welt)
from xwatc.utils import uartikel, bartikel, adj_endung, UndPred
from xwatc.weg import Ausgang, Wegpunkt, WegEnde, Weg, Gebiet
from xwatc.weg import dorf


if TYPE_CHECKING:
    from xwatc import nsc
__author__ = "jasper"


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


@define(frozen=True)
class _KreuzungsAusgang(Ausgang):
    """Ein Ausgang für Kreuzungen."""
    kreuzung: Wegkreuzung
    richtung: NachbarKey
    option: Richtungsoption

    def verbinde(self, anderer: Wegpunkt, /):
        self.kreuzung.nachbarn[self.richtung] = anderer
        self.kreuzung._optionen[self.richtung] = self.option

    def __lt__(self, anderer: Ausgang):
        """Verbindet in eine Richtung mit dem anderen, aber als Sackgasse."""
        self.kreuzung.nachbarn[self.richtung] = anderer.wegpunkt
        self.kreuzung._optionen[self.richtung] = self.option
        self.kreuzung._wenn_fn[str(self.richtung)] = lambda *__: False
        anderer.verbinde(self.kreuzung)

    @property
    def wegpunkt(self) -> Wegpunkt:
        return self.kreuzung


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
                      immer_fragen=immer_fragen)
    if gucken:
        ans.add_option("Umschauen", "gucken", gucken)
    for ausgang in kwargs.values():
        ausgang.verbinde(ans)
    return ans


@define(eq=True)
class NSCReference:
    """Referenz auf einen NSC per Template-Name und Nummer."""
    template: str
    idx: int = 0

    @classmethod
    def from_nsc(cls, nsc_: nsc.NSC) -> Self:
        assert nsc_.template.id_, "NSC-Template hat keine ID."
        return cls(nsc_.template.id_, nsc_.nr)


@define(eq=False)
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
    _menschen: list[NSCReference] = field(factory=list, repr=False)
    immer_fragen: bool = True
    kreuzung_beschreiben: bool = False
    _gebiet: 'Gebiet | None' = None
    dorf: dorf.Dorf | None = None
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

    def ausgang(self, richtung: str, ziel_name: str, ziel_kurz: str = "",
                typ=Wegtyp.WEG) -> _KreuzungsAusgang:
        """Erzeuge ein Ausgangs-Objekt, um diesen Wegpunkt verbinden zu können.

        >>> a = kreuzung("a")
        >>> a.ausgang("nachb") - kreuzung("b").ausgang("nacha");
        >>> len(a.get_nachbarn())
        1
        """
        return _KreuzungsAusgang(
            self,
            Himmelsrichtung.from_kurz(richtung),
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
        if ri_name and (self.kreuzung_beschreiben or not self.beschreibungen and self.immer_fragen):
            from xwatc.vorlagen.kreuzung_beschreiben import beschreibe_kreuzung
            if isinstance(ri_name, Himmelsrichtung):
                beschreibe_kreuzung(self, ri_name.nr)
            else:
                beschreibe_kreuzung(self, None)
        # for mensch in self.menschen:
        #    mensch.ansehen(mänx)
        return None

    def optionen(self, mänx: Mänx,
                 von: NachbarKey | None) -> Iterable[MenuOption[Wegpunkt | 'nsc.NSC']]:
        """Sammelt Optionen, wie der Mensch sich verhalten kann."""
        for mensch in self.get_nscs(mänx.welt):
            yield (_("Mit {name} reden").format(name=mensch.name),
                   mensch.bezeichnung.kurz_name.lower(),
                   mensch)
        for pt, himri in self._richtungen(mänx, von):
            ri = self._optionen.setdefault(himri, Richtungsoption())
            if himri == von and isinstance(himri, Himmelsrichtung):
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
        # Direkt wählen, wenn nicht immer_fragen an.
        if not self.immer_fragen and ((von is None) + len(opts)) <= 2:
            if isinstance(opts[0][2], Wegpunkt):
                return opts[0][2]
        frage = _("Welchen Weg nimmst du?") if mänx.ausgabe.terminal else ""
        ans = mänx.menu(opts, frage=frage, save=self)
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
        """Verbinde Wegkreuzungen anhand ihres Namens."""
        anderer.nachbarn[Himmelsrichtung.from_kurz(self.name)] = self
        self.nachbarn[Himmelsrichtung.from_kurz(anderer.name)] = anderer
        return anderer

    def verbinde(
        self, anderer: Ausgang, richtung: str, ziel: str = "",
        kurz: str = "", typ: Wegtyp = Wegtyp.WEG,
    ):
        """Verbinde einen Ausgang.

        `kreuzung.verbinde(ausgang, *args)` ist äquivalent zu `kreuzung.ausgang(*args) - ausgang`.
        """
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
        nach._optionen[ri2] = Richtungsoption(beschriftung_zurück, typ=typ)
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

    def get_nscs(self, welt: Welt) -> Iterable[nsc.NSC]:
        """Gibt einen Iterator über die NSCs an diesem Ort."""
        for ref in self._menschen:
            nscs: Sequence[nsc.NSC] | nsc.NSC = welt.obj(ref.template)
            if isinstance(nscs, Sequence):
                yield nscs[ref.idx]
            else:
                yield nscs

    def add_nsc(self, nsc: nsc.NSC) -> None:
        """Fügt den NSC hinzu. Wird auch beim Setzen vom NSC-Ort aufgerufen."""
        if nsc.ort is not self:
            nsc.ort = self  # Will call this function again
            return
        ref = NSCReference.from_nsc(nsc)
        if ref not in self._menschen:
            self._menschen.append(ref)

    def remove_nsc(self, nsc: nsc.NSC) -> None:
        """Entfernt den NSC."""
        if nsc.ort is self:
            nsc.ort = None  # Will call this function again
            return
        self._menschen.remove(NSCReference.from_nsc(nsc))

    def add_char(self, welt: Welt, char: nsc.StoryChar) -> nsc.NSC:
        """Füge einen Story-Charakter zu diesem Ort hinzu."""
        if not char.id_:
            raise ValueError(
                "Der Charakter für add_char muss eine ID besitzen.")
        nsc = welt.obj(char.id_)
        nsc.ort = self
        return nsc

    @property
    def gebiet(self) -> Gebiet:
        if self._gebiet:
            return self._gebiet
        # Tiefensuche nach Gebiet
        seen: set[Wegpunkt] = {self}
        to_check: list[Wegpunkt] = [self]
        while to_check:
            punkt = to_check.pop()
            match punkt:
                case Wegkreuzung(_gebiet=Gebiet() as ans):
                    self._gebiet = ans
                    return ans
            for next_ in punkt.get_nachbarn():
                if next_ not in seen:
                    seen.add(next_)
                    to_check.append(next_)
        raise ValueError("Diese Kreuzung gehört zu keinem Gebiet.")
 
    def __str__(self) -> str:
        try:
            return f"{self.gebiet.name}:{self.name}"
        except ValueError:
            return f"?:{self.name}"
    
