"""
Created on 07.11.2020
"""
from __future__ import annotations
from typing import Union, Sequence, List
import xwatc
from xwatc.system import Mänx, Spielende
import enum
__author__ = "jasper"


Kämpfer = Union['MänxAlsKämpfer', 'xwatc.dorf.NSC']

class MänxAlsKämpfer:
    def __init__(self, mänx: Mänx):
        self.mänx = mänx
        self.seite = 1

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

    def wähle_attacke(self, kampf: Kampf):
        pass

    @property
    def tot(self):
        return self._tot

    @tot.setter
    def tot(self, ja: bool):
        self._tot = ja
        if ja:
            raise Spielende
        

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
                self._attacke_ausführen(teilnehmer.wähle_attacke(self))
    
    def neuer_teilnehmer(self, kämpfer: Kämpfer):
        self.teilnehmer.append(kämpfer)
    
    def _attacke_ausführen(self, attacke: Attacke):
        
            
