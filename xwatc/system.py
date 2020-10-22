from collections import defaultdict
from typing import Sequence, Dict, List, Tuple, TypeVar, Callable, Any, Union,\
    overload, Optional, Iterator, Mapping, Set
from time import sleep
import re

ITEMVERZEICHNIS = {
    "Apfel": "Obst",
    "Aprikose": "Obst",
    "Banane": "Obst",
    "Beere": "Obst",
    "Einfaches Kleid": "Kleidung",
    "Eisen": "Metall",
    "Dolch": "normale Waffe",
    "Distelblüte": "Blume",
    "Gänseblümchen": "Blume",
    "Hering": "Fisch",
    "Holz": "Holz",
    "Hose": "Kleidung",
    "Hühnerfleisch": "Fleisch",
    "Klatschmohn": "Blume",
    "Kohle": "Brennstoff",
    "Leere": "Scherz-Item",
    "mächtige Axt": "legendäre Waffe",
    "Mantel": "Kleidung",
    "Menschenskelett": "Dekoration",
    "Messer": "normale Waffe",
    "Mugel der Draufsicht": "Mugel",
    "Mugel des Sprechens": "Mugel",
    "Normales Schwert": "normale Waffe",
    "Riesenschneckeninnereien": "Superpapierrohstoff",
    "Riesenschneckenfleisch": "Fleisch",
    "Ring des Berndoc": "Ring",
    "Rose": "Blume",
    "Sardine": "Fisch",
    "Schild": "Rüstungsgegenstand",
    "Schneckenschleim": "Superfolienrohstoff",
    "Schnöder Ehering": "Ring",
    "Scholle": "Fisch",
    "Schwert": "legendäre Waffe",
    "Speer": "normale Waffe",
    "Spitzhacke": "normales Werkzeug",
    "Stein": "Stein",
    "Stein der aussieht wie ein Hühnerei": "Heiliges Tagesei",
    "Stöckchen": "Holz",
    "Talisman der Schreie": "Talisman",
    "Unterhose": "Kleidung",
    "Zwetschge": "Obst",
}

UNTERKLASSEN = {
    "Fisch": "Nahrung",
    "Fleisch": "Nahrung",
    "legendäre Waffe": "Waffe",
    "normale Waffe": "Waffe",
    "Obst": "Nahrung",
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
Tcov = TypeVar("Tcov", covariant=True)
MenuOption = Tuple[str, str, Tcov]
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

    def erweitertes_inventar(self):
        import xwatc.haendler
        if not any(self.inventar.values()):
            return "Nichts da."
        ans = ["{} Gold".format(self.inventar["Gold"])]
        for item, anzahl in sorted(self.inventar.items()):
            if anzahl and item != "Gold":
                klasse = get_class(item) or "?"
                kosten = xwatc.haendler.ALLGEMEINE_PREISE.get(item, "?")
                ans.append(f"{anzahl:>4}x {item:<20} ({kosten:>3}G) {klasse}")
        return "\n".join(ans)

    @property
    def gold(self) -> int:
        return self.inventar["Gold"]

    @gold.setter
    def gold(self, menge: int) -> None:
        self.inventar["Gold"] = menge

    def hat_klasse(self, *klassen: str) -> bool:
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

    def __init__(self) -> None:
        super().__init__()
        self.gebe_startinventar()
        self.gefährten: List['Gefährte'] = []
        self.titel: Set[str] = set()
        self.lebenswille = 10
        self.fähigkeiten: Set[str] = set()
        self.welt = Welt("bliblablux")
        self.missionen: List[None] = list()
        self.rasse = "Arak"
        self.context: Any = None

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

    def missionen_zeigen(self):
        ans = []
        for item, anzahl in self.inventar.items():
            if anzahl:
                ans.append(f"{anzahl}x {item}")
        return ", ".join(ans)

    def inventar_leeren(self) -> None:
        """Töte den Menschen, leere sein Inventar und entlasse
        seine Gefährten."""
        self.inventar.clear()
        # self.titel.clear()
        self.gefährten.clear()
        self.gebe_startinventar()

    def get_kampfkraft(self) -> int:
        if any(get_class(it) == "magische Waffe" for it in self.items()):
            return 2000
        if any(get_class(it) == "Waffe" for it in self.items()):
            return 1000
        return 20

    def erhalte(self, item: str, anzahl: int = 1,
                von: Optional[InventarBasis] = None):
        if von:
            anzahl = min(anzahl, von.inventar[item])
            if not anzahl:
                return
        print(f"Du erhältst {anzahl} {item}")
        self.inventar[item] += anzahl
        if von:
            von.inventar[item] -= anzahl

    def will_weiterleben(self):
        return self.lebenswille > 0

    def minput(self, *args, **kwargs):
        return minput(self, *args, **kwargs)

    def ja_nein(self, *args, **kwargs):
        return ja_nein(self, *args, **kwargs)

    def menu(self,
             optionen: List[MenuOption[T]],
             frage: str = "",
             gucken: Union[Sequence[str], Callable[[], Any]] =
             ("Hier gibt es nichts zu sehen",),
             versteckt: Optional[Mapping[str, T]] = None) -> T:
        """Ähnlich wie Minput, nur werden jetzt Optionen als Liste gegeben.

        Die Zuordnung geschieht in folgender Reihenfolge
        #. Versteckte Optionen
        #. Optionen
        #. Gucken
        #. Spezialtasten
        #. Nummer
        #. Passendste Antwort
        """
        # print("Du kannst")
        print()
        for i, (name, kurz, _) in enumerate(optionen):
            print(i + 1, ".", name, " [", kurz, "]", sep="")
        kurz_optionen = " " + "/".join(o[1] for o in optionen)
        if len(kurz_optionen) < 50:
            frage += kurz_optionen + " "
        while True:
            eingabe = input(frage).lower()
            if versteckt and eingabe in versteckt:
                return versteckt[eingabe]
            kandidaten = []
            for _, o, v in optionen:
                if o == eingabe:  # Genauer Match
                    return v
                elif o.startswith(eingabe):
                    kandidaten.append((o, v))
            if eingabe == "g" or eingabe == "gucken":
                print(gucken)
            elif not spezial_taste(self, eingabe) and eingabe:
                try:
                    return optionen[int(eingabe) - 1][2]
                except (IndexError, ValueError):
                    pass
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

    def sleep(self, länge: float, pausenzeichen="."):
        for _i in range(int(länge/0.5)):
            print(pausenzeichen, end="", flush=True)
            sleep(0.5)
        print()

    def inventar_zugriff(self, inv: InventarBasis,
                         nimmt: Union[bool, Sequence[str]] = False) -> None:
        """Ein Menu, um auf ein anderes Inventar zuzugreifen."""
        print(inv.erweitertes_inventar())
        while True:
            a = self.minput(">")
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
                    if ding in inv.inventar:
                        self.erhalte(ding, inv.inventar[ding], inv)
                    else:
                        print(f"Kein {ding} da.")
                elif len(args) == 2:
                    ding = args[1]
                    try:
                        anzahl = int(args[0])
                        assert anzahl > 0
                    except (AssertionError, ValueError):
                        print("Gebe eine positive Anzahl an.")
                    else:
                        if ding in inv.inventar:
                            self.erhalte(ding, anzahl, inv)
                        else:
                            print(f"Kein {ding} da.")
            elif co == "a" or co == "auslage":
                print(inv.erweitertes_inventar())
            elif co == "g" or co == "geben":
                if not nimmt:
                    print("Du kannst hier nichts hereingeben")
                elif len(args) == 1:
                    ding = args[0]
                    if ding in self.inventar:
                        inv.inventar[ding] = self.inventar[ding]
                        self.inventar[ding] = 0
                    else:
                        print(f"Du hast kein {ding}.")
                elif len(args) == 2:
                    ding = args[1]
                    try:
                        anzahl = int(args[0])
                        assert anzahl > 0
                    except (AssertionError, ValueError):
                        print("Gebe eine positive Anzahl an.")
                    else:
                        if self.hat_item(ding, anzahl):
                            self.inventar[ding] -= anzahl
                            inv.inventar[ding] += anzahl
                        else:
                            print(f"Du hast kein {ding}.")

class Gefährte:
    def __init__(self, name):
        self.name = name


class Welt:
    """Speichert den Zustand der Welt, in der sich der Hauptcharakter befindet."""

    def __init__(self, name: str) -> None:
        self.inventar: Dict[str, int] = {}
        self.name = name
        self.objekte: Dict[str, Any] = {}
        self.inventar["generell:tag"] = 0

    def setze(self, name: str) -> None:
        """Setze eine Welt-Variable"""
        self.inventar[name] = 1

    def ist(self, name: str) -> bool:
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
            return fkt(*args, **kwargs)

    def am_leben(self, name: str) -> bool:
        """Prüfe, ob das Objekt name da und noch am Leben ist."""
        from xwatc import dorf
        return name in self.objekte and (
            not isinstance(self.objekte[name], dorf.NSC) or
            not self.objekte[name].tot)

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


def spezial_taste(mänx: Mänx, taste: str) -> bool:
    """Führe die Spezialaktion taste aus, oder gebe Falsch zurück."""
    if taste == "e":
        print(mänx.inventar_zeigen())
    elif taste == "ee":
        print(mänx.erweitertes_inventar())
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


def sprich(sprecher: str, text: str, warte: bool = False):
    if warte:
        mint(f'{sprecher}: "{text}"')
    else:
        print(end=f'{sprecher}: "')
        for word in re.split(r"(\W)", text):
            print(end=word, flush=True)
            sleep(0.05)
        print('"')
        


def ja_nein(mänx, frage):
    """Ja-Nein-Frage"""
    ans = minput(mänx, frage, ["j", "ja", "n", "nein"]).lower()
    return ans == "j" or ans == "ja"


def kursiv(text: str) -> str:
    """Packt text so, dass es kursiv ausgedruckt wird."""
    return "\x1b[3m" + text + "\x1b[0m"


class Spielende(Exception):
    """Diese Exception wird geschmissen, um das Spiel zu beenden."""
