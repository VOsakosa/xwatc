"""
Kampf-vorlagen
"""
from __future__ import annotations
from typing import Optional as Opt, cast
from xwatc.system import Mänx
from xwatc.dorf import Dialog

class ausgerüstet:
    """Prüft, ob der Mänx eine Waffe ausgerüstet hat."""
    def __init__(self, *waffe: str, klasse: Opt[str] = None):
        if not (waffe or klasse):
            raise TypeError("Waffe oder Klasse müssen angegeben werden.")
        elif waffe and klasse:
            raise TypeError("Waffe und Klasse können nicht beide gegeben werden.")
        self.waffe = waffe
        self.klasse: str = cast(str, klasse)
    def __call__(self, __, mänx: Mänx) -> bool:
        if self.waffe:
            return any(mänx.hat_item(waffe) for waffe in self.waffe)
        else:
            return bool(mänx.hat_klasse(self.klasse))


DORFBEWOHNER_KAMPF: list[Dialog] = [
    
]

