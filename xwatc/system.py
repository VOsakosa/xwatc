from __future__ import annotations

from attrs import define
from collections import defaultdict
from collections.abc import Sequence, Callable, Iterator, Mapping
from logging import getLogger
import logging
from pathlib import Path
import pickle
from time import sleep
from typing import TypeVar, Any, Protocol
from typing import (Dict, List, Tuple, Union, Optional,
                    Set, Optional as Opt, TypeAlias)
import typing

from xwatc.terminal import Terminal
from xwatc.untersystem import hilfe
from xwatc.untersystem.itemverzeichnis import lade_itemverzeichnis, Item
from xwatc.untersystem.verbrechen import Verbrechen, Verbrechensart

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


MänxPrädikat = MänxFkt[bool]
Fortsetzung = Union[MänxFkt, HatMain, 'weg.Wegpunkt']
ITEMVERZEICHNIS = lade_itemverzeichnis(Path(__file__).parent / "itemverzeichnis.txt",
                                       Path(__file__).parent / "waffenverzeichnis.yaml")

_OBJEKT_REGISTER: Dict[str, Callable[[], 'HatMain']] = {}
ausgabe: Terminal | 'anzeige.XwatcFenster' = Terminal()


def get_classes(item: str) -> Iterator[str]:
    return ITEMVERZEICHNIS.get(item).yield_classes()


def get_preise(item: str) -> int:
    return ITEMVERZEICHNIS.get(item).get_preis()


def get_item(item_name: str) -> Item:
    return ITEMVERZEICHNIS.get(item_name)


T = TypeVar("T")
Tcov = TypeVar("Tcov", covariant=True)
MenuOption: TypeAlias = tuple[str, str, Tcov]
Inventar: TypeAlias = dict[str, int]
_null_func = int


@define
class Persönlichkeit:
    """ Deine Persönlichkeit innerhalb des Spieles """
    ehrlichkeit: int = 0
    stolz: int = 0
    arroganz: int = 0
    vertrauenswürdigkeit: int = 0
    hilfsbereischaft: int = 0
    mut: int = 0


class InventarBasis:
    """Ein Ding mit Inventar"""
    inventar: Inventar

    def __init__(self):
        self.inventar = defaultdict(int)

    def erhalte(self, item: str, anzahl: int = 1,
                von: Optional[InventarBasis] = None):
        """Transferiert Items in das Inventar des Mänxen und gibt das aus."""
        if von:
            anzahl = min(anzahl, von.inventar[item])
        anzahl = max(anzahl, -self.inventar[item])
        if not anzahl:
            return
        self.inventar[item] += anzahl
        if von:
            von.inventar[item] -= anzahl

    def inventar_zeigen(self):
        ans = []
        for item, anzahl in self.inventar.items():
            if anzahl:
                ans.append(f"{anzahl}x {item}")
        return ", ".join(ans)

    def erweitertes_inventar(self):
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

    def items(self):
        for item, anzahl in self.inventar.items():
            if anzahl:
                yield item

    def hat_item(self, item, anzahl=1):
        return item in self.inventar and self.inventar[item] >= anzahl


class Karawanenfracht(InventarBasis):
    """Die Fracht einer Karawane zeigt nicht direkt ihr Gold (, da sie keines hat)"""

    def karawanenfracht_anzeigen(self):
        ans = []
        if not any(self.inventar.values()):
            return "Nichts da."
        for item, anzahl in sorted(self.inventar.items()):
            if anzahl and item != "Gold":
                item_obj = get_item(item)
                kosten = get_preise(item)
                ans.append(f"{anzahl:>4}x {item_obj:<20} ({kosten:>3}G)")
        return "\n".join(ans)


class Mänx(InventarBasis, Persönlichkeit):
    """Der Hauptcharakter des Spiels, alles dreht sich um ihn, er hält alle
    Information."""

    def __init__(self, ausgabe=ausgabe) -> None:
        super().__init__()
        self.ausgabe: Terminal | 'anzeige.XwatcFenster' = ausgabe
        self.gebe_startinventar()
        self.gefährten: List['nsc.NSC'] = []
        self.titel: Set[str] = set()
        self.lebenspunkte = 100
        self.fähigkeiten: Set[str] = set()
        self.welt = Welt("bliblablux")
        self.missionen: List[None] = list()
        self.verbrechen: defaultdict[Verbrechen, int] = defaultdict(int)
        self.rasse = "Arak"
        self.context: Any = None
        self.speicherpunkt: Opt[Fortsetzung] = None
        self.speicherdatei_name: Opt[str] = None

    def hat_fähigkeit(self, name: str) -> bool:
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

    def minput(self, *args, **kwargs):
        self.speicherpunkt = None
        return self.ausgabe.minput(self, *args, **kwargs)

    def ja_nein(self, *args, **kwargs):
        self.speicherpunkt = None
        return self.ausgabe.ja_nein(self, *args, **kwargs)

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
        self.speicherpunkt = None
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

    def __getstate__(self):
        dct = self.__dict__.copy()
        del dct["ausgabe"]
        assert dct["speicherpunkt"]
        return dct

    def __setstate__(self, dct: dict):
        bsp = type(self)()
        self.__dict__.update(bsp.__dict__)
        self.__dict__.update(dct)
        self.ausgabe = ausgabe

    def save(self, punkt: HatMain | MänxFkt, name: Opt[str] = None) -> None:
        self.speicherpunkt = punkt
        SPEICHER_VERZEICHNIS.mkdir(exist_ok=True, parents=True)
        if not self.speicherdatei_name:
            self.speicherdatei_name = "welt"
        if name:
            self.speicherdatei_name = name
        filename = self.speicherdatei_name + ".pickle"

        with open(SPEICHER_VERZEICHNIS / filename, "wb") as write:
            pickle.dump(self, write)
        self.speicherpunkt = None


class Welt:
    """Speichert den Zustand der Welt, in der sich der Hauptcharakter befindet."""

    def __init__(self, name: str) -> None:
        self.inventar: Dict[str, int] = {}
        self.name = name
        self.objekte: Dict[str, Any] = {}
        self.tag = 0.0

    def setze(self, name: str) -> None:
        """Setze eine Welt-Variable"""
        self.inventar[name] = 1

    def ist(self, name: str) -> bool:
        """Testet eine Welt-Variable."""
        return name in self.inventar and bool(self.inventar[name])

    def get_or_else(self, name: str, fkt: Callable[..., T], *args,
                    **kwargs) -> T:
        """Hole ein Objekt aus dem Speicher oder erzeuge ist mit *fkt*"""
        if name in self.objekte:
            ans = self.objekte[name]
            if isinstance(fkt, type):
                assert isinstance(ans, fkt)
            return ans
        else:
            ans = fkt(*args, **kwargs)
            self.objekte[name] = ans
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
        """Hole ein registriertes oder existentes Objekt."""
        if isinstance(name, Besuche):
            name = name.objekt_name
        if name in self.objekte:
            return self.objekte[name]
        from xwatc import nsc  # @Reimport
        obj: HatMain
        if name in nsc.CHAR_REGISTER:
            obj = nsc.CHAR_REGISTER[name].zu_nsc()
        elif name in _OBJEKT_REGISTER:
            obj = _OBJEKT_REGISTER[name]()
        else:
            raise MissingID(f"Das Objekt {name} existiert nicht.")
        self.objekte[name] = obj
        return obj

    def nächster_tag(self, tage: int = 1):
        """Springe zum nächsten Tag"""
        self.tag = int(self.tag + tage)

    def get_tag(self) -> int:
        """Gebe den Tag seit Anfang des Spiels aus. Der erste Tag ist 0."""
        return int(self.tag)

    def is_nacht(self) -> bool:
        return self.tag % 1.0 >= 0.5

    def tick(self, uhr: float):
        """Lasse etwas Zeit vergehen."""
        self.tag += uhr

    def uhrzeit(self) -> tuple[int, int]:
        """Gebe die momentane Uhrzeit als Tupel (Stunde, Minute) aus."""
        stunde, rest = divmod(30 + (self.tag % 1.) * 24, 1.)
        minute = (rest * 60) % 1.
        return int(stunde) % 24, int(minute)


def schiebe_inventar(start: Inventar, ziel: Inventar):
    """Schiebe alles aus start in ziel"""
    for item, anzahl in start.items():
        ziel[item] += anzahl
    start.clear()


@define
class MissingIDError(Exception):
    id_: str


Speicherpunkt = Union[HatMain, MänxFkt]


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


def minput(mänx: Mänx, frage: str, möglichkeiten=None, lower=True, save=None) -> str:
    """Ruft die Methode auf Mänx auf."""
    return mänx.minput(frage, möglichkeiten, lower, save)


def mint(*text) -> None:
    """Printe und warte auf ein Enter."""
    ausgabe.mint(*text)


def sprich(sprecher: str, text: str, warte: bool = False, wie: str = "") -> None:
    ausgabe.sprich(sprecher, text, warte, wie)


def malp(*text, sep=" ", end='\n', warte=False) -> None:
    """Angenehm zu lesender, langsamer Print."""
    ausgabe.malp(*text, sep=sep, end=end, warte=warte)


def malpw(*text, sep=" ", end='\n') -> None:
    ausgabe.malp(*text, sep=sep, end=end, warte=True)


def ja_nein(mänx: Mänx, frage, save=None) -> bool:
    """Ja-Nein-Frage"""
    return mänx.ja_nein(frage, save)


def kursiv(text: str) -> str:
    """Packt text so, dass es kursiv ausgedruckt wird."""
    return ausgabe.kursiv(text)


class Spielende(Exception):
    """Diese Exception wird geschmissen, um das Spiel zu beenden."""
