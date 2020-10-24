from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner
import . norden
from . Fischerfraumassaker import fischerfraumassaker

class Fischerfrau(haendler.Händler):
    def __init__(self):
        super().__init__("Maria Fischfrisch", kauft=["Blume"], verkauft={
            "Hering": 4,
            "Sardine": 3,
            "Lachs": 6}, art="alte Fischerfrau")
        self.inventar["Gold"] = 

    def kampf(self, mänx: Mänx) -> None:
        fischerfraumassaker(mänx)
        
        
    def vorstellen(self, mänx):
        print("Die Fischerfrau verkauft Fische")
    

    def reden(self, mänx: Mänx) -> None:
        print('An einem Stand verkauft eine alte Frau Fische. ')
        opts = [
            ('"Hallo, Wer bist du?"', 'bist', 0),
            ('"Wie findest du das Wetter heute?"', "wetter", 1),
            ('"Wie geht es dir?"', "geht", 2)
        ]
        opt = mänx.menu(
            "Was sagst du?", opts)
        if opt == 0:
            print('(freundlich) "Ich heiße Maria. Und du?"')
            d=input('')
            print('"Das ist aber ein schöner Name."')
        elif opt == 1:
            print('"Schön, mein Kind."')
        elif opt == 2:
            mint('"Mir geht es gut. Wie geht es dir?"')
            k=input("")
            if k=="gut" or "sehr gut" or "super gut" or "wirklich gut" or "wirklich sehr gut":
                print('"Das ist aber schön."')
            else:
                print('"oh"')

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        return NSC.optionen(self, mänx) + [
            ("Reden", "reden", self.reden)
            ("Handeln", "handeln", self.handeln)
        ]

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und geht ernst und dienstbeflissen ihrer Arbeit nach.")
        super().main(mänx)
        
        




