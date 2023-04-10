from __future__ import annotations

from attrs import define, field
from collections import defaultdict
from collections.abc import Sequence, Callable, Iterator, Mapping
from logging import getLogger
import logging
from pathlib import Path
from time import sleep
from typing import TypeVar, Any, Protocol
from typing import (Dict, List, Union, Optional, Optional as Opt, TypeAlias)
from typing_extensions import Self, assert_never
import typing
import yaml
try:
    from yaml import CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeDumper

from xwatc import _
from xwatc.serialize import mache_converter
from xwatc.terminal import Terminal
from xwatc.untersystem import hilfe
from xwatc.untersystem.itemverzeichnis import lade_itemverzeichnis, Item
from xwatc.untersystem.verbrechen import Verbrechen, Verbrechensart
from xwatc.untersystem.person import Rasse, Fähigkeit

if typing.TYPE_CHECKING:
    from xwatc import dorf  # @UnusedImport
    from xwatc import anzeige  # @UnusedImport
    from xwatc import weg  # @UnusedImport
    from xwatc import nsc  # @UnusedImport

SPEICHER_VERZEICHNIS = Path(__file__).parent.parent / "xwatc_saves"
getLogger("xwatc").addHandler(logging.StreamHandler())


class HatMain(typing.Protocol):
    """Eine Klasse für Objekte, die Geschichte haben und daher mit main()
    ausgeführt werden können. Das können Menschen, aber auch Wegpunkte
    und Pflanzen sein."""

    def main(self, mänx: 'Mänx'):
        """Lasse den Mänxen mit dem Objekt interagieren."""


M_cov = TypeVar("M_cov", covariant=True)


class MänxFkt(Protocol[M_cov]):
    """Basically a callable with Mänx as only parameter."""

    def __call__(self, __mänx: 'Mänx') -> M_cov:
        """Call this MänxFkt."""


class MissingID(KeyError):
    """Zeigt an, dass ein Objekt per ID gesucht wurde, aber nicht existiert."""


Speicherpunkt = HatMain | MänxFkt
MänxPrädikat = MänxFkt[bool]
Fortsetzung = Union[MänxFkt, HatMain, 'weg.Wegpunkt']
ITEMVERZEICHNIS = lade_itemverzeichnis(Path(__file__).parent / "itemverzeichnis.txt",
                                       Path(__file__).parent / "waffenverzeichnis.yaml")

_OBJEKT_REGISTER: Dict[str, Callable[[], 'HatMain']] = {}
ausgabe: Terminal | 'anzeige.XwatcFenster' = Terminal()


def get_classes(item: str) -> Iterator[str]:
    """Hole die Klassen, zu dem ein Item gehört, also z.B. "magisch", "Waffe"."""
    return map(str, ITEMVERZEICHNIS[item].yield_classes())


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


T = TypeVar("T")
Tcov = TypeVar("Tcov", covariant=True)
MenuOption: TypeAlias = tuple[str, str, Tcov]
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

def _inventar_converter(eingabe: Mapping[str, int]) -> Inventar:
    """Konvertiert eine Eingabe in den konkreten Inventartyp."""
    return defaultdict(int, eingabe)


@define
class InventarBasis:
    """Ein Ding mit Inventar"""
    inventar: Inventar = field(factory=lambda: defaultdict(int), kw_only=True,
                               converter=_inventar_converter)

    def erhalte(self, item: str, anzahl: int = 1,
                von: Optional[InventarBasis] = None) -> None:
        """Transferiert Items in das Inventar des Mänxen und gibt das aus."""
        if von:
            anzahl = min(anzahl, von.inventar[item])
        anzahl = max(anzahl, -self.inventar[item])
        if not anzahl:
            return
        self.inventar[item] += anzahl
        if von:
            von.inventar[item] -= anzahl

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
                item_obj = get_item(item)
                kosten = get_preise(item)
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
    name: str
    tag: float = 0.
    _objekte: dict[str, Any] = field(factory=dict, repr=False)
    _flaggen: set[str] = field(factory=set, repr=False)

    @classmethod
    def default(cls) -> Self:
        """Erzeuge eine leere Standardwelt, die aus historischen Gründen bliblablux heißt."""
        return cls(name="Bliblablux")

    def setze(self, name: str) -> None:
        """Setze eine Welt-Variable"""
        self._flaggen.add(name)

    def ist(self, name: str) -> bool:
        """Testet eine Welt-Variable."""
        return name in self._flaggen

    def get_or_else(self, name: str, fkt: Callable[..., T], *args,
                    **kwargs) -> T:
        """Hole ein Objekt aus dem Speicher oder erzeuge ist mit *fkt*"""
        if name in self._objekte:
            ans = self._objekte[name]
            if isinstance(fkt, type):
                assert isinstance(ans, fkt)
            return ans
        else:
            ans = fkt(*args, **kwargs)
            self._objekte[name] = ans
            return ans

    def am_leben(self, name: str) -> bool:
        """Prüfe, ob das Objekt *name* da und noch am Leben ist."""
        try:
            obj = self.obj(name)
        except KeyError:
            return False
        else:
            return not getattr(obj, 'tot', False)

    def obj(self, name: str | Besuche) -> Any:
        """Hole ein registriertes oder existentes Objekt.

        :raise MissingID: Wenn das Objekt nicht existiert und nicht registriert ist.
        """
        if isinstance(name, Besuche):
            name = name.objekt_name
        if name in self._objekte:
            return self._objekte[name]
        from xwatc import nsc  # @Reimport
        obj: HatMain
        if name in nsc.CHAR_REGISTER:
            obj = nsc.CHAR_REGISTER[name].zu_nsc()
        elif name in _OBJEKT_REGISTER:
            obj = _OBJEKT_REGISTER[name]()
        else:
            raise MissingID(f"Das Objekt {name} existiert nicht.")
        self._objekte[name] = obj
        return obj

    def setze_objekt(self, name: str, objekt: object) -> None:
        """Setze ein Objekt in der Welt."""
        self._objekte[name] = objekt

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
    rasse: Rasse = Rasse.Mensch
    titel: set[str] = field(factory=set, repr=False)
    fähigkeiten: set[Fähigkeit] = field(factory=set, repr=False)
    verbrechen: defaultdict[Verbrechen, int] = field(
        factory=lambda: defaultdict(int))
    gefährten: list[nsc.NSC] = field(factory=list, repr=False)
    context: Any | None = None
    # Speicherpunkt signalisiert, dass der Mänx gerade geladen wird.
    _geladen_von: Fortsetzung | None = None
    speicherdatei_name: str | None = None

    def __attrs_pre_init__(self) -> None:
        super().__init__()

    def __attrs_post_init__(self) -> None:
        self.gebe_startinventar()

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

    def inventar_leeren(self) -> None:
        """Töte den Menschen, leere sein Inventar und entlasse
        seine Gefährten."""
        self.inventar.clear()
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
        if von:
            von.inventar[item] -= anzahl

    def minput(self, frage: str, möglichkeiten: Sequence[str] | None = None, lower: bool = True,
               save: Speicherpunkt | None = None) -> str:
        """Fragt den Benutzer nach einer Eingabe."""
        self._reset_laden(save)
        return self.ausgabe.minput(
            self, frage=frage, möglichkeiten=möglichkeiten,
            lower=lower, save=save)

    def ja_nein(self, frage: str, save: Speicherpunkt | None = None) -> bool:
        """Fragt den Benutzer eine Ja-Nein-Frage."""
        self._reset_laden(save)
        return self.ausgabe.ja_nein(self, frage=frage, save=save)

    def menu(self,
             optionen: List[MenuOption[T]],
             frage: str = "",
             versteckt: Mapping[str, T] | None = None,
             save: Opt[HatMain | MänxFkt] = None) -> T:
        """Lasse den Spieler aus verschiedenen Optionen wählen.

        z.B:

        >>> Mänx().menu([("Nach Hause gehen", "hause", 1), ("Weitergehen", "weiter", 12)])

        erlaubt Eingaben 1, hau, hause für "Nach Hause gehen".

        """
        self._reset_laden(save)
        return ausgabe.menu(self, optionen, frage, versteckt, save)

    def genauer(self, text: Sequence[str]) -> None:
        """Frage nach, ob der Spieler etwas genauer erfahren will.
        Es kann sich um viel Text handeln."""
        if isinstance(self.ausgabe, Terminal):
            t = self.minput("Genauer? (Schreibe irgendwas für ja)")
            if t and t not in ("nein", "n"):
                for block in text:
                    self.ausgabe.malp(block)
        else:
            if self.menu([("Genauer", "", True), ("Weiter", "", False)]):
                self.ausgabe.malp("\n".join(text))

    def sleep(self, länge: float, pausenzeichen="."):
        """Lasse den Spieler warten und zeige nur in regelmäßigen Abständen Pausenzeichen."""
        for _i in range(int(länge / 0.5)):
            if self.ausgabe.terminal:
                print(pausenzeichen, end="", flush=True)
            else:
                malp(pausenzeichen, end="")
            sleep(0.5)
        malp()

    def tutorial(self, art: str) -> None:
        """Spielt das Tutorial für ein Spielsystem ab. Diese sind unter hilfe.HILFEN."""
        if not self.welt.ist("tutorial:" + art):
            for zeile in hilfe.HILFEN[art]:
                malp(zeile)
            self.welt.setze("tutorial:" + art)

    def inventar_zugriff(self, inv: InventarBasis,
                         nimmt: Union[bool, Sequence[str]] = False) -> None:
        """Ein Menu, um auf ein anderes Inventar zuzugreifen."""
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
        opts: list[MenuOption[nsc.NSC | None]] = [
            (f"Mit {g.name} reden", g.bezeichnung.kurz_name.lower(), g) for g in self.gefährten]
        if not opts:
            malp("Du hast noch keine Gefährten.")
        opts.append(("zurück", "f", None))
        if gefährte := self.menu(opts):
            gefährte.main(self)

    def add_verbrechen(self, name: str | Verbrechen | Verbrechensart, versuch=False):
        """Laste dem Mänxen ein Verbrechen an."""
        if isinstance(name, str):
            verbrechen = Verbrechen(Verbrechensart(name.upper()), versuch)
        elif isinstance(name, Verbrechen):
            verbrechen = name
        elif isinstance(name, Verbrechensart):
            verbrechen = Verbrechen(name, versuch)
        else:
            raise TypeError("name muss Verbrechen, VerbrechenArt oder Name "
                            "des Verbrechens sein.")
        self.verbrechen[verbrechen] += 1

    @property
    def am_laden(self) -> bool:
        return self._geladen_von is not None

    def _reset_laden(self, save: Fortsetzung | None) -> None:
        """Beende den Lade-Modus. Prüfe möglichst noch, ob man auch an der selben Stelle
        landet und gebe sonst eine Warnung aus."""
        warn = getLogger("xwatc.system").warn
        if self._geladen_von is not None:
            if self._geladen_von != save:
                warn(f"Load from {self._geladen_von} first asked for {save}.")

            self._geladen_von = None

    def save(self, punkt: HatMain | MänxFkt, name: Path | str | None = None) -> None:
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
        from pprint import pprint
        pprint(dict_)
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
            dict_ = yaml.safe_load_all(file)
            ans = mache_converter().structure(dict_, cls)
            assert ans._geladen_von
            ans.ausgabe = ausgabe
            return ans, ans._geladen_von


def schiebe_inventar(start: Inventar, ziel: Inventar):
    """Schiebe alles aus start in ziel"""
    for item, anzahl in start.items():
        ziel[item] += anzahl
    start.clear()


@define
class MissingIDError(Exception):
    id_: str


class Besuche:
    """Mache einer ID für ein Objekt aus dem Objektregister ein HatMain-object.
    Bei der Main wird das Objekt aus dem Register gesucht bzw. erzeugt und dann dessen
    Main aufgerufen."""

    def __init__(self, objekt_name: str):
        self.objekt_name = objekt_name
        assert self.objekt_name in _OBJEKT_REGISTER

    def main(self, mänx: Mänx):
        mänx.welt.obj(self.objekt_name).main(mänx)


def register(name: str) -> Callable[[Callable[[], HatMain]], Besuche]:
    """Registriere einen Erzeuger im Objekt-Register.
    Beispiel:
    ..
        @register("system.test.banana")
        def banane():
            class Banane:
                def main(mänx: Mänx):
                    malp("Du rutscht auf der Banane aus.")

    """

    def wrapper(func: Callable[[], HatMain]) -> Besuche:
        # assert name not in _OBJEKT_REGISTER,("Doppelte Registrierung " + name)
        _OBJEKT_REGISTER[name] = func
        return Besuche(name)

    return wrapper


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


from xwatc import anzeige, nsc, dorf, weg  # @UnusedImport @Reimport
if __debug__:
    from typing import get_type_hints
    get_type_hints(Mänx)
