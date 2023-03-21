"""
Ein Händler ist ein spezieller NSC, der Kaufen und Verkaufen von Items erlaubt.
"""
from __future__ import annotations

from typing import (List, Optional as Opt, NewType, Dict, cast, Tuple,
                    Sequence)

from xwatc.dorf import NSC, NSCOptionen, Rückkehr, DialogErzeugerFn
from xwatc.system import Mänx, minput, ja_nein, get_classes, Inventar, malp,\
    Fortsetzung, ALLGEMEINE_PREISE, InventarBasis, Speicherpunkt, MenuOption
import re
from dataclasses import dataclass


Preis = int
Item = str
Klasse = str


class Händler(NSC):
    """Ein NSC, von dem du in einem Menü kaufen und verkaufen kannst."""

    def __init__(self,
                 name: str,
                 kauft: Opt[List[Klasse]],
                 verkauft: Dict[Item, Tuple[int, int]],
                 gold: int,
                 art="Händler",
                 direkt_handeln: bool = False,
                 startinventar: Opt[Inventar] = None,
                 dlg: Opt[DialogErzeugerFn] = None):
        """Neuer Händler namens *name*, der Sachen aus den Kategorien *kauft* kauft.
        *verkauft* ist das Inventar. *gold* ist die Anzahl von Gold."""
        super().__init__(name, art, dlg=dlg)
        self.kauft = kauft
        # Anzahl, Preis
        self.verkauft: Dict[Item, int] = {}
        for ware, (anzahl, preis) in verkauft.items():
            self.verkauft[ware] = preis
            self.inventar[ware] += anzahl
        if startinventar:
            for item, anzahl in startinventar.items():
                self.inventar[item] += anzahl
        self.gold = gold
        self.rückkauf = False
        self.direkt_handeln = direkt_handeln

    def kaufen(self, mänx: Mänx, name: str, anzahl: int = 1) -> str:
        """Mänx kauft von Händler"""
        if anzahl <= 0:
            return "Du musst eine positive Anzahl kaufen."
        elif name not in self.verkauft:
            return f"\"{name}\" hat {self.name} nicht."
        preis = self.verkauft[name] * anzahl
        if self.inventar[name] < anzahl:
            return f"Der Händler hat nicht genug {name}."
        elif mänx.gold < preis:
            return "Du hast nicht genug Geld dafür."
        else:
            self.inventar[name] -= anzahl
            self.gold += preis
            mänx.gold -= preis
            mänx.inventar[name] += anzahl
            return "Gekauft."

    def kann_kaufen(self, name: str):
        """Prüft, ob der Händler *name* ankauft."""
        return self.kauft is None or any(
            cls in self.kauft for cls in get_classes(name))

    def verkaufen(self, mänx: Mänx, name: str, preis: Preis, anzahl: int = 1) -> bool:
        """Mänx verkauft an Händler"""
        if self.kann_kaufen(name) and self.gold >= preis * anzahl:
            self.gold -= preis * anzahl
            mänx.gold += preis * anzahl
            mänx.inventar[name] -= anzahl
            self.inventar[name] += anzahl
            if self.rückkauf and name not in self.verkauft:
                self.verkauft[name] = preis + 1
            return True
        return False

    def get_preis(self, name: str) -> Opt[int]:
        """Berechne den Ankaufpreis für das Objekt name.
        :return: Preis in Gold, oder None, wenn nicht gekauft wird.
        """
        return ALLGEMEINE_PREISE.get(name)

    def _verkaufen(self, mänx, gegenstand, menge):
        """Versuch interaktiv, an den Händler zu verkaufen."""
        if menge <= 0:
            malp("Jetzt mal ernsthaft, gib eine positive Anzahl an.")
        elif not mänx.hat_item(gegenstand, menge):
            malp(
                f'Du hast nicht genug "{gegenstand}" zum verkaufen. Versuch "e".')
        elif not self.kann_kaufen(gegenstand):
            if self.kauft:
                malp("So etwas kauft der Händler nicht")
                malp("Der Händler kauft nur", ", ".join(self.kauft))
            else:
                malp("Der Händler verkauft nur.")

        else:
            preis = self.get_preis(gegenstand)
            if preis is None:
                malp("Der Händler kann dir dafür keinen Preis nennen")
            elif preis * menge >= mänx.inventar["Gold"]:
                malp("So viel kannst du dir nicht leisten")
            else:
                self.verkaufen(mänx, gegenstand, preis, menge)
                malp("Verkauft.")

    def zeige_auslage(self) -> None:
        """Printe die Auslage auf den Bildschirm."""
        etwas_da = False
        länge = max(len(a) for a in self.verkauft) + 1
        for item, preis in self.verkauft.items():
            anzahl = self.inventar[item]
            if anzahl:
                etwas_da = True
                malp(f"{item:<{länge}}{anzahl:04}x {preis:3} Gold")
        if not etwas_da:
            malp("Der Händler*in hat nichts mehr zu verkaufen")

    def vorstellen(self, mänx: Mänx) -> None:
        malp("Du stehst du vor dem Händler*in", self.name)
        if self.kauft is None:
            malp("Er kauft grundsätzlich alles")
        elif self.kauft:
            malp("Er kauft", ", ".join(self.kauft))
        self.zeige_auslage()

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        yield ("handeln", "handel", self.handeln)
        yield from super().optionen(mänx)

    def _main(self, mänx: Mänx):
        if self.direkt_handeln:
            self.handeln(mänx)
        else:
            super()._main(mänx)

    def handeln(self, mänx: Mänx) -> Rückkehr | Fortsetzung:
        """Lass Spieler mit Mänx handeln"""
        if mänx.ausgabe.terminal:
            mänx.tutorial("handel")
        menu = InventarMenu([
            InventarOption("kaufen", self),
            InventarOption("verkaufen", mänx),
            InventarOption("preis", self, menge=False),
            "auslage",
            "reden",
            "kämpfen",
            "zurück",  # oder w, z
        ], prompt="handel>", hilfe="Nutze k [Anzahl] [Item] zum Kaufen, v zum Verkaufen, "
            "z für Zurück, a für eine Anzeige und "
            "nur k zum Kämpfen, p [Item] um nach dem Preis zu fragen."
        )
        while True:
            a, gegenstand, menge = menu.main(mänx, save=self)
            al = a[0]
            if a == "kaufen":
                malp(self.kaufen(mänx, gegenstand, menge))
            elif al == "v":
                self._verkaufen(mänx, gegenstand, menge)
            elif al == "p":
                preis = self.get_preis(gegenstand)
                if preis is None:
                    malp("Der Händler kann den Wert davon nicht einschätzen.")
                else:
                    malp(
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
                assert False


@dataclass
class InventarOption:
    """Eine Option für InventarMenu."""
    name: str
    inventar: InventarBasis
    menge: bool = True
    allow_missing: bool = True


@dataclass
class InventarMenu():
    """Eine Verallgemeinerung des Handelsmenüs.

    Es gibt Befehle ohne Inventar und mit Inventar, mit und ohne Menge.
    """
    optionen: Sequence[str | InventarOption]
    prompt: str
    hilfe: str

    def main(self, mänx: Mänx, save: Speicherpunkt) -> tuple[str, str, int]:
        """Run the option.

        :return: the option name, the item and the amount
        """
        while True:
            # Im Terminal wie Kommandozeile
            if mänx.ausgabe.terminal:
                a: str = mänx.minput(self.prompt, lower=False, save=save)
            else:
                # Ansonsten mit schrittweiser Auswahl
                mgn: list[MenuOption[str]] = []
                for opt in self.optionen:
                    if isinstance(opt, InventarOption):
                        mgn.append((opt.name, opt.name.lower(), opt.name))
                    else:
                        mgn.append((opt, opt.lower(), opt))
                a = mänx.menu(mgn, save=save)
            args = a.split()
            if not args:
                continue
            for option in self.optionen:
                if isinstance(option, str) and option.startswith(args[0]):
                    if len(args) > 1:
                        malp("Die restlichen Argumente werden ignoriert.")
                    return option, "", 0
                elif isinstance(option, InventarOption) and option.name.startswith(args[0]):
                    while len(args) == 1:
                        args.extend(mänx.minput(
                            "Welches Item?", lower=False).split())
                    if option.menge and re.fullmatch("[0-9]+", args[-1]):
                        anzahl = int(args.pop())
                    else:
                        anzahl = 1
                    item = " ".join(args[1:])
                    return option.name, item, anzahl
            else:
                malp(self.hilfe)
