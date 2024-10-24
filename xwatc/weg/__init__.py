"""
Wegpunkte für JTGs Wegesystem.

Das Wegsystem besteht aus mehreren, gegenseitig miteinander verbundenen Wegpunkten.
An diesen Punkten passieren dann die Geschichten. Üblicherweise geht der Spieler dann
zu einem benachbarten Wegpunkt.
Created on 17.10.2020
"""
from __future__ import annotations

from attrs import define, field
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from logging import getLogger
from typing import TYPE_CHECKING, Final, Literal, runtime_checkable, Protocol, TypeAlias, TypeVar
import typing
from typing_extensions import Self

from xwatc import _
from xwatc.system import Fortsetzung, Mänx, MänxFkt, MänxPrädikat, MenuOption, MissingID, MissingIDError
from itertools import repeat


if TYPE_CHECKING:
    from xwatc import nsc
    from xwatc.weg._kreuzung import Wegkreuzung
    from xwatc.weg import begegnung

__author__ = "jasper"


@dataclass(eq=False)
class WegEnde:
    """Wird vom Wegpunkt zurückgegeben und markiert, dass das
    Wegsystem hier zu Ende ist und in das alte, MänxFkt-basierte
    System übergegangen wird.
    """
    weiter: MänxFkt[Fortsetzung]

    @staticmethod
    def wrap(weiter: Fortsetzung | None) -> WegEnde | Wegpunkt | None:
        """Packe die Forsetzung in ein WegEnde, falls sie nicht schon ein Wegpunkt ist."""
        match weiter:
            case None | Wegpunkt():
                return weiter
            case _ if callable(weiter):
                return WegEnde(weiter)
            case _:
                return WegEnde(weiter.main)  # type: ignore


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


AndererAusgang = TypeVar("AndererAusgang", bound="Ausgang")


@runtime_checkable
class Ausgang(Protocol):
    """Ein Wegpunkt mit festen losen Enden. Dieses Protokoll ist beim Zusammenbauen des
    Wegenetzes wichtig: Ein Ausgang lässt sich wohldefiniert mit einem anderen Ausgang
    verbinden."""

    def verbinde(self, __anderer: Wegpunkt) -> None:
        """Verbinde diesen Wegpunkt mit anderen. Diese Methode wird vom anderen Wegpunkt
        aufgerufen, um sicherzugehen, dass der andere Wegpunkt verbunden ist."""

    @property
    def wegpunkt(self) -> Wegpunkt:
        """Der Wegpunkt, der zu einem Ausgang gehört."""

    def __sub__(self, anderer: AndererAusgang, /) -> AndererAusgang:
        """Verbindet zwei Ausgänge miteinander."""
        self.verbinde(anderer.wegpunkt)
        anderer.verbinde(self.wegpunkt)
        return anderer


class WegpunktAusgang(Wegpunkt, Ausgang):
    """Mixin für Wegpunkte, die selbst Ausgänge sind."""
    @property
    def wegpunkt(self) -> Self:
        return self


class _Strecke(WegpunktAusgang):
    """Abstrakte Basisklasse für Wegpunkte, die zwei Orte verbinden."""

    def __init__(self, start: Ausgang | None, ende: Ausgang | None = None):
        super().__init__()
        self.start = self._verbinde(start)
        self.ende = self._verbinde(ende)

    def _verbinde(self, anderer: Ausgang | None) -> Wegpunkt | None:
        """Ruft anderer.verbinde(self) auf."""
        if anderer is None:
            return anderer
        else:
            anderer.verbinde(self)
            return anderer.wegpunkt

    def get_nachbarn(self) -> list[Wegpunkt]:
        return [a for a in (self.start, self.ende) if a]

    @property
    def enden(self) -> tuple[Wegpunkt, Wegpunkt]:
        assert self.start, "Loses Ende!"
        assert self.ende, "Loses Ende!"
        return (self.start, self.ende)

    def verbinde(self, anderer: Wegpunkt) -> None:
        if not self.start:
            self.start = anderer
        elif self.start != anderer and not self.ende:
            self.ende = anderer

    def __repr__(self):
        def name(pk: Wegpunkt | None):
            match pk:
                case None:  # @UnusedVariable
                    return "Leeres Ende"
                case object(name=str(ans)) if ans:  # type: ignore
                    return ans
                case _:
                    return type(pk).__name__
        return (f"{type(self).__name__} von {name(self.start)} "
                f"nach {name(self.ende)}")


@define(kw_only=True)
class _Durchlauf:
    richtung: bool
    weg_rest: int
    will_ruhen: bool = True


class Weg(_Strecke):
    """Ein Weg hat zwei Enden und dient dazu, die Länge der Reise darzustellen.
    Zwei Menschen auf dem Weg zählen als nicht benachbart."""
    DEFAULT_FRAGE: Final[str] = _("Folgst du weiter dem Weg?")
    länge: float
    monster: 'begegnung.Monstergebiet' | None

    def __init__(self, länge: float,
                 p1: Ausgang | None = None,
                 p2: Ausgang | None = None,
                 monster: 'begegnung.Monstergebiet' | None = None):
        """
        :param länge: Länge in Stunden
        :param p1: Startpunkt
        :param p2: Endpunkt
        """
        super().__init__(p1, p2)
        self.länge = länge / 24
        self.monster = monster

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt | WegEnde:
        """Verwendet Zeit und bringt den Spieler an die gegenüberliegende Seite."""
        tagrest = mänx.welt.tag % 1.0
        if tagrest < 0.5 and tagrest + self.länge >= 0.5 and self.länge < 0.5:
            if von and mänx.ja_nein("Du wirst nicht vor Ende der Nacht ankommen. "
                                    "Willst du umkehren?"):
                return von
        if self.monster:
            self.monster.betrete(mänx)

        durchlauf = _Durchlauf(richtung=von == self.start, weg_rest=int(self.länge * 48))
        while durchlauf.weg_rest > 0:
            durchlauf.weg_rest -= 1 if mänx.welt.is_nacht() else 2
            mänx.welt.tick(1 / 24, tag_nachricht=True)
            if ans := self._stück_gelaufen(mänx, durchlauf):
                return ans
        return self.enden[durchlauf.richtung]

    def _stück_gelaufen(self, mänx: Mänx, durchlauf: _Durchlauf) -> WegEnde | Wegpunkt | None:
        """Nachdem der Mänx ein Stück gelaufen ist, kann er auf Monster treffen oder er will
        schlafen."""
        from xwatc.weg.begegnung import Flucht
        begegnung = None
        if self.monster:
            begegnung = self.monster.nächste_begegnung(mänx)
            if begegnung and begegnung.ausgang:
                if begegnung.ausgang == Flucht:
                    return self.enden[not durchlauf.richtung]
                return begegnung.ausgang
        if not begegnung and not (durchlauf.will_ruhen and mänx.welt.is_nacht()):
            # Nichts passiert, keine Nacht
            return None
        optionen: list[MenuOption[Literal["w", "f", "s"]]] = [
            ("Weiter", "w", "w"),
            ("Zurück", "f", "f")
        ]
        if mänx.welt.is_nacht():
            optionen.append(("Schlafen", "schlafen", "s"))
        aktion = mänx.menu(optionen, frage=self.DEFAULT_FRAGE)
        if aktion == "s":
            mänx.welt.nächster_tag()
            durchlauf.will_ruhen = True
        elif aktion == "f":
            mänx.welt.tick(self.länge - durchlauf.weg_rest / 48, tag_nachricht=True)
            return self.enden[not durchlauf.richtung]
        elif mänx.welt.is_nacht():
            durchlauf.will_ruhen = False
        return None


@runtime_checkable
class BenannterWegpunkt(Wegpunkt, Protocol):
    """Protokoll, dass einen Wegpunkt mit Namen darstellt."""
    @property
    def name(self) -> str: ...


def finde_punkt(mänx: Mänx, gebiet: str, name: str) -> BenannterWegpunkt:
    """Finde eine Kreuzung in einem Gebiet."""
    # Tiefensuche nach der Kreuzung mit den richtigen Namen.
    gb = get_gebiet(mänx, gebiet)
    if ans := gb.finde_punkt(name):
        return ans
    seen: set[Wegpunkt] = {*gb.eintrittspunkte.values()}
    to_check: list[Wegpunkt] = [*gb.eintrittspunkte.values()]
    while to_check:
        punkt = to_check.pop()
        match punkt:
            case Wegkreuzung(name=name2):
                gb.add_punkt(punkt)
                if name == name2:
                    return punkt
            case BenannterWegpunkt(name=name2):
                gb.add_punkt(punkt)
                if name == name2:
                    return punkt
        for next_ in punkt.get_nachbarn():
            if next_ not in seen:
                seen.add(next_)
                to_check.append(next_)
    raise MissingIDError(name)


@define
class Gebiet:
    """Fasst mehrere Wegkreuzungen zusammen. Wegkreuzung können als Punkte auf einem Gitter
    erzeugt werden und werden dann automatisch mit ihren Nachbarn verbunden."""
    name: str
    gitterlänge: float = 5 / 64
    _punkte: list[list[Wegkreuzung | None]] = field(factory=list, repr=False)
    eintrittspunkte: dict[str, Wegpunkt] = field(factory=dict, repr=False)
    _benannte: dict[str, BenannterWegpunkt] = field(factory=dict, repr=False)

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
        self.add_punkt(wegpunkt)

    def add_punkt(self, punkt: BenannterWegpunkt) -> None:
        self._benannte[punkt.name] = punkt

    def finde_punkt(self, name: str) -> BenannterWegpunkt | None:
        return self._benannte.get(name)

    def finde_kreuzung(self, name: str) -> Wegkreuzung | None:
        ans = self.finde_punkt(name)
        if isinstance(ans, Wegkreuzung):
            return ans
        return None

    def _verbind(self, pkt1: Wegkreuzung, pkt2: Wegkreuzung, ri_name: str, länge: int) -> None:
        ri1 = Himmelsrichtung.from_kurz(ri_name)
        assert isinstance(ri1, Himmelsrichtung)
        ri2 = ri1.gegenrichtung

        weg = Weg(länge * self.gitterlänge)
        pkt1.nachbarn[ri1] = weg
        pkt2.nachbarn[ri2] = weg
        weg.start = pkt1
        weg.ende = pkt2

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
        if "start" not in self.eintrittspunkte:
            raise MissingIDError(f"Gebiet {self.name} hat keinen Default-Start.")
        return self.eintrittspunkte["start"]

    def ende(self, name: Eintritt, ziel: Eintritt | MänxFkt[Fortsetzung]
             ) -> Gebietsende | WegAdapter:
        """Erzeugt ein Ende von diesem Gebiet, dass unter dem Namen `name` von außen betreten
        werden kann.
        :param name: Ein Eintritt von **diesem** Gebiet mit einem Namen. Das soll dafür sorgen,
        dass alle Eintritte im Modul definiert werden.
        :param ziel: Ein Eintritt von einem anderen Gebiet oder aber eine MänxFkt.
        """
        if name.gebiet != self.name:
            raise ValueError(
                "Das erste Argument muss ein Eintritt zu diesem Gebiet sein.")
        match ziel:
            case Eintritt(gebiet=str(nach), port=str(nach_port)):
                return Gebietsende(None, self, name.port, nach, nach_port)
            case zurück:
                return WegAdapter(zurück, name.port, self)


@define(init=False, eq=False)
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

    **Beispiel**::

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
    """

    def __init__(self, start: Ausgang | None, ende: Ausgang | None,
                 hin: MänxPrädikat | None = None,
                 zurück: MänxPrädikat | None = None):
        super().__init__(start, ende)
        self.hin = hin
        self.zurück = zurück

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt | WegEnde:
        assert self.ende
        assert self.start
        if von is self.start:
            if self.hin and self.hin(mänx):
                return self.ende
            return self.start
        elif von is self.ende:
            if self.zurück and self.zurück(mänx):
                return self.start
            return self.ende
        else:
            # Strecke einfach so betreten?
            getLogger("xwatc.weg").warning(
                f"{self} von unverbundenem Punkt betreten, gehe zu Punkt 1")
            return self.start


class Gebietsende(_Strecke):
    """Das Ende eines Gebietes ist der Anfang eines anderen."""

    def __init__(self, von: Ausgang | None,
                 gebiet: Gebiet,  # pylint: disable=redefined-outer-name
                 port: str,
                 nach: str,
                 nach_port: str = ""):
        """Erzeuge ein Gebietsende::

            gb = Gebiet("lg:mitte")
            Gebietsende(None, gb, "norden", "lg:norden", "süden");
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

    def main(self, mänx: Mänx, von: Wegpunkt | None) -> Wegpunkt:
        assert self.start, "Loses Ende"
        if von is not self.start:
            return self.start
        if self.ende:
            return self.ende
        else:
            try:
                self.ende = get_eintritt(mänx, (self.nach, self.nach_port))
            except KeyError:
                raise MissingID(
                    f"Gebietsende {self.gebiet}:{self.port} ist lose.")
            else:
                return self.ende

    def __str__(self) -> str:
        return f"Gebietsende {self.gebiet.name}:{self.port} - {self.nach}:{self.nach_port}"


def get_gebiet(mänx: Mänx, name: str) -> Gebiet:
    """Hole oder erzeuge das Gebiet `name` in `mänx`."""
    if name not in GEBIETE:
        raise MissingID(f"Unbekanntes Gebiet {name}")
    return mänx.welt.get_gebiet(mänx, name)


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
    gebiet: str
    port: str = "start"

    def __call__(self, mänx: Mänx) -> Wegpunkt:
        return get_eintritt(mänx, (self.gebiet, self.port))


BeschreibungFn = MänxFkt[None | Wegpunkt | WegEnde]
GebietsFn: TypeAlias = Callable[[Mänx, Gebiet], Wegpunkt | None]


def gebiet(name: str) -> Callable[[GebietsFn], MänxFkt[Gebiet]]:
    """Dekorator für Gebietserzeugungsfunktionen.

    >>> @gebiet("jtg:banane")
    ... def erzeuge_banane(mänx: Mänx, gebiet: weg.Gebiet) -> Wegpunkt:
    ...    ...
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
from xwatc import nsc  # @Reimport
from xwatc.weg._kreuzung import Wegkreuzung, Himmelsrichtung, kreuzung, Wegtyp, Beschreibung  # @Reimport

# def wegkreuzung_structure(_typ: type, kreuzung) -> Wegkreuzung:
#     raise NotImplementedError
#
# def wegkreuzung_unstructure(kreuzung: Wegkreuzung) -> dict:
#     assert kreuzung._gebiet
#     return {"gebiet": kreuzung._gebiet.name, "ort": kreuzung.name}
#
# converter.register_structure_hook(Wegkreuzung, wegkreuzung_structure)
# converter.register_unstructure_hook(Wegkreuzung, wegkreuzung_unstructure)
