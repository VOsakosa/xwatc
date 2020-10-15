from collections import defaultdict
from typing import Sequence, Dict, List, Tuple, TypeVar, Callable, Any, Union,\
    overload, Optional, Iterator

ITEMVERZEICHNIS = {
    "Beere": "Obst",
    "Eisen": "Metall",
    "Dolch": "normale Waffe",
    "Hering": "Fisch",
    "Holz": "Holz",
    "Hühnerfleisch": "Fleisch",
    "Kohle": "Brennstoff",
    "Leere": "Scherz-Item",
    "Mantel": "Kleidung",
    "Messer": "normale Waffe",
    "Mugel des Sprechens": "Mugel",
    "Normales Schwert": "normale Waffe",
    "Riesenschneckeninnereien": "Superpapierrohstoff",
    "Riesenschneckenfleisch": "Fleisch",
    "Ring des Berndoc": "Ring",
    "Sardine": "Fisch",
    "Schild": "Rüstungsgegenstand",
    "Schneckenschleim": "Superfolienrohstoff",
    "Scholle": "Fisch",
    "Schwert": "legendäre Waffe",
    "Speer": "normale Waffe",
    "Spitzhacke": "normales Werkzeug",
    "Stein": "Stein",
    "Stein der aussieht wie ein Hühnerei": "Heilige Tagesei",
    "Stöckchen": "Holz",
    "Talisman der Schreie": "Talisman",
    "Unterhose": "Kleidung",

}

UNTERKLASSEN = {
    "Fisch": "Nahrung",
    "Fleisch": "Nahrung",
    "legendäre Waffe": "Waffe",
    "Ring": "Ausrüstung",
    "Rüstungsgegenstand": "Ausrüstung",
}


def get_class(item: str) -> Optional[str]:
    return ITEMVERZEICHNIS.get(item)


def get_classes(item: str) -> Iterator[str]:
    c = get_class(item)
    if c:
        yield c
        while c in UNTERKLASSEN:
            c = UNTERKLASSEN[c]
            yield c


T = TypeVar("T")

MenuOption = Tuple[str, str, T]
Inventar = Dict[str, int]


class InventarBasis:
    """Ein Ding mit Inventar"""
    inventar: Inventar

    def __init__(self):
        self.inventar = defaultdict(lambda: 0)

    def inventar_zeigen(self):
        ans = []
        for item, anzahl in self.inventar.items():
            if anzahl:
                ans.append(f"{anzahl}x {item}")
        return ", ".join(ans)

    @property
    def gold(self) -> int:
        return self.inventar["Gold"]

    @gold.setter
    def gold(self, menge: int) -> None:
        self.inventar["Gold"] = menge

    def hat_klasse(self, *klassen) -> bool:
        """Prüfe, ob mänx item aus einer der Klassen besitzt."""
        for item in self.items():
            if any(c in klassen for c in get_classes(item)):
                return True
        return False

    def items(self):
        for item, anzahl in self.inventar.items():
            if anzahl:
                yield item

    def hat_item(self, item, anzahl=1):
        return item in self.inventar and self.inventar[item] >= anzahl


class Mänx(InventarBasis):
    """Der Hauptcharakter des Spiels, alles dreht sich um ihn, er hält alle
    Information."""

    def __init__(self):
        super().__init__()
        self.inventar["Gold"] = 33
        self.inventar["Mantel"] = 1
        self.inventar["Unterhose"] = 1
        self.inventar["Hose"] = 1
        self.inventar["T-Shirt"] = 1
        self.inventar["Gürtel"] = 1
        self.inventar["Socke"] = 2
        self.inventar["Turnschuh"] = 2
        self.inventar["Mütze"] = 1
        self.gefährten = []
        self.titel = set()
        self.lebenswille = 10
        self.fähigkeiten = set()
        self.welt = Welt("bliblablux")
        self.missionen = list()

    def missionen_zeigen(self):
        ans = []
        for item, anzahl in self.inventar.items():
            if anzahl:
                ans.append(f"{anzahl}x {item}")
        return ", ".join(ans)

    def inventar_leeren(self) -> None:
        self.inventar.clear()
        self.titel.clear()
        self.gefährten.clear()

    def get_kampfkraft(self) -> int:
        if any(get_class(it) == "magische Waffe" for it in self.items()):
            return 2000
        if any(get_class(it) == "Waffe" for it in self.items()):
            return 1000
        return 20

    def erhalte(self, item, anzahl=1):
        print(f"Du erhältst {anzahl} {item}")
        self.inventar[item] += anzahl

    def will_weiterleben(self):
        return self.lebenswille > 0

    def minput(self, *args, **kwargs):
        return minput(self, *args, **kwargs)

    @overload
    def menu(self, frage: str, optionen: List[MenuOption[T]],
             gucken: Union[Sequence[str], Callable[[], Any]] = ...,
             versteckt: None = None) -> T: ...

    @overload
    def menu(self, frage: str, optionen: List[MenuOption[T]],
             gucken: Union[Sequence[str], Callable[[], Any]] = ...,
             versteckt: Sequence[str] = ...) -> Union[str, T]: ...

    def menu(self, frage, optionen,
             gucken=("Hier gibt es nichts zu sehen",), versteckt=None):
        """Ähnlich wie Minput, nur werden jetzt Optionen als Liste gegeben."""
        # print("Du kannst")
        print()
        for name, kurz, _ in optionen:
            print("-", name, " (", kurz, ")", sep="")
        kurz_optionen = " " + "/".join(o[1] for o in optionen)
        if len(kurz_optionen) < 50:
            frage += kurz_optionen + " "
        while True:
            eingabe = input(frage).lower()
            if versteckt and eingabe in versteckt:
                return eingabe
            elif not eingabe:
                # Nach leerer Option suchen
                for _, o, v in optionen:
                    if not o:
                        return v
            elif eingabe == "g" or eingabe == "gucken":
                print(gucken)
            elif not spezial_taste(self, eingabe):
                kandidaten = [(o, v) for _, o, v in optionen
                              if o.startswith(eingabe)]
                if len(kandidaten) == 1:
                    return kandidaten[0][1]
                elif not kandidaten:
                    print("Keine Antwort beginnt mit", eingabe)
                else:
                    print("Es könnte eines davon sein:",
                          ",".join(o for o, v in kandidaten))

    def genauer(self, text: Sequence[str]) -> None:
        t = self.minput("Genauer? (Schreibe irgendwas für ja)")
        if t and t not in ("nein", "n"):
            for block in text:
                print(block)


class Gefährte:
    def __init__(self, name):
        self.name = name


class Welt:
    def __init__(self, name: str) -> None:
        self.inventar: Dict[str, int] = {}
        self.name = name
        self.objekte: Dict[str, Any] = {}

    def setze(self, name: str) -> None:
        """Setze eine Welt-Variable"""
        self.inventar[name] = 1

    def ist(self, name: str) -> bool:
        return name in self.inventar and bool(self.inventar[name])

    def get_or_else(self, name: str, fkt: Callable[..., T], *args,
                    **kwargs) -> T:
        if name in self.objekte:
            ans = self.objekte[name]
            if isinstance(fkt, type):
                assert isinstance(ans, fkt)
            return ans
        else:
            return fkt(*args, **kwargs)

    def nächster_tag(self, tage: int = 1):
        self.inventar["generell:tag"] += tage

    def get_tag(self) -> int:
        return self.inventar["generell:tag"]


def schiebe_inventar(start: Inventar, ziel: Inventar):
    """Schiebe alles aus start in ziel"""
    for item, anzahl in start.items():
        ziel[item] += anzahl
    start.clear()
# EIN- und AUSGABE


def minput(mänx: Mänx, frage: str, möglichkeiten=None, lower=True) -> str:
    """Manipulierter Input
    Wenn möglichkeiten (in kleinbuchstaben) gegeben, dann muss die Antwort eine davon sein."""
    if not frage.endswith(" "):
        frage += " "
    while True:
        taste = input(frage)
        if lower:
            taste = taste.lower()
        if spezial_taste(mänx, taste):
            pass
        elif not möglichkeiten or taste in möglichkeiten:
            return taste


def spezial_taste(mänx, taste: str) -> bool:
    """Führe die Spezialaktion taste aus, oder gebe Falsch zurück."""
    if taste == "e":
        print(mänx.inventar_zeigen())
    elif taste == "q":
        print(mänx.missionen_zeigen())
    elif taste == "sterben":
        mänx.lebenswille = 0
    elif taste == "sofort sterben":
        raise Spielende()
    else:
        return False
    return True


def mint(*text):
    """Printe und warte auf ein Enter."""
    input(" ".join(str(t) for t in text))


def sprich(sprecher: str, text: str):
    mint(f'{sprecher}: "{text}"')


def ja_nein(mänx, frage):
    """Ja-Nein-Frage"""
    ans = minput(mänx, frage, ["j", "ja", "n", "nein"]).lower()
    return ans == "j" or ans == "ja"


def kursiv(text: str) -> str:
    """Packt text so, dass es kursiv ausgedruckt wird."""
    return "\x1b[3m" + text + "\x1b[0m"


class Spielende(Exception):
    """Diese Exception wird geschmissen, um das Spiel zu beenden."""
