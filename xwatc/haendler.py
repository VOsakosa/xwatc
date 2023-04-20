"""
Ein Händler ist ein spezieller NSC, der Kaufen und Verkaufen von Items erlaubt.
"""
from __future__ import annotations

from attrs import define
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import re

from xwatc.nsc import Rückkehr, Zeitpunkt, Dialog, StoryChar, NSC
from xwatc.system import (_, Mänx, get_classes, malp, Fortsetzung,
                          ITEMVERZEICHNIS, get_preise, Speicherpunkt, MenuOption)
import typing_extensions


Preis = int
Item = str
Klasse = str


def mache_händler(
    nsc: StoryChar, verkauft: Mapping[Item, tuple[int, Preis]],
    kauft: Sequence[Klasse], gold: int = 0, direkt_handeln: bool = False,
        aufpreis: float = 1.05, rückkauf: bool = False
) -> Dialog:
    """Füge einem NSC die nötigen Funktionen hinzu, um ihn zum Händler zu machen,
    einem NSC, von dem du in einem Menü kaufen und verkaufen kannst.

    :param direkt_handeln: Fange an zu handeln, noch bevor r,k,f gezeigt wird.
    """
    new_inventar = defaultdict[Item, Preis](int)
    for item, anzahl in nsc.startinventar.items():
        new_inventar[item] += anzahl
    for item, (anzahl, _preis) in verkauft.items():
        new_inventar[item] += anzahl
    new_inventar["Gold"] += gold
    nsc.startinventar = new_inventar

    handel = HandelsFn(
        {item: preis for item, (__, preis) in verkauft.items()}, kauft, aufpreis, rückkauf)
    return nsc.dialog("h", "Handeln", handel, min_freundlich=0,
                      zeitpunkt=Zeitpunkt.Vorstellen if direkt_handeln else Zeitpunkt.Option)


KaufenHook = Callable[[NSC, Mänx, Item, Preis, int], None]


@define
class HandelsFn:
    """Die Dialog-Funktion für Händler."""
    verkauft: dict[Item, Preis]
    kauft: Sequence[Klasse]
    aufpreis: float
    rückkauf: bool
    _kaufen_hook: KaufenHook | None = None
    _verkaufen_hook: KaufenHook | None = None

    def kaufen(self, nsc: NSC, mänx: Mänx, name: str, anzahl: int = 1) -> str:
        """Mänx kauft von Händler"""
        if anzahl <= 0:
            return "Du musst eine positive Anzahl kaufen."
        elif name not in self.verkauft:
            return f"\"{name}\" hat {nsc.name} nicht."
        preis = self.verkauft[name] * anzahl
        if nsc.inventar[name] < anzahl:
            return f"Der Händler hat nicht genug {name}."
        elif mänx.gold < preis:
            return "Du hast nicht genug Geld dafür."
        else:
            nsc.inventar[name] -= anzahl
            nsc.inventar["Gold"] += preis
            mänx.gold -= preis
            mänx.inventar[name] += anzahl
            if self._kaufen_hook:
                self._kaufen_hook(nsc, mänx, name, preis, anzahl)
            return "Gekauft."

    def kann_kaufen(self, name: str) -> bool:
        """Prüft, ob der Händler *name* ankauft."""
        try:
            return self.kauft is None or any(
                cls in self.kauft for cls in get_classes(name))
        except KeyError:
            return False

    def verkaufen(self, nsc: NSC, mänx: Mänx, name: str, preis: Preis, anzahl: int = 1) -> bool:
        """Mänx verkauft an Händler"""
        if self.kann_kaufen(name) and nsc.inventar["Gold"] >= preis * anzahl:
            nsc.inventar["Gold"] -= preis * anzahl
            mänx.gold += preis * anzahl
            mänx.inventar[name] -= anzahl
            nsc.inventar[name] += anzahl
            if self.rückkauf and name not in self.verkauft:
                self.verkauft[name] = (preis * self.aufpreis).__ceil__()
            if self._verkaufen_hook:
                self._verkaufen_hook(nsc, mänx, name, preis, anzahl)
            return True
        return False
    
    def get_verkauf_inventar(self, nsc: NSC) -> Mapping[str, int]:
        return {item: anzahl for item, anzahl in nsc.inventar.items() if item in self.verkauft}
    
    def get_ankauf_inventar(self, mänx: Mänx) -> Mapping[str, int]:
        return {item: anzahl for item, anzahl in mänx.inventar.items() if self.kann_kaufen(item)}

    def get_preis(self, name: str) -> int | None:
        """Berechne den Ankaufpreis für das Objekt name.
        :return: Preis in Gold, oder None, wenn nicht gekauft wird.
        """
        if name in ITEMVERZEICHNIS:
            return (get_preise(name) * self.aufpreis).__ceil__()
        return None

    def _verkaufen(self, nsc: NSC, mänx: Mänx, gegenstand: Item, menge: int) -> None:
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
            elif preis * menge > nsc.gold:
                malp("Der Händler kann dir nicht so viel davon abkaufen.")
            else:
                self.verkaufen(nsc, mänx, gegenstand, preis, menge)
                malp("Verkauft.")

    def zeige_auslage(self, nsc: NSC) -> None:
        """Printe die Auslage auf den Bildschirm."""
        etwas_da = False
        länge = max((len(a) for a in self.verkauft), default=0) + 1
        for item, preis in self.verkauft.items():
            anzahl = nsc.inventar[item]
            if anzahl:
                etwas_da = True
                malp(f"{item:<{länge}}{anzahl:04}x {preis:3} Gold")
        if not etwas_da:
            malp("Der Händler*in hat nichts mehr zu verkaufen")

    def __call__(self, nsc: NSC, mänx: Mänx) -> Rückkehr | Fortsetzung:
        """Lass Spieler mit Mänx handeln"""
        self.zeige_auslage(nsc)
        if mänx.ausgabe.terminal:
            mänx.tutorial("handel")
        menu = InventarMenu([
            InventarOption("kaufen", self.get_verkauf_inventar(nsc)),
            InventarOption("verkaufen", self.get_ankauf_inventar(mänx)),
            InventarOption("preis", self.get_ankauf_inventar(mänx), menge=False),
            "auslage",
            "reden",
            "kämpfen",
            "zurück",  # oder w, z
        ], prompt="handel>", hilfe="Nutze k [Anzahl] [Item] zum Kaufen, v zum Verkaufen, "
            "z für Zurück, a für eine Anzeige und "
            "nur k zum Kämpfen, p [Item] um nach dem Preis zu fragen."
        )
        while True:
            befehl = menu.main(mänx, save=nsc)
            a = befehl.name
            gegenstand = befehl.item
            al = a[0]
            if a == "kaufen":
                malp(self.kaufen(nsc, mänx, gegenstand, befehl.menge))
            elif al == "v":
                self._verkaufen(nsc, mänx, gegenstand, befehl.menge)
            elif al == "p":
                preis = self.get_preis(gegenstand)
                if preis is None:
                    malp("Der Händler kann den Wert davon nicht einschätzen.")
                else:
                    malp(
                        f"Der Händler ist bereit, dir dafür {preis} Gold zu zahlen.")
            elif al == "a":
                self.zeige_auslage(nsc)
            elif al == "z" or al == "w" or al == "f":
                return Rückkehr.ZURÜCK
            elif al == "r":
                ans = nsc.reden(mänx)
                if ans != Rückkehr.ZURÜCK:
                    return ans
            elif a == "kämpfen":
                # Startet den Standard-Kampf, falls verfügbar.
                nsc.kampf(mänx)
                return Rückkehr.ZURÜCK
            else:
                assert False, f"Illegale Rückgabe {a}"

    def kaufen_hook(self, fn: KaufenHook) -> KaufenHook:
        self._kaufen_hook = fn
        return fn

    def verkaufen_hook(self, fn: KaufenHook) -> KaufenHook:
        self._verkaufen_hook = fn
        return fn


@dataclass(eq=False)
class InventarOption:
    """Eine Option für InventarMenu."""
    name: str
    inventar: Mapping[str, int] | None
    menge: bool = True  # Ob der Befehl eine Menge nimmt
    allow_missing: bool = True

    def __str__(self) -> str:
        return self.name


@dataclass(eq=True)
class GewählteOption:
    """Eine ausgewählte Option beim InventarMenu, bestehend aus einem Befehl und möglicherweise
    einem Item und einer Anzahl.
    """
    name: str
    item: str = ""
    menge: int = 0


@dataclass(eq=False)
class InventarMenu():
    """Eine Verallgemeinerung des Handelsmenüs.

    Es gibt Befehle ohne Inventar und mit Inventar, mit und ohne Menge.
    """
    optionen: Sequence[str | InventarOption]
    prompt: str
    hilfe: str

    def main(self, mänx: Mänx, save: Speicherpunkt) -> GewählteOption:
        """Run the option.

        :return: the option name, the item and the amount
        """
        assert self.optionen
        while True:
            # Im Terminal wie Kommandozeile
            if mänx.ausgabe.terminal:
                text_input: str = mänx.minput(self.prompt, lower=False, save=save)
            else:
                # Ansonsten mit schrittweiser Auswahl
                mgn: list[MenuOption[str]] = []
                for opt in self.optionen:
                    if isinstance(opt, InventarOption):
                        mgn.append((opt.name, opt.name.lower(), opt.name))
                    else:
                        mgn.append((opt, opt.lower(), opt))
                text_input = mänx.menu(mgn, save=save)
            if not text_input:
                continue
            cmd, *args = text_input.split()
            for option in self.optionen:
                if str(option) == cmd:
                    break
            else:
                passende_optionen = [
                    option for option in self.optionen if str(option).startswith(cmd)]
                if len(passende_optionen) == 1:
                    option = passende_optionen[0]
                else:
                    malp(self.hilfe)
                    continue

            if isinstance(option, str):
                if args:
                    malp("Die restlichen Argumente werden ignoriert.")
                return GewählteOption(option)
            elif isinstance(option, InventarOption):
                if not args:
                    anzahl, item = self.wähle_item(mänx, option)
                    if not item:
                        continue
                elif option.menge and re.fullmatch("[0-9]+", args[0]):
                    anzahl = int(args[0])
                    item = " ".join(args[1:])
                else:
                    anzahl = 1
                    item = " ".join(args)
                return GewählteOption(option.name, item, anzahl)
            else:
                typing_extensions.assert_never(option)

    def wähle_item(self, mänx: Mänx, option: InventarOption) -> tuple[int, str | None]:
        """Lasse den Spieler das Item und eine Anzahl für eine InventarOption wählen.

        :return: Die Anzahl und der Name des Items, oder None wenn der Spieler abbricht.
        """
        if mänx.ausgabe.terminal or not option.inventar:
            text = mänx.minput(_("Welches Item?"), lower=False)
            if not text:
                return 0, None
            if match_ := re.match("([0-9]+)\\s+(.*)", text):
                return int(match_.group(1)), match_.group(2)
            return 1, text
        else:
            malp("Welches Item?")
            item = mänx.menu([("mehrere", "", None),
                             *((item, item, item) for item in option.inventar)])
            if item is None:
                item = mänx.menu([(item, item, item) for item in option.inventar])
                anzahl_str = mänx.minput(_("Wie viele?"))
                try:
                    return int(anzahl_str), item
                except ValueError:
                    malp("Das ist keine Zahl. Abbruch")
                    return 0, None
            return 1, item
