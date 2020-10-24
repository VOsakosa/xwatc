from typing import List, Optional as Op, NewType, Dict, cast, Tuple

from xwatc.dorf import NSC, NSCOptionen, Rückkehr
from xwatc.system import Mänx, minput, ja_nein, get_class

ALLGEMEINE_PREISE = {
    "Speer": 50,
    "Hering": 5,
    "Sardine": 5,
    "Gänseblümchen": 3,
    "Löwenzahn": 2,
    "Distelblüte": 10,
    "Rose": 20,
    "Aorenblume": 80,
    "Atctenrose": 350
    
}
Preis = NewType("Preis", int)
Item = str
Klasse = str


class Händler(NSC):
    def __init__(self, name, kauft: Op[List[Klasse]],
                 verkauft: Dict[Item, Tuple[int, int]], gold: int,
                 art="Händler", direkt_handeln: bool = False):
        """Neuer Händler namens *name*, der Sachen aus den Kategorien *kauft* kauft.
        *verkauft* ist das Inventar. *gold* ist die Anzahl von Gold."""
        super().__init__(name, art)
        self.kauft = kauft
        # Anzahl, Preis
        self.verkauft: Dict[Item, int] = {}
        for ware, (anzahl, preis) in verkauft.items():
            self.verkauft[ware] = Preis(preis)
            self.inventar[ware] += anzahl
        self.gold = gold
        self.rückkauf = False
        self.direkt_handeln = direkt_handeln

    def kaufen(self, mänx: Mänx, name: str, anzahl: int=1) -> bool:
        """Mänx kauft von Händler"""
        if name not in self.verkauft:
            return False
        preis = self.verkauft[name] * anzahl
        if self.inventar[name] >= anzahl and mänx.gold >= preis:
            self.inventar[name] -= anzahl
            self.gold += preis
            mänx.gold -= preis
            mänx.inventar[name] += anzahl
            return True
        return False

    def kann_kaufen(self, name: str):
        """Prüft, ob der Händler *name* ankauft."""
        return self.kauft is None or get_class(name) in self.kauft

    def verkaufen(self, mänx: Mänx, name: str, preis: Preis, anzahl: int = 1) -> bool:
        """Mänx verkauft an Händler"""
        if self.kann_kaufen(name) and self.gold >= preis * anzahl:
            self.gold -= preis * anzahl
            mänx.gold += preis * anzahl
            mänx.inventar[name] -= anzahl
            self.inventar[name] += anzahl
            if self.rückkauf and name not in self.verkauft:
                self.verkauft[name] = cast(Preis, preis + 1)
            return True
        return False

    def get_preis(self, name: str) -> Op[int]:
        """Berechne den Ankaufpreis für das Objekt name.
        :return: Preis in Gold, oder None, wenn nicht gekauft wird.
        """
        return ALLGEMEINE_PREISE.get(name)

    def _verkaufen(self, mänx, gegenstand, menge):
        """Versuch interaktiv, an den Händler zu verkaufen."""
        if menge <= 0:
            print("Jetzt mal ernsthaft, gib eine positive Anzahl an.")
        elif not mänx.hat_item(gegenstand, menge):
            print(
                f'Du hast nicht genug "{gegenstand}" zum verkaufen. Versuch "e".')
        elif not self.kann_kaufen(gegenstand):
            if self.kauft:
                print("So etwas kauft der Händler nicht")
                print("Der Händler kauft nur", ", ".join(self.kauft))
            else:
                print("Der Händler verkauft nur.")

        else:
            preis = self.get_preis(gegenstand)
            if preis is None:
                print("Der Händler kann dir dafür keinen Preis nennen")
            elif preis * menge >= mänx.inventar["Gold"]:
                print("So viel kannst du dir nicht leisten")
            else:
                self.verkaufen(mänx, gegenstand, preis, menge)
                print("Verkauft.")

    def zeige_auslage(self) -> None:
        """Printe die Auslage auf den Bildschirm."""
        if self.verkauft:
            länge = max(len(a) for a in self.verkauft) + 1
            for item, preis in self.verkauft.items():
                anzahl = self.inventar[item]
                if anzahl:
                    print(f"{item:<{länge}}{anzahl:04}x {preis:3} Gold")
        else:
            print("Der Händler*in hat nichts mehr zu verkaufen")

    def vorstellen(self, mänx: Mänx) -> None:
        print("Du stehst du vor dem Händler*in", self.name)
        if self.kauft is None:
            print("Er kauft grundsätzlich alles")
        elif self.kauft:
            print("Er kauft", ", ".join(self.kauft))
        self.zeige_auslage()

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        yield ("handeln", "handel", self.handeln)
        yield from super().optionen(mänx)

    def _main(self, mänx: Mänx):
        if self.direkt_handeln:
            self.handeln(mänx)
        else:
            super()._main(mänx)

    def handeln(self, mänx: Mänx) -> Rückkehr:
        """Lass Spieler mit Mänx handeln"""
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
                    if len(kauft) == 2:
                        menge = 1
                        gegenstand = kauft[1]
                    else:
                        menge = int(kauft[1])
                        gegenstand = kauft[2]
                except (ValueError, IndexError):
                    print("Syntax: v [anzahl]? [gegenstand]")
                    print("Bsp: v 12 Augapfel")
                else:
                    self._verkaufen(mänx, gegenstand, menge)
            elif al.startswith("p ") or al.startswith("preis "):
                _, item = a.split(" ", 1)
                preis = self.get_preis(item)
                if preis is None:
                    print("Der Händler kann den Wert davon nicht einschätzen.")
                else:
                    print(
                        f"Der Händler ist bereit, dir dafür {preis} Gold zu zahlen.")
            elif al == "a":
                self.zeige_auslage()
            elif al == "z" or al == "w" or al == "f":
                return Rückkehr.ZURÜCK
            elif al == "k":
                if ja_nein(mänx, "Wirklich kämpfen? "):
                    self.kampf(mänx)
                    return Rückkehr.VERLASSEN
            elif al == "r":
                ans = self.reden(mänx)
                if ans != Rückkehr.ZURÜCK:
                    return ans
            else:
                print("Nutze k [Anzahl] [Item] zum Kaufen, v zum Verkaufen, "
                      "z für Zurück, a für eine Anzeige und "
                      "nur k zum Kämpfen, p [Item] um nach dem Preis zu fragen.")
