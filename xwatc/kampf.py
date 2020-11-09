"""
Created on 07.11.2020
"""
from __future__ import annotations
from typing import Union, Sequence, List, Tuple
import xwatc
from xwatc.system import Mänx, Spielende, malp
import enum
__author__ = "jasper"


Kämpfer = Union['MänxAlsKämpfer', 'NSCKämpfer']


class MänxAlsKämpfer:
    def __init__(self, mänx: Mänx):
        self.mänx = mänx
        self.seite = 1
        self.name = "Du"

    def attacken(self) -> Sequence[Attacke]:
        ans = []
        mänx = self.mänx
        if not mänx.hat_klasse("Waffe"):
            ans.append(Attacke("Faustschlag", 5))
        elif mänx.hat_klasse("legendäre Waffe"):
            ans.append(Attacke("normale Attacke", 50))
        else:
            ans.append(Attacke("normale Attacke", 40))
        return ans

    def wähle_attacke(self, kampf: Kampf) -> Tuple[Attacke, Sequence['Kämpfer']]:
        att = self.mänx.menu([(a.name, a.name.lower(), a) for a in self.attacken()],
                             frage="kampf>")
        gegner = [a for a in kampf.teilnehmer if a.seite != self.seite]
        if att.zieltyp == Zieltyp.Einzel:
            gegner = [self.mänx.menu([(a.name, a.name.lower(), a) for a in gegner],
                                     frage="Wen?")]
        return att, gegner

    @property
    def tot(self):
        return self._tot

    @tot.setter
    def tot(self, ja: bool):
        self._tot = ja
        if ja:
            raise Spielende

    def schade(self, anzahl: int):
        self.mänx.lebenspunkte -= anzahl
        if self.mänx.lebenspunkte < 0:
            self.tot = True


class NSCKämpfer:
    def __init__(self, basis: xwatc.dorf.NSC, seite: int) -> None:
        self.basis = basis
        self.lebenspunkte = basis.max_lp
        self.max_lp = basis.max_lp
        self.seite = seite

    @property
    def name(self):
        return self.basis.name

    @property
    def tot(self):
        return self.basis.tot

    @tot.setter
    def tot(self, ja: bool):
        self.basis.tot = ja

    def schade(self, anzahl: int):
        if anzahl < 0:
            self.lebenspunkte = min(self.max_lp, self.lebenspunkte - anzahl)
        else:
            self.lebenspunkte -= anzahl
            if self.lebenspunkte < 0:
                self.tot = True


class Zieltyp(enum.Enum):
    Alle = enum.auto()
    Einzel = enum.auto()


class Attacke:
    """Eine Art von Angriff, die ein Kämpfer besitzt."""
    name: str  # z.B. normaler Angriff
    zieltyp: Zieltyp

    def __init__(self, name: str, schaden: int):
        self.name = name
        self.schaden = schaden
        self.zieltyp = Zieltyp.Einzel

    def text(self, angreifer, verteidiger_liste: Sequence[Kämpfer]):
        verteidiger = [(a.name if a.name != "Du" else "dich")
                       for a in verteidiger_liste]
        if len(verteidiger) == 1:
            vers, = verteidiger
        else:
            vers = ", ".join(verteidiger[:-1]) + " und " + verteidiger[-1]

        return (f"{angreifer.name} setzt {self.name} gegen "
                f"{vers} ein.")


class Kampf:
    def __init__(self, mänx: Mänx, teilnehmer: Sequence['Kämpfer']):
        self.teilnehmer: List['Kämpfer'] = [MänxAlsKämpfer(mänx)]
        self.teilnehmer.extend(teilnehmer)
        self.runde = 0

    def main(self):
        self.runde = 0
        while len({a.seite for a in self.teilnehmer}) > 2:
            self.runde += 1
            for teilnehmer in self.teilnehmer[:]:
                if teilnehmer.tot:
                    pass
                self._attacke_ausführen(
                    teilnehmer, *teilnehmer.wähle_attacke(self))

    def neuer_teilnehmer(self, kämpfer: Kämpfer):
        self.teilnehmer.append(kämpfer)

    def _attacke_ausführen(self, angreifer: Kämpfer,
                           attacke: Attacke, ziele: Sequence['Kämpfer']):
        for ziel in ziele:
            ziel.schade(attacke.schaden)
        malp(attacke.text(angreifer, ziele))
