"""
Created on 07.11.2020
"""
from __future__ import annotations
from typing import List, Sequence
from xwatc.system import Mänx
import enum
__author__ = "jasper"

class MänxAlsKämpfer:
    def __init__(self, mänx: Mänx):
        self.mänx = mänx
    
    def attacken(self) -> Sequence[Attacke]:
        ans = []
        if not mänx.hat_klasse("Waffe"):
            ans.append(Attacke("Faustschlag"))
        elif mänx.hat_klasse("legendäre Waffe"):
            ans.append(Attacke("normale Attacke"))
        else:
            ans.append(Attacke("normale Attacke"))
        return ans

    def wähle_attacke(self, kampf: Kampf):
        pass

class Zieltyp(enum.Enum):
    Alle = enum.auto()
    Einzel = enum.auto()

class Attacke:
    """Eine Art von Angriff, die ein Kämpfer besitzt."""
    name: str  # z.B. normaler Angriff
    zieltyp: Zieltyp

class Kampf:
    def __init__(self, mänx: Mänx, teilnehmer: Sequence['Kämpfer']):
        self.teilnehmer = [MänxAlsKämpfer(mänx)]
        self.teilnehmer.extend(teilnehmer)