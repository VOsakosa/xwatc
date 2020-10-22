"""
Wegpunkte für JTGs Wegesystem.
Created on 17.10.2020
"""
import enum
import random
__author__ = "jasper"
import typing
from typing import List, Any, Optional as Opt
from xwatc.system import Mänx
from xwatc.dorf import MänxFkt


class Ereignis(enum.Enum):
    KAMPF = enum.auto()
    MORD = enum.auto()
    DIEBSTAHL = enum.auto()


class Context(typing.Protocol):
    def melde(self, mänx: Mänx, ereignis: Ereignis, data: Any) -> None:
        """Melde ein Ereignis an den Kontext"""


class Wegpunkt(Context, typing.Protocol):
    def get_nachbarn(self)->List[Wegpunkt]:
        return []


class MonsterChance:
    """Eine Möglichkeit eines Monsterzusammenstoßes."""

    def __init__(self, wahrscheinlichkeit: float, geschichte: MänxFkt) -> None:
        self.wkeit = wahrscheinlichkeit
        self.geschichte = geschichte

    def main(self, mänx: Mänx):
        # Hier in den Kampf einsteigen
        self.geschichte(mänx)


class Weg:
    """Ein Weg hat zwei Enden und dient dazu, die Länge der Reise darzustellen.
    Zwei Menschen auf dem Weg zählen als nicht benachbart."""
    def __init__(self, länge: float, p1: Wegpunkt, p2: Wegpunkt,
                 monster_tag: Opt[List[MonsterChance]] = None,
                 monster_nachts: Opt[List[MonsterChance]] = None):
        self.länge = länge
        self.p1 = p1
        self.p2 = p2
        self.monster_tag = monster_tag
        self.monster_nachts = monster_nachts

    def get_nachbarn(self) -> List[Wegpunkt]:
        return [self.p1, self.p2]

    def melde(self, mänx: Mänx, ereignis: Ereignis,
              data: Any) -> None:  # pylint: disable=unused-argument
        if ereignis == Ereignis.KAMPF:
            self.monster_check(mänx)
        # super().melde(mänx, ereignis, data)

    def monster_check(self, mänx: Mänx) -> bool:
        """Checkt, ob ein Monster getroffen wird.
        
        :return:
            True, wenn der Spieler sich entscheidet umzukehren.
        """
        if mänx.welt.is_nacht():
            ms = self.monster_nachts
        else:
            ms = self.monster_tag
        if ms:
            r = random.random()
            for mon in ms:
                r -= mon.wkeit
                if r < 0:
                    return mon.main(mänx)
        return False

    def main(self, mänx: Mänx, von: Wegpunkt) -> Wegpunkt:
        tagrest = mänx.welt.tag % 1.0
        if tagrest < 0.5 and tagrest + self.länge >= 0.5:
            if mänx.ja_nein("Du wirst nicht vor Ende der Nacht ankommen. "
                            "Willst du umkehren?"):
                return von
        # frage_nacht = False
        richtung = von == self.p1
        weg_rest = self.länge
        while weg_rest > 0:
            mänx.welt.tick(1/24)
            if self.monster_check(mänx):
                # umkehren
                richtung = not richtung
                weg_rest = self.länge - weg_rest
            if mänx.welt.is_nacht():
                if mänx.ja_nein("Willst du ruhen?"):
                    # TODO Monster beim Schlafen!
                    mänx.welt.nächster_tag()
            weg_rest -= 1/24
            

        if richtung:
            return self.p2
        else:
            return self.p1
