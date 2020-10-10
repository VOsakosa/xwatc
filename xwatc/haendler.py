from typing import Dict, List, Optional as Op

from xwatc.system import Mänx, minput, Gefährte, ja_nein, get_class

class Händler:
    def __init__(self, name, kauft: Op[List[str]], verkauft, gold: int):
        """Neuer Händler namens *name*, der Sachen aus den Kategorien *kauft* kauft.
        *verkauft* ist das Inventar. *gold* ist die Anzahl von Gold."""
        self.name = name
        self.kauft = kauft
        # Anzahl, Preis
        self.verkauft = verkauft
        self.gold: int = gold

    def kaufen(self, mänx: Mänx, name: str, anzahl: int=1) -> bool:
        """Mänx kauft von Händler"""
        if name not in self.verkauft:
            return False
        preis = self.verkauft[name][1]
        if self.verkauft[name][0] >= anzahl and mänx.inventar["Gold"] >= preis:
            self.verkauft[name][0] -= anzahl
            self.gold += anzahl * preis
            mänx.inventar["Gold"] -= anzahl * preis
            mänx.inventar[name] += anzahl
            return True
        return False

    def kann_kaufen(self, name: str):
        return self.kauft is None or get_class(name) in self.kauft

    def verkaufen(self, mänx: Mänx, name: str, preis: int, anzahl: int = 1) -> bool:
        """Mänx verkauft an Händler"""
        if self.kann_kaufen(name) and self.gold >= preis * anzahl:
            self.gold -= preis * anzahl
            mänx.inventar["Gold"] += preis * anzahl
            mänx.inventar[name] -= anzahl
            if name not in self.verkauft:
                self.verkauft[name] = [anzahl, preis + 1]
            else:
                self.verkauft[name][0] += 1

    def get_preis(self, name: str) -> Op[int]:
        return None

    def _verkaufen(self, mänx, gegenstand, menge):
        """Versuch interaktiv, an den Händler zu verkaufen."""
        if menge <= 0:
            print("Jetzt mal ernsthaft, gib eine positive Anzahl an.")
        elif not mänx.hat_item(gegenstand, menge):
            print(f'Du hast nicht genug "{gegenstand}" zum verkaufen. Versuch "e".')
        elif not self.kann_kaufen(gegenstand):
            if self.kauft:
                print("So etwas kauft der Händler nicht")
                print("Der Händler kauft nur", ", ".join(self.kauft))
            else:
                print("Der Händler verkauft nur")
                
        else:
            preis = self.get_preis(gegenstand)
            if preis is None:
                print("Der Händler kann dir dafür keinen Preis nennen")
            elif preis * menge >= mänx.inventar["Gold"]:
                print("So viel kannst du dir nicht leisten")
            else:
                self.verkaufen(mänx, gegenstand, preis, menge)

    def zeige_auslage(self):
        if self.verkauft:
            länge = max(len(a) for a in self.verkauft) + 1
            for item, (anzahl, preis) in self.verkauft.items():
                if anzahl:
                    print(f"{item:<{länge}}{anzahl:04}x {preis:3} Gold")
        else:
            print("Der Händler*in hat nichts mehr zu verkaufen")

    def vorstellen(self):
        print("Du stehst du vor dem Händler*in", name)
        if self.kauft is None:
            print("Er kauft grundsätzlich alles")
        elif self.kauft:
            print("Er kauft", ", ".join(self.kauft))
        self.zeige_auslage()

    def handeln(self, mänx):
        """Lass Spieler mit Mänx handeln"""
        self.vorstellen()
        while True:
            a = minput(mänx, "handel>", lower=False)
            al = a.lower()
            if al.startswith("k ") or al.startswith("kaufe "):
                kauft = a.split(" ", 2)
                try:
                    menge = int(kauft[1])
                    gegenstand = kauft[2]
                except (ValueError, IndexError):
                    print("Syntax: k [anzahl] [gegenstand]")
                    print("Bsp: k 12 Stein der Weisen")
                else:
                    if menge > 0 and self.kaufen(mänx, gegenstand, menge):
                        print("gekauft")
                    else:
                        print("nicht da / nicht genug Geld")
            elif al.startswith("v ") or al.startswith("verkaufe "):
                kauft = a.split(" ", 2)
                try:
                    menge = int(kauft[1])
                    gegenstand = kauft[2]
                except (ValueError, IndexError):
                    print("Syntax: v [anzahl] [gegenstand]")
                    print("Bsp: v 12 Augapfel")
                else:
                    self._verkaufen(mänx, gegenstand, menge)
            elif al.startswith("p ") or al.startswith("preis "):
                _, item = a.split(" ", 1)
                preis = self.get_preis(item)
                if preis is None:
                    print("Der Händler kann den Wert davon nicht einschätzen.")
                else:
                    print(f"Der Händler ist bereit, die dafür {preis} Gold zu zahlen.")
            elif al == "a":
                self.zeige_auslage()
            elif al == "z" or al == "w":
                return "z"
            elif al == "k":
                if ja_nein(mänx, "Wirklich kämpfen? "):
                    return "k"
            else:
                print("Nutze k [Anzahl] [Item] zum Kaufen, v zum Verkaufen, z für Zurück, a für eine Anzeige und "
                      "nur k zum Kämpfen, p [Item] um nach dem Preis zu fragen.")
    def plündern(self, mänx):
        """Gib den ganzen Inventarinhalt an mänx"""
        for item, (anzahl, _rest) in self.verkauft.items():
            mänx.inventar[item] += anzahl
        self.verkauft.clear()
        mänx.inventar["Gold"] += self.gold
        self.gold = 0