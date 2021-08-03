from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner, Rückkehr
import xwatc.lg.norden
from . Fischerfraumassaker import fischerfraumassaker
from xwatc.haendler import Händler
from xwatc.system import Mänx, malp, mint

class Fischerfrau(Händler):
    def __init__(self):
        super().__init__("Maria Fischfrisch", kauft=["Blume"], verkauft={
            "Hering": 4,
            "Sardine": 3,
            "Lachs": 6}, art="alte Fischerfrau")
        self.inventar["Gold"] = 12

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
            mänx.minput(mänx, "")
            if k=="gut" or "sehr gut" or "super gut" or "wirklich gut" or "wirklich sehr gut":
                malp('"Das ist aber schön."')
            else:
                malp('"oh"')
        return Rückkehr.VERLASSEN
        
        




