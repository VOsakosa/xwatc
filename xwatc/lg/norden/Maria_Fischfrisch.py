from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner, Rückkehr
from xwatc import haendler
from xwatc.system import Mänx, mint
from xwatc.lg.norden.Fischerfrau_Massaker import fischerfraumassaker

class Fischerfrau(haendler.Händler):

    def kampf(self, mänx: Mänx) -> None:
        fischerfraumassaker(mänx)
        self.tot = True

    def vorstellen(self, mänx):
        print("Die Fischerfrau verkauft Fische.")
        
    def __init__(self):
        super().__init__("Maria Fischfrisch", art="Fischerfrau",
                          kauft=["Blume"], gold=200, verkauft={
            "Hering": (4, 6),
            "Sardelle": (13, 5),
            "Lachs": (4, 8)})


    def reden(self, mänx: Mänx) -> Rückkehr:
        print('An einem Stand verkauft eine alte Frau Fische. ')
        opts = [
            ('"Hallo, Wer bist du?"', 'bist', 0),
            ('"Wie findest du das Wetter heute?"', "wetter", 1),
            ('"Wie geht es dir?"', "geht", 2)
        ]
        opt = mänx.menu(opts, frage="Was sagst du?")
        if opt == 0:
            print('(freundlich) "Ich heiße Maria. Und du?"')
            if "tot" not in mänx.minput(': '):
                print('"Das ist aber ein schöner Name."')
            else:
                print('"Tod?"')
        elif opt == 1:
            print('"Schön, mein Kind."')
        elif opt == 2:
            mint('"Mir geht es gut. Wie geht es dir?"')
            k=input("")
            if k=="gut" or "sehr gut" or "super gut" or "wirklich gut" or "wirklich sehr gut":
                print('"Das ist aber schön."')
            else:
                print('"oh"')
        return Rückkehr.WEITER_REDEN
        
        




