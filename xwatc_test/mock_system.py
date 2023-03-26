"""
Ein Mock für das Aus-/Eingabesystem, um Geschichten ordentlich testen zu können.

Created on 25.03.2023
"""
from attrs import define
from collections.abc import Sequence, Mapping
from typing import TypeVar
from xwatc import system
from xwatc.system import MenuOption, Mänx, Speicherpunkt
from attr import Factory
__author__ = "jasper"


@define
class ScriptEnde(Exception):
    """Besagt, dass die letzte Eingabe abgearbeitet wurde."""


@define
class UnpassendeEingabe(AssertionError):
    """Besagt, dass die Eingabe nicht zur Frage gepasst hat."""
    eingabe: str
    optionen: list[str]


T = TypeVar("T")


@define
class MockSystem:
    """Ausgaben über das Terminal"""
    terminal = True
    ausgaben: list[str] = Factory(list)
    eingaben: list[str] = Factory(list)

    def install(self) -> system.Mänx:
        system.ausgabe = self  # type: ignore
        return system.Mänx(self)

    def ein(self, txt: str):
        self.eingaben.append(txt)

    def pop_ausgaben(self) -> list[str]:
        ans = list(self.ausgaben)
        self.ausgaben.clear()
        return ans

    def menu(self,
             mänx: Mänx | None,
             optionen: list[MenuOption[T]],
             frage: str = "",
             gucken: Sequence[str] | None = None,
             versteckt: Mapping[str, T] | None = None,
             save: Speicherpunkt | None = None) -> T:
        """Bei Menu wird nur genau geantwortet.
        """
        if frage:
            self.ausgaben.append(frage.strip())
        if not self.eingaben:
            raise ScriptEnde()
        eingabe = self.eingaben.pop(0)
        for _label, opt, value in optionen:
            if opt == eingabe:
                return value
        if versteckt and eingabe in versteckt:
            return versteckt[eingabe]
        ok = [a[1] for a in optionen]
        if versteckt:
            ok.extend(versteckt.keys())
        raise UnpassendeEingabe(eingabe, ok)

    def minput(self, mänx: Mänx | None, frage: str, möglichkeiten=None, lower=True,
               save: Speicherpunkt | None = None) -> str:
        """Manipulierter Input
        Wenn möglichkeiten (in kleinbuchstaben) gegeben, dann muss die Antwort eine davon sein."""
        if frage:
            self.ausgaben.append(frage.strip())
        if not self.eingaben:
            raise ScriptEnde()
        eingabe = self.eingaben.pop(0)
        if lower:
            eingabe = eingabe.lower()
            möglichkeiten = [a.lower() for a in möglichkeiten]
        if not möglichkeiten or eingabe in möglichkeiten:
            return eingabe
        raise UnpassendeEingabe(eingabe, möglichkeiten)

    def mint(self, *text):
        """Printe und warte auf ein Enter."""
        self.ausgaben.append(" ".join(str(t) for t in text))

    def sprich(self, sprecher: str, text: str, warte: bool = False, wie: str = ""):
        if wie:
            sprecher += f"({wie})"
        self.ausgaben.append(f'{sprecher}: »{text}«')

    def malp(self, *text, sep=" ", end='\n', warte=False) -> None:
        """Angenehm zu lesender, langsamer Print."""
        self.ausgaben.append((sep.join(text) + end).strip())

    def ja_nein(self, mänx, frage,
                save: Speicherpunkt | None = None):
        """Ja-Nein-Frage"""
        ans = self.minput(
            mänx, frage, ["j", "ja", "n", "nein"], save=save).lower()
        return ans == "j" or ans == "ja"

    @staticmethod
    def kursiv(text: str) -> str:
        """Kursiv wird erstmal ignoriert."""
        return text
