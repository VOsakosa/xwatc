from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner
class MartinPortulakk(NSC):
    def __init__(self):
        super().__init__("Martin Portulakk", "Bürger")

    def kampf(self, mänx: Mänx) -> None:
        if mänx.hat_klasse("Waffe", "legendäre Waffe"):
            mint('Du streckst ihn nieder, bevor er auch nur "Wache!" rufen konnte.')
            self.tot = True
        elif mänx.hat_klasse("Werkzeug"):
            mint('Du tötest den Mann. '
                 'Doch bevor er stirbt, ruft er noch: '
                 '"', kursiv ("Wachen!"), '", '
                 'und schon ist das Haus umstellt...')
            
        else:
            print("Du stürzt auf ihn zu und schlägst auf ihn ein.")
            print('Doch dann schreit er: ', kursiv('"Wache!"'), ', und schon ist das Haus umstellt...')
            
        
        
            


    def reden(self, mänx: Mänx) -> None:
        print('(ängstlich) "Was machst du in meinem Haus?!')
        opts = [
            ('"Ich tue dir nichts. Ich habe mich verirrt."', 'verirrt', 0),
            ('"Beruhige dich! Du bist doch Siegbert, oder?"', "siegbert", 1),
            ('"Wie findest du das Wetter heute?"', "wetter", 2),
            ('"Wie geht es dir?"', "geht", 3)
            ('"Ich will dir nichts tun!"', "!", 4)
            ('"Ich will dir nichts tun."', ".", 5)
            ('"Still oder ich töte dich!"', "töte", 6)
            ('(beruhigend)"Sei leise. '
             'Wenn du die Wachen rufst töte ich '
             'dich schneller als du "muck" sagst."', "muck", 7)
        ]
        opt = mänx.menu(
            "Was sagst du?", opts)
        if opt == 0:
            print("Der Wachmann reagiert nicht.")
            if ja_nein(mänx, " Beharrst du auf deine Frage?"):
                mint("Die Wache seufzt. Ich heiße Mario. Mario Wittenpfäld.")
            else:
                mint(self.name, "Du lässt die Wache in Ruhe.")
        elif opt == 1:
            print('Der Mann entspannte sich. "Nein" Siegbert wohnt in Haus Nr.5')
            
        elif opt == 2:
            mint('Ängstlich blickte der Mann sich um. "Schön... ', kursiv('Wachen!'), '"')
            print("Kaum rief er war das Haus schon umstellt.")
            
        elif opt == 3:
            mint('Ängstlich blickte der Mann sich um. "Gut... ', kursiv('Wachen!'), '"')
            print("Kaum rief er war das Haus schon umstellt.")
            
        elif opt == 4:
            mint('', kursiv('"Hilfe! Wachen!"'), ', schrie der Mann aus voller Kehle')
            print("Und kaum rief er war das Haus schon umstellt.")

        elif opt == 5:
            mint('Unsicher blickte der Mann sich um. "Gut... ', kursiv('Wachen!'), '"')
            print("Kaum rief er war das Haus schon umstellt.")

        elif opt == 6:
            mint('Still und ängstlich quetschte der Mann sich in eine Ecke seines Hauses.')
            print("Was tust du nun?")
            a=minput(mänx, "Durchsuchst du die Hütte, "
                     "bringst du den Mann um, "
                     "versuchst du mit ihm zu reden oder fliehst du? (d/um/r/f)", ["d", "um", "r", "f"])
            if a==d:
                mint("Du findest Kleidung, Fisch, Gemüse und Zeug.")
                mänx.inventar ["Socke"] += 8
                mänx.inventar ["Hose"] += 2
                mänx.inventar ["Hemd"] += 3
                mänx.inventar ["Seil"] += 1
                mänx.inventar ["Wollmütze"] += 1
                mänx.inventar ["Mantel"] += 2
                mänx.inventar ["Unterhose"] += 3
                mänx.inventar ["Stiefel"] += 2
                mänx.inventar ["Hering"] += 23
                mänx.inventar ["Forelle"] += 13
                mänx.inventar ["Lachs"] +=6
                mänx.inventar ["Hecht"] += 1
                mänx.inventar ["Piranha"] += 1
                mänx.inventar ["Blaufisch"] += 5
                mänx.inventar ["Geistfisch"] += 1
                mänx.inventar ["Kartoffel"] += 45
                mänx.inventar ["Karotte"] += 28
                mänx.inventar ["Aubergine"] += 12
                mänx.inventar ["Tomate"] += 18
                mänx.inventar ["Angel"] += 1
                mänx.inventar ["Glücksbringer eines Bauern"] += 1
                mänx.inventar ["Schaufel"] += 1
                mänx.inventar ["Harke"] += 1
                mänx.inventar ["Rechen"] += 1
                mänx.inventar ["Messer"] += 1

        elif opt == 7:
            mint('"gut", sagte die Wache.')
            
            

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        return NSC.optionen(self, mänx) + [
            ("Reden", "reden", self.reden)
            ("Kämpfen", "kämpfen", self.kampf)
        ]

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und geht ernst und dienstbeflissen ihrer Arbeit nach.")
        super().main(mänx)