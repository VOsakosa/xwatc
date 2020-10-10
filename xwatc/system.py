from collections import defaultdict

ITEMVERZEICHNIS = {
     "Beere": "Obst",
     "Hering":"Fisch",
     "Holz":"Holz",
     "Hühnerfleisch":"Fleisch",
     "Leere": "Scherz-Item",
     "Mantel": "Kleidung",
     "Messer":"Waffe",
     "Mugel des Sprechens":"Mugel",
     "Normales Schwert": "Waffe",
     "Riesenschneckeninnereien": "Superpapierrohstoff",
     "Riesenschneckenfleisch": "Fleisch",
     "Ring des Berndoc": "Ring",
     "Sardine":"Fisch",
     "Schild": "Rüstungsgegenstand",
     "Schneckenschleim":"Superfolienrohstoff",
     "Scholle":"Fisch",
     "Schwert": "magische Waffe",
     "Speer": "Waffe",
     "Spitzhacke":"Werkzeug",
     "Stein":"Stein",
     "Stein der aussieht wie ein Hühnerei": "Heilige Tagesei",
     "Stöckchen": "Holz",
     "Unterhose": "Kleidung",
}

def get_class(item):
    return ITEMVERZEICHNIS.get(item)

class Mänx:
    def __init__(self):
        self.inventar = defaultdict(lambda:0)
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
        return self.lebenswille>0

    def minput(self, *args, **kwargs):
        return minput(self, *args, **kwargs)

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

def minput(mänx, frage, möglichkeiten=None, lower=True):
    """Manipulierter Input
    Wenn möglichkeiten (in kleinbuchstaben) gegeben, dann muss die Antwort eine davon sein."""
    while True:
        taste = input(frage)
        if lower:
            taste = taste.lower()
        if taste == "e":
            print(mänx.inventar_zeigen())
        elif taste == "sterben":
            mänx.lebenswille = 0
        elif taste == "sofort sterben":
            raise Spielende()
        elif not möglichkeiten or taste in möglichkeiten:
            return taste

def ja_nein(mänx, frage):
    """Ja-Nein-Frage"""
    ans = minput(mänx, frage, ["j","ja","n","nein"]).lower()
    return ans=="j" or ans == "ja"

def kursiv(text: str) -> str:
    """Packt text so, dass es kursiv ausgedruckt wird."""
    return "\x1b[3m" + text + "\x1b[0m"

class Spielende(Exception):
    pass