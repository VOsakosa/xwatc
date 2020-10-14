from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner
class OrfGrouundt(NSC):
    def __init__(self):
        super().__init__("Orf Grouudt", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        print("Als du Anstalten machtest, deine Waffe zu zücken, "
              "gab der Wachmann dir eine so dicke Kopfnuss, dass du ohnmächtig auf das Pflaster sinkst.")
        
        
            


    def reden(self, mänx: Mänx) -> None:
        print('"Hallo"')
        opts = [
            ('"Wer bist du?"', 'bist', 0),
            ('"Du bist doch ein Panti, oder?"', "panti", 1),
            ('"Wie findest du das Wetter heute?"', "wetter", 2),
            ('"Wie geht es dir?"', "geht", 3)
        ]
        opt = mänx.menu(
            "Was sagst du?", opts)
        if opt == 0:
            print('"Hau ab!"')
        elif opt == 1:
            print("", kursiv ("NEIN!"), "")
            mint("Wage es ja nicht wieder mich einen Panti zu nennen!!!")
        elif opt == 2:
            mint('"Hau ab", sagte die Wache mürrisch.')
        elif opt == 3:
            mint('"Hau ab!", sagte die Wache.')
            print('Sie scheint nicht allzu gesprächig zu sein.')

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        return NSC.optionen(self, mänx) + [
            ("Reden", "reden", self.reden)
            ("Kämpfen", "kämpfen", self.kampf)
        ]

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und geht ernst und dienstbeflissen ihrer Arbeit nach.")
        super().main(mänx)