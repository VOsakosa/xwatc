"""
Ein Mock für das Aus-/Eingabesystem, um Geschichten ordentlich testen zu können.

>>> mänx = MockSystem().install(); mänx
Mänx(...)

Created on 25.03.2023
"""
import re
from attrs import define
from collections.abc import Sequence
from typing import TypeVar
import unittest
from xwatc import system
from xwatc.system import Menu, Mänx, Speicherpunkt, MänxFkt
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
    """Stellt ein Test-System bereit, dass die Aus- und Eingaben von Xwatc mockt.

    >>> system = MockSystem()
    >>> mänx = system.install()
    >>> system.ein("ja")
    >>> mänx.ja_nein("Willst du mich heiraten?")
    True
    >>> system.aus_regex(r"Willst du mich .*\?")
    >>> mänx.ja_nein("Wirklich?")
    Traceback (most recent call last):
    xwatc_test.mock_system.ScriptEnde
    """
    terminal: bool = True
    ausgaben: list[str] = Factory(list)
    eingaben: list[str] = Factory(list)

    def install(self) -> system.Mänx:
        system.ausgabe = self  # type: ignore
        return system.Mänx(self)  # type: ignore

    def ein(self, txt: str) -> None:
        self.eingaben.append(txt)

    def aus(self, text: str) -> None:
        if not self.ausgaben:
            raise AssertionError(f"Es gab keine Ausgabe. Erwartet: {text}")
        ausgabe = self.ausgaben.pop(0)
        if ausgabe != text:
            raise AssertionError(f"Ausgabe {ausgabe!r} ist nicht {text}.")

    def aus_regex(self, regex: str) -> None:
        if not self.ausgaben:
            raise AssertionError(f"Es gab keine Ausgabe. Erwartet: {regex}")
        ausgabe = self.ausgaben.pop(0)
        if not re.fullmatch(regex, ausgabe):
            raise AssertionError(f"Ausgabe {ausgabe!r} passt nicht auf {regex}.")

    def pop_ausgaben(self) -> list[str]:
        ans = list(self.ausgaben)
        self.ausgaben.clear()
        return ans

    def test_mänx_fn(self, case_: unittest.TestCase, mänx_fn: MänxFkt[T],
                     eingaben: Sequence[str], ausgaben: Sequence[str],
                     allow_script_ende: bool = False) -> T | None:
        """Teste eine MänxFkt gegen eine Reihe von eingaben."""
        self.eingaben.extend(eingaben)
        ans = None
        try:
            ans = mänx_fn(self.install())
        except ScriptEnde:
            if not allow_script_ende:
                raise
        case_.assertListEqual(self.pop_ausgaben(), [*ausgaben])
        return ans

    def menu(self,
             mänx: Mänx,
             menu: Menu[T],
             save: 'Speicherpunkt | None' = None) -> T:
        """Bei Menu wird nur genau geantwortet.
        """
        if menu.frage:
            self.ausgaben.append(menu.frage.strip())
        if not self.eingaben:
            raise ScriptEnde()
        eingabe = self.eingaben.pop(0)
        for _label, opt, value in menu.optionen:
            if opt == eingabe:
                return value
        if eingabe in menu.versteckt:
            return menu.versteckt[eingabe]
        ok = [a[1] for a in menu.optionen]
        ok.extend(menu.versteckt.keys())
        raise UnpassendeEingabe(eingabe, ok)

    def minput(self, mänx: Mänx | None, frage: str, möglichkeiten=None, lower=True,
               save: 'Speicherpunkt | None' = None) -> str:
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
                save: 'Speicherpunkt | None' = None):
        """Ja-Nein-Frage"""
        ans = self.minput(
            mänx, frage, ["j", "ja", "n", "nein"], save=save).lower()
        return ans == "j" or ans == "ja"

    @staticmethod
    def kursiv(text: str) -> str:
        """Kursiv wird erstmal ignoriert."""
        return text
