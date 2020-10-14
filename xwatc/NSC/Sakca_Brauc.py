from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner
class SakcaBrauc(NSC):
    def __init__(self):
        super().__init__("Sakca Brauc", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        print("Als du Anstalten machtest, deine Waffe zu zücken, "
              "schlug Sakca dir mit der Faust ins Gesicht.")
        mint("Als du daraufhin zurücktaumelst, schlägt sie dich bewusstlos.")
        
        
            


    def reden(self, mänx: Mänx) -> None:
        print('"Was ist?", fragt dich die Wache.')
        opts = [
            ('"Hallo, Wie heißt du?"', 'heißt', 0),
            ('"Du heißt Maria, oder?"', "maria", 1),
            ('"Wie findest du das Wetter heute?"', "wetter", 2),
            ('"Wie geht es dir?"', "geht", 3)
        ]
        opt = mänx.menu(
            "Was sagst du?", opts)
        if opt == 0:
            print("Ich heiße Sakca")
            
            
        elif opt == 1:
            print("Lass mich in Ruhe!")
            if ja_nein(mänx, "Lässt du sie in Ruhe?"):
                mint("Du lässt sie in Ruhe.")
            else:
                ('Weil du sie anscheinend nicht in Ruhe lassen willst, schlägt Sakca dir ins Gesicht.')
        elif opt == 2:
            mint('"schön", sagt Sakca.')
        elif opt == 3:
            mint('"gut", sagte die Wache.')
            print('Sie scheint nicht allzu gesprächig zu sein.')

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        return NSC.optionen(self, mänx) + [
            ("Reden", "reden", self.reden)
            ("Kämpfen", "kämpfen", self.kampf)
        ]

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und geht ihrer Arbeit nach.")
        super().main(mänx)