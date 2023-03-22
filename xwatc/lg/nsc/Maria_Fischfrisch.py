from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Rückkehr
import xwatc.lg.norden
from .Fischerfraumassaker import fischerfraumassaker
from xwatc.haendler import Händler
from xwatc.system import Mänx, malp, mint


class Fischerfrau(Händler):
    def __init__(self):
        super().__init__("Maria Fischfrisch", kauft=["Blume"], verkauft={
            "Hering": (4, 3),
            "Sardine": (3, 3),
            "Lachs": (6, 4)}, art="alte Fischerfrau", gold=12)

    def kampf(self, mänx: Mänx) -> None:
        fischerfraumassaker(mänx)

    def vorstellen(self, mänx):
        malp("Die Fischerfrau verkauft Fische")

    def reden(self, mänx: Mänx) -> Rückkehr:
        malp('An einem Stand verkauft eine alte Frau Fische. ')
        opts = [
            ('"Hallo, Wer bist du?"', 'bist', 0),
            ('"Wie findest du das Wetter heute?"', "wetter", 1),
            ('"Wie geht es dir?"', "geht", 2)
        ]
        opt: int = mänx.menu(opts, "Was sagst du?")
        if opt == 0:
            malp('(freundlich) "Ich heiße Maria. Und du?"')
            mänx.minput(mänx, '')
            malp('"Das ist aber ein schöner Name."')
        elif opt == 1:
            malp('"Schön, mein Kind."')
        elif opt == 2:
            mint('"Mir geht es gut. Wie geht es dir?"')
            k = mänx.minput(mänx, "")
            if k in {"gut", "sehr gut", "super gut", "wirklich gut", "wirklich sehr gut",
                     "unglaublich schlecht"}:
                malp('"Das ist aber schön."')

            elif k in {"krass", "hammermäßig", "geil", "super"}:
                malp("Okeeey")

            elif k in {"schlecht", "sehr schlecht", "super schlecht", "wirklich schlecht",
                       "wirklich sehr schlecht", "unglaublich schlecht"}:
                malp('"Das ist aber traurig."')

            else:
                malp('"oh"')
        return Rückkehr.VERLASSEN
