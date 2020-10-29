from typing import List, Optional as Op, Union, NewType, Dict
import os.path
from xwatc.system import Mänx
import sys

if __name__ == "__main__":
    sys.path.append("..")

from xwatc import system

SCENARIO_ORT = os.path.join(os.path.dirname(__file__), "../scenarios")


def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise. 
    Taken from https://github.com/django/django/blob/master/django/core/management/color.py
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty


ERLAUBT_FARBEN = supports_color()
FARBEN = {
    "gn": "32",
    "gu": "37",
    "bu": "34",
    "gb": "1;33",
    "bn": "33",
}
_SpielerTyp = NewType("_SpielerTyp", object)
Spieler = _SpielerTyp(object())


class ScenarioEnde:
    def __init__(self, tot=False, nächstes=None, ergebnis=None):
        self.tot = tot
        self.nächstes = nächstes
        self.ergebnis = ergebnis


class Weg:
    def __init__(self, wird_zu=None, feld=None):
        self.wird_zu = wird_zu
        self.feld = feld


def _calc_zeichen(zeichen, farbe, ausweich):
    farbe = farbe.strip()
    if zeichen and farbe and ERLAUBT_FARBEN:
        return "\x1b[" + FARBEN[farbe] + "m" + zeichen + "\x1b[0m"
    if not ERLAUBT_FARBEN:
        return ausweich or " "
    return zeichen or "  "


class Feld:
    obj: Union[ScenarioEnde, str, _SpielerTyp, None]

    def __init__(self, boden: str = "",
                 boden_zeichen: str = "",
                 boden_ausweich: str = "",
                 boden_farbe: str = "",
                 obj: str = "",
                 zeichen: str = "",
                 ausweich: str = "",
                 farbe: str = ""
                 ) -> None:
        boden = boden.strip()
        obj = obj.strip()
        self.boden = boden
        self.boden_zeichen = boden_zeichen
        if obj.startswith('#'):
            self.obj = ScenarioEnde(ergebnis=obj[1:])
        elif obj == 'Spieler':
            self.obj = Spieler
        elif obj:
            self.obj = obj
        else:
            self.obj = None
        self.zeichen = _calc_zeichen(zeichen, farbe, ausweich)
        self.boden_zeichen = _calc_zeichen(boden_zeichen, boden_farbe, 
                                           boden_ausweich)
        # self.obj_data = obj_data

    def __str__(self):
        if self.obj and self.zeichen and self.zeichen != " ":
            return self.zeichen
        return self.boden_zeichen

    def treffe(self, mänx: Mänx, sc: 'Scenario') -> Union[bool, ScenarioEnde]:
        if isinstance(self.obj, ScenarioEnde):
            return self.obj
        elif not self.obj:
            if self.boden:
                return sc.treffe_boden(mänx, self.boden)
            return True
        else:
            assert isinstance(self.obj, str)
            try:
                obj = mänx.welt.obj(self.obj)
            except KeyError:
                return False
            else:
                return obj.main(mänx) or False

    def move_obj(self, other: 'Feld'):
        self.zeichen, other.zeichen = other.zeichen, self.zeichen
        self.obj, other.obj = other.obj, self.obj
        # self.obj_data, other.obj_data = other.obj_data, self.obj_data


def _auf_drei(boden: str, zeichen="", ausweich="", farbe=""):
    return boden, zeichen, ausweich, farbe


def parse_feld(obj, ch):
    if ch not in obj:
        return Feld(" ")
    n = obj[ch]
    n0 = n[0].strip()
    if n0.startswith("@"):
        return Feld(n0[1:], *n[1:])
    ns = n[:3] + n[4:]
    if len(n) > 3 and n[3] in obj:
        return Feld(*_auf_drei(*obj[n[3]]), *ns)
    else:
        return Feld("", "", "","", *ns)


def _strip_nl(line: str) -> str:
    if line.endswith("\n"):
        return line[:-1]
    return line


class Scenario:
    def __init__(self, name: str, feld: List[List[Feld]]) -> None:
        self.name = name
        self.anzeigename = name
        self.feld = feld
        self.spielerpos: List[int]
        spos_set = False
        höhe = max(len(line) for line in feld)
        for y, r in enumerate(feld):
            for _i in range(len(r), höhe):
                r.append(Feld(""))
            for x, k in enumerate(r):
                if k.obj is Spieler:
                    self.spielerpos = [y, x]
                    spos_set = True
        assert spos_set

    @classmethod
    def laden(cls, pfad: str) -> 'Scenario':
        with open(pfad, "r") as p:
            lines = map(_strip_nl, p.readlines())
            sc_name = next(lines)
            obs: Dict[str, List[str]] = {}
            for line in lines:
                if line == "---":
                    break
                elif not line:
                    continue
                s = line.split(":", 1)
                if len(s) > 1:
                    name, vals = s
                    if name in obs:
                        raise ValueError("Doppeltes Objekt:", name)
                    obs[name] = vals.split(";")
            else:
                raise ValueError("Kein Anfang des Feldes gefunden!")
            feld = []
            for line in lines:
                line = line.rstrip()
                if line == "..." or not line:
                    break
                feldl = []
                for ch in line:
                    feldl.append(parse_feld(obs, ch))
                feld.append(feldl)
        return cls(sc_name, feld)

    def print_feld(self, clear: bool=True):
        if ERLAUBT_FARBEN:
            if clear:
                print("\x1b7\x1b[0;0H", end="")
            else:
                print("\x1b[2J\x1b[0;0H", end="")
        print(self.anzeigename)
        for reihe in self.feld:
            for feld in reihe:
                print(feld, end="")
            print()
        if ERLAUBT_FARBEN and clear:
            print("\x1b8", end="")

    def bewege_spieler(self, mänx, y, x) -> Op[ScenarioEnde]:
        """Bewege den Spieler um y und x relativ"""
        ys, xs = self.spielerpos
        yn, xn = (ys + y) % len(self.feld), (xs + x) % len(self.feld[0])
        feld = self.feld[yn][xn]
        treff = feld.treffe(mänx, self)
        if isinstance(treff, ScenarioEnde):
            return treff
        if treff:
            self.feld[yn][xn].move_obj(self.feld[ys][xs])
            self.spielerpos = [yn, xn]
        return None

    def treffe_boden(self, mänx, obj):
        """Treffe ein Stück Boden"""
        # if obj in self.bodenfns:
        #     self.bodenfns[obj](mänx)
        return True

    def einleiten(self, mänx: Mänx) -> ScenarioEnde:
        mänx.context = self
        ans = None
        clear = False
        while not ans:
            self.print_feld(clear)
            clear = True
            arg = mänx.minput(">")
            if arg == "w":
                ans = self.bewege_spieler(mänx, -1, 0)
            elif arg == "d":
                ans = self.bewege_spieler(mänx, 0, 1)
            elif arg == "s":
                ans = self.bewege_spieler(mänx, 1, 0)
            elif arg == "a":
                ans = self.bewege_spieler(mänx, 0, -1)
            else:
                print("Hä? Was is'n 'n", repr(arg))
        if mänx.context is self:
            mänx.context = None
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
    from xwatc.jtg.nord import registrieren
    m = system.Mänx()
    registrieren(m)
    try:
        erg = lade_scenario(m, "disnajenbun")
    except system.Spielende:
        print("Du bist tot")
    else:
        print(f"Es geht mit {erg} weiter.")
