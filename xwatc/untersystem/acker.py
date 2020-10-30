"""
Anbau von Pflanzen.
Created on 29.10.2020
"""
from typing import Optional as Opt
from xwatc.system import Inventar, malp, Mänx
__author__ = "jasper"

class Wildpflanze:
    """Eine Pflanze, die immer nachwächst, auch wenn man nicht nachpflanzt."""
    def __init__(self, reife: float, beute: Inventar, text: str) -> None:
        self.reife = reife
        self.beute = beute
        self.text = text
        self.zeit: Opt[float] = None
    
    def main(self, mänx: Mänx):
        if self.zeit is None or mänx.welt.tag - self.zeit >= self.reife:
            malp(self.text)
            for item, anzahl in self.beute.items():
                mänx.erhalte(item, anzahl)
            mänx.welt.tick(1/120)
            self.zeit = mänx.welt.tag