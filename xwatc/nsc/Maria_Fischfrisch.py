from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner
class Fischerfrau(NSC):
    def __init__(self):
        super().__init__("Maria Fischfrisch", "alte Fischerfrau")

    def kampf(self, mänx: Mänx) -> None:
        print("Als du Anstalten machtest, deine Waffe zu zücken, "
              "schlug die Wache dir mit der flachen Seite ihres Schwertes gegen die Schläfe.")
        
        
        
        
        
    def handeln(self, mänx: Mänx) -> None:
    

        
        
            


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
        
        
    class Fischerfrau(haendler.Händler):
    """Alte Frau, die Fische verkauft."""

    def __init__(self):
        super().__init__("Frau", kauft=["Blumen"], verkauft={
            "Hering": 1}, gold=0, art="Frau")

    def vorstellen(self, mänx):
        print("Die Fischerfrau verkauft Fische"
              "Sie scheint zu frieren.")

    def get_preis(self, _):
        return 0

    def kampf(self, mänx: Mänx) -> None:
        print("Das Mädchen ist schwach. Niemand hindert dich daran, sie "
              "auf offener Straße zu schlagen.")
        print("Sie hat nichts außer ihren Lumpen.", end="")
        if self.verkauft["Rose"]:
            print(
                ", die Blume, die sie dir verkaufen wollte, ist beim Kampf zertreten worden.")
        else:
            print(".")
        del self.verkauft["Rose"]
        self.plündern(mänx)
