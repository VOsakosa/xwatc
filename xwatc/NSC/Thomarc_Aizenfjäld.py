    
from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner    
class ThomarcAizenfjäld(NSC):    
    
    def __init__(self):
        super().__init__("Thomarc Aizenfjäld", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        print("Als du Anstalten machtest, deine Waffe zu zücken, "
              "schlug die Wache dir mit der flachen Seite ihres Schwertes gegen die Schläfe.")
        
        
            


    def reden(self, mänx: Mänx) -> None:
        print('"Was ist?", fragt die Wache dich.')
        opts = [
            ('"Hallo, Wer bist du?"', 'bist', 0),
            ('"Wie findest du das Wetter heute?"', "wetter", 1),
            ('"Hey, wie geht es dir?"', "geht", 2)
        ]
        opt = mänx.menu(
            "Was sagst du?", opts)
        if opt == 0:
            print("Der Wachmann reagiert nicht.")
        elif opt == 1:
            mint('"schön", sagte die Wache mürrisch.')
        elif opt == 2:
            mint('"gut", sagte die Wache.')
            print('Sie scheint nicht allzu gesprächig zu sein.')

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        return NSC.optionen(self, mänx) + [
            ("Reden", "reden", self.reden)
            ("Kämpfen", "kämpfen", self.kampf)
        ]

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und geht ernst und dienstbeflissen ihrer Arbeit nach.")
        super().main(mänx)