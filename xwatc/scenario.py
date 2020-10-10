from typing import List, Optional as Op
import os.path

if __name__ == "__main__":
    import sys
    sys.path.append("..")

from xwatc import system

SPIELER = "Y"
TOD = " Tod"
SCENARIO_ORT = os.path.join(os.path.dirname(__file__), "../scenarios")

class ScenarioEnde:
    def __init__(self, tot=False, nächstes=None, ergebnis=None):
        self.tot = tot
        self.nächstes = nächstes
        self.ergebnis = ergebnis

class Weg:
    def __init__(self, wird_zu=None, feld=None):
        self.wird_zu = wird_zu
        self.feld = feld

from xwatc import scenario_reden
from xwatc import scenario_kämpfen
from xwatc import scenario_feld

class Scenario:
    def __init__(self, name, feld: List[List[str]], objekte: List[List[Op[str]]]):
        self.name = name
        self.anzeigename = name
        self.feld = feld
        self.objekte = objekte
        self.spielerpos = None
        höhe = len(feld[0])
        assert len(feld) == len(objekte)
        for reihe in feld:
            assert len(reihe) == höhe
        for y, reihe in enumerate(objekte):
            assert len(reihe) == höhe
            for x, obj in enumerate(reihe):
                if obj == SPIELER:
                    assert not self.spielerpos
                    self.spielerpos = [y, x]
        assert self.spielerpos

    @classmethod
    def laden(cls, pfad) -> "Scenario":
        with open(pfad, "r") as p:
            name = p.readline()[:-1]
            feld = []
            lines = iter(p.readlines())
            for line in lines:
                if line.endswith("\n"):
                    line = line[:-1]
                if not line:
                    break
                feld.append(line.split(","))
            objekte = []
            for line in lines:
                if line.endswith("\n"):
                    line = line[:-1]
                if not line:
                    break
                objekte.append([i if i.strip() else None for i in line.split(",")])
            print(repr(name), feld, objekte)
        return cls(name, feld, objekte)

    def print(self):
        # print("\1b[2J")
        print(self.anzeigename)
        for y, reihe in enumerate(self.feld):
            for x, feld in enumerate(reihe):
                obj = self.objekte[y][x]
                if obj:
                    print(obj[0], end="")
                elif feld:
                    print(feld[0], end="")
            print()

    def bewege_spieler(self, mänx, y, x) -> Op[ScenarioEnde]:
        """Bewege den Spieler um y und x relativ"""
        ys, xs = self.spielerpos
        yn, xn = (ys+y) % len(self.feld), (xs+x) % len(self.feld[0])
        obj = self.objekte[yn][xn]
        if obj:
            ans = self.treffe_objekt(mänx, obj)
            if isinstance(ans, Weg):
                self.objekte[yn][xn] = ans.wird_zu
                if ans.feld:
                    self.feld[yn][xn] = ans.feld
                return None
            return ans
        feld = self.feld[yn][xn]
        if feld == TOD:
            return ScenarioEnde(tot=True)
        elif feld != " ":
            treff = scenario_feld.treffe(mänx, feld, self)
            if treff != None:
                return treff
        self.objekte[yn][xn] = SPIELER
        self.objekte[ys][xs] = None
        self.spielerpos= [yn, xn]
        return None

    def treffe_objekt(self, mänx, obj):
        a = mänx.minput(f"Willst du mit {obj} reden oder kämpfen?[r/k/z]", ["r","k","z"])
        if a == "r":
            return scenario_reden.reden(mänx, obj, self)
        elif a == "z":
            return None
        else:
            return scenario_kämpfen.kämpfen(mänx, obj, self)

    def einleiten(self, mänx) -> ScenarioEnde:
        ans = None
        while not ans:
            self.print()
            arg = mänx.minput(">")
            if arg == "w":
                ans = self.bewege_spieler(mänx,-1,0)
            elif arg == "d":
                ans = self.bewege_spieler(mänx, 0,1)
            elif arg == "s":
                ans = self.bewege_spieler(mänx, 1,0)
            elif arg == "a":
                ans = self.bewege_spieler(mänx, 0,-1)
            else:
                print("Hä? Was is'n 'n", repr(arg))
        return ans
    
def lade_scenario(mänx, path):
    """Beispiel lade_scenario(mänx, "s1.txt")"""
    ans = ScenarioEnde(nächstes=path)
    while ans:
        if not path.endswith(".txt"):
            path += ".txt"
        path = os.path.join(SCENARIO_ORT, path)
        sc = Scenario.laden(path)
        ans = sc.einleiten(mänx)
        if ans.tot:
            raise system.Spielende()
        elif ans.ergebnis:
            return ans.ergebnis
    return None

if __name__ == '__main__':
    # objekte = [[None]*3 for i in range(4)]
    # feld = [[" "]*3 for i in range(4)]
    # objekte[1][2] = "Y"
    #feld[0][2] = TOD
    # objekte[1][1] = "B"
    # scenario = Scenario("Hallo", feld, objekte)
    scenario = Scenario.laden("../scenarios/s1.txt")
    ergebnis = scenario.einleiten(system.Mänx())
    if ergebnis.tot:
        print("Du bist tot")
        
        
        
        
        