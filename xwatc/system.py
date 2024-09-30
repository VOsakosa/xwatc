from __future__ import annotations

import enum
import logging
import types  # @UnusedImport
import typing
from collections import defaultdict
from collections.abc import Collection, Iterator, Mapping, Sequence
from logging import getLogger
from pathlib import Path
from time import sleep
from typing import (Any, List, Optional, Protocol, TypeAlias, TypeVar, Union,
                    overload)

import yaml
from attrs import define, field
from typing_extensions import Self, assert_never

from xwatc.untersystem.menus import Menu, MenuOption

try:
    from yaml import CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeDumper  # type: ignore

from xwatc import _
from xwatc.serialize import mache_converter, unstructure_punkt
from xwatc.terminal import Terminal
from xwatc.untersystem import hilfe
from xwatc.untersystem.itemverzeichnis import (ItemKlasse, Kleidungsslot, Waffenhand, Ausrüstungsort, Ausrüstungstyp,
                                               Item, lade_itemverzeichnis)
from xwatc.untersystem.person import Fähigkeit, Person, Rasse
from xwatc.untersystem.variablen import (VT, MethodSave, WeltVariable, get_welt_var)
from xwatc.untersystem.variablen import register
from xwatc.untersystem.verbrechen import Verbrechen, Verbrechensart

if typing.TYPE_CHECKING:
    from xwatc import anzeige, nsc, scenario, weg  # @UnusedImport

SPEICHER_VERZEICHNIS = Path(__file__).parent.parent / "xwatc_saves"
getLogger("xwatc").addHandler(logging.StreamHandler())


@typing.runtime_checkable
class HatMain(typing.Protocol):
    """Eine Klasse für Objekte, die Geschichte haben und daher mit main()
    ausgeführt werden können. Das können Menschen, aber auch Wegpunkte
    und Pflanzen sein."""

    def main(self, mänx: 'Mänx', /):
        """Lasse den Mänxen mit dem Objekt interagieren."""


class StoryObject(HatMain, typing.Protocol):
    """Eine Klasse für Objekte, die Geschichte haben und daher mit main()
    ausgeführt werden können. Das können Menschen, aber auch Wegpunkte
    und Pflanzen sein."""

    @classmethod
    def create(cls, welt: 'Welt', /) -> Self:
        """Erzeuge das Objekt. Dabei darf auf die Welt zugegriffen werden."""
        return cls()


M_cov = TypeVar("M_cov", covariant=True)


class MänxFkt(Protocol[M_cov]):
    """Basically a callable with Mänx as only parameter."""

    def __call__(self, __mänx: 'Mänx') -> M_cov:
        """Call this MänxFkt."""


class MissingID(KeyError):
    """Zeigt an, dass ein Objekt per ID gesucht wurde, aber nicht existiert."""


@define
class MissingIDError(Exception):
    id_: str


MänxPrädikat: TypeAlias = MänxFkt[bool]
Fortsetzung: TypeAlias = Union[MänxFkt, HatMain, 'weg.Wegpunkt']
ITEMVERZEICHNIS = lade_itemverzeichnis(Path(__file__).parent / "itemverzeichnis.yaml",
                                       Path(__file__).parent / "waffenverzeichnis.yaml")
ausgabe: Terminal | 'anzeige.XwatcFenster' = Terminal()


def get_classes(item: str) -> Iterator[str]:
    """Hole die Klassen, zu dem ein Item gehört, also z.B. "magisch", "Waffe"."""
    return (cls.name for cls in ITEMVERZEICHNIS[item].yield_classes())


def get_preise(item: str) -> int:
    """Hole den Standard-Marktpreis für ein Item. Das ist generell der Verkaufspreis,
    nicht der Ankaufpreis."""
    return ITEMVERZEICHNIS[item].get_preis()


def get_item(item_name: str) -> Item:
    """Hole die Item-Klasse von dem Namen des Items."""
    try:
        return ITEMVERZEICHNIS[item_name]
    except KeyError:
        raise KeyError(f"Unbekanntes Item {item_name}") from None


def get_item_or_dummy(item_name: str) -> Item:
    """Hole die Item-Klasse von dem Namen des Items, oder einfach eine leere neue, wenn das Item
    nicht existiert."""
    try:
        return ITEMVERZEICHNIS[item_name]
    except KeyError:
        return Item(item_name, 0, item_typ=[ItemKlasse.Unbekannt])  # type: ignore


T = TypeVar("T")
Inventar: TypeAlias = dict[str, int]
_null_func = int


# @define
# class Persönlichkeit:
#     """ Deine Persönlichkeit innerhalb des Spieles """
#     ehrlichkeit: int = 0
#     stolz: int = 0
#     arroganz: int = 0
#     vertrauenswürdigkeit: int = 0
#     hilfsbereischaft: int = 0
#     mut: int = 0

class Bekleidetheit(enum.IntEnum):
    """Stellt die Bekleidetheit eines Charakters dar. Trägt der Charakter nichts über dem Schnitt,
    ist er NACKT. Trägt er nichts über dem Oberkörper, ist er maximal OBERKöRPERFREI. Trägt er
    nichts außer Unterwäsche an Ober- oder Unterkörper, ist er IN_UNTERWÄSCHE. Ansonsten ist er
    BEKLEIDET.
    """
    NACKT = 0
    OBERKÖRPERFREI = 1
    IN_UNTERWÄSCHE = 2
    BEKLEIDET = 3


def _inventar_converter(eingabe: Mapping[str, int]) -> Inventar:
    """Konvertiert eine Eingabe in den konkreten Inventartyp."""
    return defaultdict(int, eingabe)


@define
class InventarBasis:
    """Ein Ding mit Inventar

    :var inventar: Ein dict str zu int. Da int auch 0 sein kann, sollte mit
    :py:func:`InventarBasis.items` über die items iteriert werden.
    """
    inventar: Inventar = field(factory=lambda: defaultdict(int), kw_only=True,
                               converter=_inventar_converter)
    _ausgerüstet: set[str] = field(factory=set, kw_only=True)
    # _slots: Collection[Ausrüstungsort] = field(default=set(Ausrüstungsort), kw_only=True)

    def __attrs_post_init__(self) -> None:
        self.auto_ausrüsten()

    def auto_ausrüsten(self) -> None:
        """Lasse den Mänxen alles ausrüsten, was er kann."""
        # Fixe zuerst die Ausrüstung.
        for item in list(self._ausgerüstet):
            if not self.hat_item(item):
                getLogger("xwatc.system").warning("Item %s ausgerüstet, ohne in Inventar zu sein.",
                                                  item)
            self._ausgerüstet.remove(item)
        for item in self.items():
            try:
                self.ausrüsten(item, andere_ablegen=False)
            except KeyError:
                continue
            except ValueError:
                continue

    def _blockierende_ausrüstung(self, klasse: Ausrüstungstyp) -> list[str]:
        """Finde Ausrüstung, die einen bestimmten Ausrüstungstyp blockiert."""
        geblockte_klassen = klasse.conflicting()
        if not geblockte_klassen:
            return []
        blockiert = []
        for item in self._ausgerüstet:
            item_klasse = get_item(item).ausrüstungsklasse
            if not item_klasse:
                getLogger("xwatc.system").warning(
                    "Item %s ausgerüstet, obwohl es keine Ausrüstung ist?", item)
                continue
            if item_klasse in geblockte_klassen:
                blockiert.append(item)
        return blockiert

    def ausrüsten(self, item: str, andere_ablegen: bool = True) -> None:
        """Lasse den Menschen etwas aus seinem Inventar ausrüsten. Etwaige Ausrüstung am
        selben und an sich gegenseitig ausschließenden Slots wird abgelegt.

        :param andere_ablegen: Wenn wahr (Standard) wird bei Konflikten die andere Ausrüstung
        abgelegt. Wenn falsch, wird die neue Ausrüstung nicht angelegt.

        :raises KeyError: Wenn das Item nicht bekannt ist.
        :raises ValueError: Wenn das Item keine Ausrüstung oder nicht im Inventar ist
        """
        if not self.hat_item(item):
            raise ValueError(f"Item {item} ist nicht im Inventar, kann nicht ausgerüstet werden.")
        if item in self._ausgerüstet:
            return
        klasse = get_item(item).ausrüstungsklasse
        if not klasse:
            raise ValueError(f"Item {item} kann nicht ausgerüstet werden.")
        konflikte = self._blockierende_ausrüstung(klasse)
        if andere_ablegen:
            for konflikt in konflikte:
                self._ausgerüstet.remove(konflikt)
            self._ausgerüstet.add(item)
        elif not konflikte:
            self._ausgerüstet.add(item)

    def ablegen(self, item: str) -> None:
        """Lasse den Menschen Ausrüstung zurück in sein Inventar legen."""
        self._ausgerüstet.discard(item)

    def ist_ausgerüstet(self, item: str) -> bool:
        """Prüfe, ob ein Item ausgerüstet ist."""
        return item in self._ausgerüstet

    def get_waffe(self) -> None | Item:
        """Hole die ausgerüstete Haupt-Waffe"""
        kandidat = None
        for waffe in self._ausgerüstet:
            item = get_item(waffe)
            klasse = item.ausrüstungsklasse
            if klasse in (Waffenhand.HAUPTHAND, Waffenhand.BEIDHÄNDIG):
                return item
            elif klasse == Waffenhand.NEBENHAND:
                kandidat = item
        return kandidat

    @property
    def bekleidetheit(self) -> Bekleidetheit:
        """Wie sehr gekleidet er ist. Siehe :py:class:`Bekleidetheit` für die Kriterien."""
        unten = 0
        oben = 0
        for item in self.ausrüstung:
            klasse = get_item(item).ausrüstungsklasse
            assert klasse
            if not isinstance(klasse, Kleidungsslot):
                continue
            ort = klasse.ort
            dicke = klasse.dicke
            if ort.name in ("UNTEN", "OBENUNTEN") and dicke.name not in ("FLATTERN", "ACCESSOIRE"):
                if dicke.name == "ANLIEGEND":
                    unten = max(unten, 1)
                else:
                    unten = 2
            if ort.name in ("OBEN", "OBENUNTEN") and dicke.name not in ("FLATTERN", "ACCESSOIRE"):
                if dicke.name == "ANLIEGEND":
                    oben = max(oben, 1)
                else:
                    oben = 2
        if not unten:
            return Bekleidetheit.NACKT
        if not oben:
            return Bekleidetheit.OBERKÖRPERFREI
        if unten == 2 and oben == 2:
            return Bekleidetheit.BEKLEIDET
        return Bekleidetheit.IN_UNTERWÄSCHE

    @property
    def ausrüstung(self) -> Iterator[str]:
        """Alle ausgerüsteten Items, inklusive Waffen."""
        return iter(self._ausgerüstet)

    def erhalte(self, item: str, anzahl: int = 1,
                von: Optional[InventarBasis] = None) -> None:
        """Transferiert Items in das Inventar des Mänxen und gibt das aus."""
        if von:
            anzahl = min(anzahl, von.inventar[item])
        anzahl = max(anzahl, -self.inventar[item])
        if not anzahl:
            return
        self.inventar[item] += anzahl
        if not self.inventar[item] and item in self._ausgerüstet:
            self._ausgerüstet.remove(item)
        if von:
            von.inventar[item] -= anzahl
            if not von.inventar[item] and item in von._ausgerüstet:
                von._ausgerüstet.remove(item)

    def inventar_zeigen(self) -> str:
        """Repräsentation des Inventars als Strings."""
        ans = []
        for item, anzahl in self.inventar.items():
            if anzahl:
                ans.append(f"{anzahl}x {item}")
        return ", ".join(ans)

    def erweitertes_inventar(self) -> str:
        """Repräsentation des Inventars als String, mit Preisen."""
        if not any(self.inventar.values()):
            return "Nichts da."
        ans = ["{} Gold".format(self.inventar["Gold"])]
        for item, anzahl in sorted(self.inventar.items()):
            if anzahl and item != "Gold":
                try:
                    item_obj = get_item(item)
                    kosten = get_preise(item)
                except KeyError:
                    ans.append(f"{anzahl:>4}x {item:<20} (  ?G)")
                else:
                    ans.append(f"{anzahl:>4}x {item_obj:<20} ({kosten:>3}G)")
        return "\n".join(ans)

    @property
    def gold(self) -> int:
        return self.inventar["Gold"]

    @gold.setter
    def gold(self, menge: int) -> None:
        self.inventar["Gold"] = menge

    def hat_klasse(self, *klassen: str) -> Optional[str]:
        """Prüfe, ob mänx item aus einer der Klassen besitzt."""
        for item in self.items():
            if any(c in klassen for c in get_classes(item)):
                return item
        return None

    def items(self) -> Iterator[str]:
        """Iteriert über alle besessenen Items."""
        for item, anzahl in self.inventar.items():
            if anzahl:
                yield item

    def hat_item(self, item: str, anzahl=1) -> bool:
        """Prüft, ob ein Item mit einen bestimmten Anzahl vorhanden ist."""
        return item in self.inventar and self.inventar[item] >= anzahl


@define
class Welt:
    """Speichert den Zustand der Welt, in der sich der Hauptcharakter befindet."""
    tag: float = 0.
    _objekte: dict[str, Any] = field(factory=dict, repr=False)
    _flaggen: set[str] = field(factory=set, repr=False)
    _gebiete: dict[str, weg.Gebiet] = field(factory=dict, repr=False)

    @classmethod
    def default(cls) -> Self:
        """Erzeuge eine leere Standardwelt"""
        return cls()

    def setze(self, name: str) -> None:
        """Setze eine Welt-Variable"""
        self._flaggen.add(name)

    def ist(self, name: str) -> bool:
        """Testet eine Welt-Variable."""
        return name in self._flaggen

    # TODO: Durch Story-Char ersetzen.
    def am_leben(self, name: str) -> bool:
        """Prüfe, ob das Objekt *name* da und noch am Leben ist."""
        try:
            obj = self.obj(name)
        except KeyError:
            return False
        else:
            return not getattr(obj, 'tot', False)

    def hat_obj(self, name: type[Any] | WeltVariable[Any] | nsc.StoryChar) -> bool:
        """Teste, ob ein Objekt bereits erzeugt wurde."""
        match name:
            case str(name_str):
                welt_var = get_welt_var(name_str)  # @UnusedVariable
            case type():
                welt_var = getattr(name, "_variable")
                assert welt_var
                name_str = welt_var.name
            case WeltVariable(name=name_str):
                pass
            case nsc.StoryChar(id_=str(name_str)):
                pass
        return name_str in self._objekte

    @overload
    def obj(self, name: WeltVariable[VT]) -> VT: ...  # @UnusedVariable

    @overload
    def obj(self, name: type[VT]) -> VT: ...  # @UnusedVariable

    @overload
    def obj(self, name: nsc.StoryChar) -> nsc.NSC: ...

    @overload
    def obj(self, name: str) -> Any: ...  # @UnusedVariable

    def obj(self, name: str | WeltVariable[Any] | type[Any] | nsc.StoryChar) -> Any:
        """Hole ein registriertes oder existentes Objekt.

        :raise MissingID: Wenn das Objekt nicht existiert und nicht registriert ist.
        """
        from xwatc import nsc  # @Reimport
        match name:
            case str(name_str):
                welt_var = get_welt_var(name_str)  # @UnusedVariable
            case type():
                welt_var = getattr(name, "_variable")
                assert welt_var
                name_str = welt_var.name
            case WeltVariable(name=name_str):
                welt_var = name
            case nsc.StoryChar(id_=str(name_str)):
                welt_var = None
        if name_str in self._objekte:
            return self._objekte[name_str]
        obj: HatMain
        if welt_var:
            obj = welt_var.erzeuger(self)
        elif name_str in nsc.CHAR_REGISTER:
            obj = nsc.CHAR_REGISTER[name_str].zu_nsc()
        else:
            raise MissingID(f"Das Objekt {name} existiert nicht.")
        self._objekte[name_str] = obj
        return obj

    def setze_var(self, var: WeltVariable[VT], wert: VT) -> None:
        self._objekte[var.name] = wert

    def setze_objekt(self, name: str, objekt: object) -> None:
        """Setze ein Objekt in der Welt."""
        self._objekte[name] = objekt

    def get_gebiet(self, mänx: Mänx, name: str) -> weg.Gebiet:
        if name not in self._gebiete:
            self._gebiete[name] = weg.GEBIETE[name](mänx)
        return self._gebiete[name]

    def nächster_tag(self, tage: int = 1):
        """Springe zum nächsten Tag"""
        self.tag = int(self.tag + tage)

    def get_tag(self) -> int:
        """Gebe den Tag seit Anfang des Spiels aus. Der erste Tag ist 0."""
        return int(self.tag)

    def is_nacht(self) -> bool:
        """Prüfe, ob Nacht ist. Die Welt startet standardmäßig am Morgen und die Hälfte des Tages
        ist Nacht."""
        return self.tag % 1.0 >= 0.5

    def tick(self, uhr: float):
        """Lasse etwas Zeit in der Welt vergehen."""
        if uhr < 0:
            raise ValueError(
                "Mit tick kann die Uhr nicht zurückbewegt werden.")
        self.tag += uhr

    def uhrzeit(self) -> tuple[int, int]:
        """Gebe die momentane Uhrzeit als Tupel (Stunde, Minute) aus."""
        stunde, rest = divmod(30 + (self.tag % 1.) * 24, 1.)
        minute = (rest * 60) % 1.
        return int(stunde) % 24, int(minute)


@define
class Mänx(InventarBasis):
    """Der Hauptcharakter des Spiels, alles dreht sich um ihn, er hält alle
    Information."""
    ausgabe: 'Terminal | anzeige.XwatcFenster' = ausgabe
    welt: Welt = field(factory=Welt.default)
    person: Person = Person("w", Rasse.Mensch)
    titel: set[str] = field(factory=set, repr=False)
    fähigkeiten: set[Fähigkeit] = field(factory=set, repr=False)
    verbrechen: list[Verbrechen] = field(factory=list)
    gefährten: list[nsc.NSC] = field(factory=list, repr=False)
    context: Any | None = None
    # Speicherpunkt signalisiert, dass der Mänx gerade geladen wird.
    _geladen_von: Fortsetzung | None = None
    speicherdatei_name: str | None = None

    def __attrs_post_init__(self) -> None:
        # Ruft super().__attrs_post_init__ nicht auf.
        if not self.inventar:
            self.gebe_startinventar()
        else:
            self.auto_ausrüsten()

    def hat_fähigkeit(self, name: Fähigkeit) -> bool:
        return name in self.fähigkeiten

    def gebe_startinventar(self):
        self.inventar["Gold"] = 33
        self.inventar["Mantel"] = 1
        self.inventar["Unterhose"] = 1
        self.inventar["Hose"] = 1
        self.inventar["T-Shirt"] = 1
        self.inventar["Gürtel"] = 1
        self.inventar["Socke"] = 2
        self.inventar["Turnschuh"] = 2
        self.inventar["Mütze"] = 1
        if self.person.geschlecht.name == "Weiblich":
            self.inventar["BH"] = 1
        self.auto_ausrüsten()

    def inventar_leeren(self) -> None:
        """Töte den Menschen, leere sein Inventar und entlasse
        seine Gefährten."""
        self.inventar.clear()
        self._ausgerüstet.clear()
        # self.titel.clear()
        self.gefährten.clear()
        self.gebe_startinventar()

    def get_kampfkraft(self) -> int:
        # TODO: add Fähigkeiten der Waffen
        # if any(get_class(it) == "magische Waffe" for it in self.items()):
        #     return 2000
        # if any(get_class(it) == "Waffe" for it in self.items()):
        #     return 1000
        return 20

    def erhalte(self, item: str, anzahl: int = 1,
                von: Optional[InventarBasis] = None):
        """Transferiert Items in das Inventar des Mänxen und gibt das aus."""
        if von:
            anzahl = min(anzahl, von.inventar[item])
        anzahl = max(anzahl, -self.inventar[item])
        if not anzahl:
            return
        if anzahl > 0:
            malp(f"Du erhältst {anzahl} {item}.")
        elif item == "Gold":
            malp(f"Du zahlst {-anzahl} Gold")
        else:
            malp(f"Du gibst {-anzahl} {item}.")
        self.inventar[item] += anzahl
        if not self.inventar[item] and item in self._ausgerüstet:
            self._ausgerüstet.remove(item)
        if von:
            von.inventar[item] -= anzahl
            if not von.inventar[item] and item in von._ausgerüstet:
                von._ausgerüstet.remove(item)

    def minput(self, frage: str, möglichkeiten: Sequence[str] | None = None, lower: bool = True,
               save: 'Speicherpunkt | None' = None) -> str:
        """Fragt den Benutzer nach einer Eingabe."""
        self._reset_laden(save)
        if möglichkeiten:
            return self.ausgabe.menu(self, Menu.minput(möglichkeiten, frage), save)
        else:
            return self.ausgabe.minput(self, frage=frage, lower=lower, save=save)

    def ja_nein(self, frage: str, save: 'Speicherpunkt | None' = None) -> bool:
        """Fragt den Benutzer eine Ja-Nein-Frage."""
        self._reset_laden(save)
        return self.ausgabe.menu(self, Menu.ja_nein_bool(frage), save)

    def menu(self,
             optionen: List[MenuOption[T]],
             frage: str = "",
             versteckt: Mapping[str, T] | None = None,
             save: 'Speicherpunkt | None' = None) -> T:
        """Lasse den Spieler aus verschiedenen Optionen wählen.

        z.B:

        >>> Mänx().menu([("Nach Hause gehen", "hause", 1), ("Weitergehen", "weiter", 12)])

        erlaubt Eingaben 1, hau, hause für "Nach Hause gehen" auf dem Terminal.
        Auf der Anzeige wird ein Knopf "Nach Hause gehen" und einer "Weitergehen" gezeigt, die
        kurzen Bezeichnungen tauchen nicht auf.
        """
        self._reset_laden(save)
        return self.ausgabe.menu(self, Menu(optionen, frage, versteckt or {}), save)

    def genauer(self, text: Sequence[str]) -> None:
        """Frage nach, ob der Spieler etwas genauer erfahren will.
        Es kann sich um viel Text handeln."""
        if self.ausgabe.terminal:
            t = self.minput("Genauer? (Schreibe irgendwas für ja)")
            if t and t not in ("nein", "n"):
                for block in text:
                    self.ausgabe.malp(block)
        else:
            if self.menu([("Genauer", "", True), ("Weiter", "", False)]):
                self.ausgabe.malp("\n".join(text))

    def sleep(self, länge: float, pausenzeichen: str = ".", stunden: float | None = None):
        """Lasse den Spieler warten und zeige nur in regelmäßigen Abständen Pausenzeichen."""
        for _i in range(int(länge / 0.5)):
            if self.ausgabe.terminal:
                print(pausenzeichen, end="", flush=True)
            else:
                malp(pausenzeichen, end="")
            sleep(0.5)
        if stunden is None:
            stunden = länge
        self.welt.tick(stunden / 24)
        malp()

    def tutorial(self, art: str) -> None:
        """Spielt das Tutorial für ein Spielsystem ab. Diese sind unter hilfe.HILFEN."""
        if not self.welt.ist("tutorial:" + art):
            for zeile in hilfe.HILFEN[art]:
                malp(zeile)
            self.welt.setze("tutorial:" + art)

    def inventar_zugriff(self, inv: InventarBasis, nimmt: bool | Sequence[str] = False) -> None:
        """Ein Menu, um auf ein anderes Inventar zuzugreifen."""
        # TODO Inventar-Zugriff in ein Untersystem.
        malp(inv.erweitertes_inventar())
        self.tutorial("inventar_zugriff")
        while True:
            a = self.minput(">", lower=False)
            if a == "z" or a == "zurück" or a == "f":
                return
            co, _, rest = a.partition(" ")
            args = rest.split()
            # TODO Items mit Leerzeichen
            if co == "n" or co == "nehmen":
                if not args or args == ["*"]:
                    schiebe_inventar(inv.inventar, self.inventar)
                    return
                elif len(args) == 1:
                    ding = args[0]
                    if inv.hat_item(ding):
                        self.erhalte(ding, inv.inventar[ding], inv)
                    else:
                        malp(f"Kein {ding} da.")
                elif len(args) == 2:
                    ding = args[1]
                    try:
                        anzahl = int(args[0])
                        assert anzahl > 0
                    except (AssertionError, ValueError):
                        malp("Gebe eine positive Anzahl an.")
                    else:
                        if inv.hat_item(ding, anzahl):
                            self.erhalte(ding, anzahl, inv)
                        else:
                            malp(f"Kein {ding} da.")
            elif co == "a" or co == "auslage":
                malp(inv.erweitertes_inventar())
            elif co == "g" or co == "geben":
                if not nimmt:
                    malp("Du kannst hier nichts hereingeben")
                elif len(args) == 1:
                    ding = args[0]
                    if self.hat_item(ding):
                        inv.inventar[ding] = self.inventar[ding]
                        self.inventar[ding] = 0
                    else:
                        malp(f"Du hast kein {ding}.")
                elif len(args) == 2:
                    ding = args[1]
                    try:
                        anzahl = int(args[0])
                        assert anzahl > 0
                    except (AssertionError, ValueError):
                        malp("Gebe eine positive Anzahl an.")
                    else:
                        if self.hat_item(ding, anzahl):
                            self.inventar[ding] -= anzahl
                            inv.inventar[ding] += anzahl
                        else:
                            malp(f"Du hast kein {ding}.")
            if not any(inv.items()):
                return

    def add_gefährte(self, gefährte: 'nsc.NSC'):
        self.gefährten.append(gefährte)

    def rede_mit_gefährten(self) -> None:
        """Unterbrechung, in der der Mänx mit seinen Gefährten redet."""
        opts: list[MenuOption[nsc.NSC | None]] = [
            (f"Mit {g.name} reden", g.bezeichnung.kurz_name.lower(), g) for g in self.gefährten]
        if not opts:
            malp("Du hast noch keine Gefährten.")
        opts.append(("zurück", "f", None))
        if gefährte := self.menu(opts):
            gefährte.main(self)

    @property
    def rasse(self) -> Rasse:
        """Die Rasse des Mänxen."""
        return self.person.rasse

    def add_verbrechen(self, name: Verbrechen | Verbrechensart, versuch: bool = False) -> None:
        """Laste dem Mänxen ein Verbrechen an."""
        if isinstance(name, Verbrechen):
            verbrechen = name
        elif isinstance(name, Verbrechensart):
            verbrechen = Verbrechen(name, versuch)
        else:
            raise TypeError("name muss Verbrechen, VerbrechenArt oder Name "
                            "des Verbrechens sein.")
        self.verbrechen.append(verbrechen)

    @property
    def am_laden(self) -> bool:
        return self._geladen_von is not None

    def _reset_laden(self, save: 'Speicherpunkt | None') -> None:
        """Beende den Lade-Modus. Prüfe möglichst noch, ob man auch an der selben Stelle
        landet und gebe sonst eine Warnung aus."""
        warn = getLogger("xwatc.system").warn
        if self._geladen_von is not None:
            if self._geladen_von != save:
                warn(f"Load from {self._geladen_von} first asked for {save}.")

            self._geladen_von = None

    def save(self, punkt: 'Speicherpunkt', name: Path | str | None = None) -> None:
        """Speicher den Mänxen."""
        # self._geladen_von = punkt
        if name is None:
            name = self.speicherdatei_name or "welt"
        if isinstance(name, str):
            self.speicherdatei_name = name
            SPEICHER_VERZEICHNIS.mkdir(exist_ok=True, parents=True)
            if not self.speicherdatei_name:
                self.speicherdatei_name = "welt"
            if name:
                self.speicherdatei_name = name
            filename = self.speicherdatei_name + ".yaml"
            path = SPEICHER_VERZEICHNIS / filename
        elif isinstance(name, Path):
            path = name
        else:
            assert_never(name)

        dict_ = mache_converter().unstructure(self, Mänx)
        dict_["punkt"] = unstructure_punkt(punkt)
        try:

            with open(path, "w", encoding="utf8") as write:
                yaml.dump(dict_, stream=write, Dumper=SafeDumper, allow_unicode=True)
        except Exception:
            try:
                path.unlink()
            except OSError:
                pass
            raise
        # self._geladen_von = None

    @classmethod
    def load_from_file(cls, path: Path | str) -> tuple[Self, Fortsetzung]:
        """Lade einen Spielstand aus der Datei."""
        if isinstance(path, str):
            path = SPEICHER_VERZEICHNIS / path
        with open(path, "r", encoding="utf8") as file:
            dict_ = yaml.safe_load(file)
            ans = mache_converter().structure(dict_, cls)
            assert ans._geladen_von
            ans.ausgabe = ausgabe
            ans.speicherdatei_name = path.stem
            return ans, ans._geladen_von


def schiebe_inventar(start: Inventar, ziel: Inventar) -> None:
    """Schiebe alles aus start in ziel"""
    for item, anzahl in start.items():
        ziel[item] += anzahl
    start.clear()


# EIN- und AUSGABE

minput = Mänx.minput
ja_nein = Mänx.ja_nein


def mint(*text) -> None:
    """Printe und warte auf ein Enter."""
    if len(text) == 1:
        text = _(text[0]),
    ausgabe.mint(*text)


def sprich(sprecher: str, text: str, warte: bool = False, wie: str = "") -> None:
    ausgabe.sprich(sprecher, text, warte, wie)


def malp(*text, sep=" ", end='\n', warte=False) -> None:
    """Angenehm zu lesender, langsamer Print."""
    if len(text) == 1:
        text = _(text[0]),
    ausgabe.malp(*text, sep=sep, end=end, warte=warte)


def malpw(*text, sep=" ", end='\n') -> None:
    ausgabe.malp(*text, sep=sep, end=end, warte=True)


def kursiv(text: str) -> str:
    """Packt text so, dass es kursiv ausgedruckt wird."""
    return ausgabe.kursiv(text)


class Spielende(Exception):
    """Diese Exception wird geschmissen, um das Spiel zu beenden."""


class ZumHauptmenu(Exception):
    """Diese Exception wird geschmissen, um direkt zum Hauptmenü zu gelangen.
    Sie sollte nur von den Ausgaben geschmissen werden, damit der Spieler je nach Regel
    vorher noch abgespeichert wird.
    """


def main_loop(mänx: Mänx, punkt: Fortsetzung | None = None) -> None:
    """Die Hauptschleife von Xwatc (im Spiel, das Hauptmenü ist in den Anzeigen.)"""
    from xwatc.lg.start import respawn, waffe_wählen
    mänx._geladen_von = punkt
    if punkt is None:
        malp(_("Willkommen bei Xwatc"))
        punkt = waffe_wählen
    while True:
        try:
            while punkt:
                getLogger("xwatc").info(f"Betrete {punkt}.")
                if isinstance(punkt, weg.Wegpunkt):
                    punkt = weg.wegsystem(mänx, punkt, return_fn=True)
                elif callable(punkt):
                    punkt = punkt(mänx)
                elif isinstance(punkt, HatMain):
                    punkt = punkt.main(mänx)
                else:
                    assert_never(punkt)
        except Spielende:
            malp(_("Du bist tot"))
            if mänx.titel:
                malp("Du hast folgende Titel erhalten:", ", ".join(mänx.titel))
                malp("Aber keine Sorge, du wirst wiedergeboren")
            punkt = respawn
        except (EOFError, ZumHauptmenu):
            return
        else:
            malp("Hier ist die Geschichte zu Ende.")
            punkt = respawn


from xwatc import anzeige, nsc, scenario, weg  # @UnusedImport @Reimport

Speicherpunkt: TypeAlias = (MänxFkt[Fortsetzung] | nsc.NSC
                            | weg.Wegkreuzung | scenario.ScenarioWegpunkt | MethodSave)
if __debug__:
    from typing import get_type_hints
    get_type_hints(Mänx)
