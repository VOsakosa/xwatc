from collections import defaultdict
from typing import Sequence, Dict, List, Tuple, TypeVar

ITEMVERZEICHNIS = {
    "Beere": "Obst",
    "Hering": "Fisch",
    "Holz": "Holz",
    "Hühnerfleisch": "Fleisch",
    "Leere": "Scherz-Item",
    "Mantel": "Kleidung",
    "Messer": "Waffe",
    "Mugel des Sprechens": "Mugel",
    "Normales Schwert": "Waffe",
    "Riesenschneckeninnereien": "Superpapierrohstoff",
    "Riesenschneckenfleisch": "Fleisch",
    "Ring des Berndoc": "Ring",
    "Sardine": "Fisch",
    "Schild": "Rüstungsgegenstand",
    "Schneckenschleim": "Superfolienrohstoff",
    "Scholle": "Fisch",
    "Schwert": "magische Waffe",
    "Speer": "Waffe",
    "Spitzhacke": "Werkzeug",
    "Stein": "Stein",
    "Stein der aussieht wie ein Hühnerei": "Heilige Tagesei",
    "Stöckchen": "Holz",
    "Unterhose": "Kleidung",
}


def get_class(item):
    return ITEMVERZEICHNIS.get(item)

Inventar = Dict[str, int]
T = TypeVar("T")

class Mänx:
    """Der Hauptcharakter des Spiels, alles dreht sich um ihn, er hält alle
    Information."""

    def __init__(self):
        self.inventar: Inventar = defaultdict(lambda: 0)
        self.inventar["Gold"] = 33
        self.inventar["Mantel"] = 1
        self.inventar["Unterhose"] = 1
        self.gefährten = []
        self.titel = set()
        self.lebenswille = 10
        self.fähigkeiten = set()
        self.welt = Welt("bliblablukc")

    def inventar_zeigen(self):
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

    @property
    def gold(self) -> int:
        return self.inventar["Gold"]

    @gold.setter
    def gold(self, menge: int) -> None:
        self.inventar["Gold"] = menge

    def hat_klasse(self, *klassen) -> bool:
        """Prüfe, ob mänx item aus einer der Klassen besitzt."""
        for item in self.items():
            if get_class(item) in klassen:
                return True
        return False

    def items(self):
        for item, anzahl in self.inventar.items():
            if anzahl:
                yield item

    def hat_item(self, item, anzahl=1):
        return item in self.inventar and self.inventar[item] >= anzahl

    def erhalte(self, item, anzahl=1):
        print(f"Du erhälst {anzahl} {item}")
        self.inventar[item] += anzahl

    def will_weiterleben(self):
        return self.lebenswille > 0

    def minput(self, *args, **kwargs):
        return minput(self, *args, **kwargs)

    def menu(self, frage: str, optionen: List[Tuple[str, str, T]]) -> T:
        """Ähnlich wie Minput, nur werden jetzt Optionen als Liste gegeben."""
        print("Du kannst")
        for name, kurz, _ in optionen:
            print(name, " (", kurz, ")", sep="")
        kurz_optionen = " " + "/".join(o[0] for o in optionen)
        if len(kurz_optionen) < 50:
            frage += kurz_optionen
        while True:
            eingabe = input(frage).lower()
            if not eingabe:
                # Nach leerer Option suchen
                for _, o, v in optionen:
                    if not o:
                        return v
            elif not spezial_taste(self, eingabe):
                kandidaten = [(o,v) for _,o,v in optionen 
                              if o.startswith(eingabe)]
                if len(kandidaten) == 1:
                    return kandidaten[0][1]
                elif not kandidaten:
                    print("Keine Antwort beginnt mit", eingabe)
                else:
                    print("Es könnte eines davon sein:", 
                          ",".join(o for o, v in kandidaten))
        

    def genauer(self, text: Sequence[str]):
        t = self.minput("Genauer? (Schreibe irgendwas für ja)")
        if t:
            for block in text:
                print(block)


class Gefährte:
    def __init__(self, name):
        self.name = name


class Welt:
    def __init__(self, name):
        self.inventar = {}
        self.name = name

    def setze(self, name):
        self.inventar[name] = 1

    def ist(self, name):
        return name in self.inventar and self.inventar[name]

def schiebe_inventar(start: Inventar, ziel: Inventar):
    """Schiebe alles aus start in ziel"""
    for item, anzahl in start.items():
        ziel[item] += anzahl
    start.clear()
# EIN- und AUSGABE

def minput(mänx, frage, möglichkeiten=None, lower=True):
    """Manipulierter Input
    Wenn möglichkeiten (in kleinbuchstaben) gegeben, dann muss die Antwort eine davon sein."""
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


def ja_nein(mänx, frage):
    """Ja-Nein-Frage"""
    ans = minput(mänx, frage, ["j", "ja", "n", "nein"]).lower()
    return ans == "j" or ans == "ja"


def kursiv(text: str) -> str:
    """Packt text so, dass es kursiv ausgedruckt wird."""
    return "\x1b[3m" + text + "\x1b[0m"


class Spielende(Exception):
    """Diese Exception wird geschmissen, um das Spiel zu beenden."""
