from xwatc.dorf import Rückkehr, NSC
from xwatc.system import mint, kursiv, Mänx, ja_nein, minput, malp
from xwatc.jtg import t2


class MartinPortulakk(NSC):
    def __init__(self) -> None:
        super().__init__("Martin Portulakk", "Bürger")
        self.position="Haus"

    def kampf(self, mänx: Mänx) -> None:
        if mänx.hat_klasse("Waffe", "legendäre Waffe"):
            mint('Du streckst ihn nieder, bevor er auch nur "Wache!" rufen konnte.')
            self.tot = True
        elif mänx.hat_klasse("Werkzeug"):
            mint('Du tötest den Mann. '
                 'Doch bevor er stirbt, ruft er noch: '
                 '"', kursiv("Wachen!"), '", '
                 'und schon ist das Haus umstellt...')

        else:
            malp("Du stürzt auf ihn zu und schlägst auf ihn ein.")
            malp('Doch dann schreit er: ', kursiv('"Wache!"'),
                  ', und schon ist das Haus umstellt...')

    def reden(self, mänx: Mänx) -> Rückkehr:
        malp('(ängstlich) "Was machst du in meinem Haus?!')
        opts = [
            ('"Ich tue dir nichts. Ich habe mich verirrt."', 'verirrt', 0),
            ('"Beruhige dich! Du bist doch Siegbert, oder?"', "siegbert", 1),
            ('"Wie findest du das Wetter heute?"', "wetter", 2),
            ('"Wie geht es dir?"', "geht", 3),
            ('"Ich will dir nichts tun!"', "!", 4),
            ('"Ich will dir nichts tun."', ".", 5),
            ('"Still oder ich töte dich!"', "töte", 6),
            ('(beruhigend)"Sei leise. '
             'Wenn du die Wachen rufst töte ich '
             'dich schneller als du "muck" sagst.', "muck", 7),
            ('Tut mir Leid, das war ein Missverständnis', "Missverständnis", 8),
        ]
        opt = mänx.menu(opts, frage="Was sagst du?")
        if opt == 0:
            malp("Der Wachmann reagiert nicht.")
            if ja_nein(mänx, " Beharrst du auf deine Frage?"):
                mint("Die Wache seufzt. Ich heiße Mario. Mario Wittenpfäld.")
            else:
                mint(self.name, "Du lässt die Wache in Ruhe.")
        elif opt == 1:
            malp('Der Mann entspannte sich. "Nein" Siegbert wohnt in Haus Nr.5')

        elif opt == 2:
            mint('Ängstlich blickte der Mann sich um. "Schön... ',
                 kursiv('Wachen!'), '"')
            malp("Kaum rief er war das Haus schon umstellt.")

        elif opt == 3:
            mint('Ängstlich blickte der Mann sich um. "Gut... ',
                 kursiv('Wachen!'), '"')
            malp("Kaum rief er war das Haus schon umstellt.")

        elif opt == 4:
            mint('', kursiv('"Hilfe! Wachen!"'),
                 ', schrie der Mann aus voller Kehle')
            malp("Und kaum rief er war das Haus schon umstellt.")

        elif opt == 5:
            mint('Unsicher blickte der Mann sich um. "Gut... ',
                 kursiv('Wachen!'), '"')
            malp("Kaum rief er war das Haus schon umstellt.")

        elif opt == 6:
            mint('Still und ängstlich quetschte der Mann sich in eine Ecke seines Hauses.')
            malp("Was tust du nun?")
            a = minput(mänx, "Durchsuchst du die Hütte, "
                       "bringst du den Mann um, "
                       "versuchst du mit ihm zu reden oder fliehst du? (d/um/r/f)", ["d", "um", "r", "f"])
            if a == 'd':
                mint("Du findest Kleidung, Fisch, Gemüse und Zeug.")
                # so ist es schöner
                # d = {"Socke": 8, "Hose":2}
                # for name, anzahl in d.items():
                #    mänx.inventar[name] += anzahl
                mänx.inventar["Socke"] += 8
                mänx.inventar["Hose"] += 2
                mänx.inventar["Hemd"] += 3
                mänx.inventar["Seil"] += 1
                mänx.inventar["Wollmütze"] += 1
                mänx.inventar["Mantel"] += 2
                mänx.inventar["Unterhose"] += 3
                mänx.inventar["Stiefel"] += 2
                mänx.inventar["Hering"] += 23
                mänx.inventar["Forelle"] += 13
                mänx.inventar["Lachs"] += 6
                mänx.inventar["Hecht"] += 1
                mänx.inventar["Piranha"] += 1
                mänx.inventar["Blaufisch"] += 5
                mänx.inventar["Geistfisch"] += 1
                mänx.inventar["Kartoffel"] += 45
                mänx.inventar["Karotte"] += 28
                mänx.inventar["Aubergine"] += 12
                mänx.inventar["Tomate"] += 18
                mänx.inventar["Angel"] += 1
                mänx.inventar["Glücksbringer eines Bauern"] += 1
                mänx.inventar["Schaufel"] += 1
                mänx.inventar["Harke"] += 1
                mänx.inventar["Rechen"] += 1
                mänx.inventar["Messer"] += 1

        elif opt == 7:
            mint('!!!?B?Ä?B?Ä?B?Ä?B?Ä?!!!  FEHLERüłþſs')
            mänx.erhalte("Banane", 3)
            mänx.erhalte("Apfel", 12)
            mänx.erhalte("Gold", 153)
            mänx.erhalte("Ätherrose", 1)
            mänx.erhalte("Moorfut'schlamm", 10)
            mänx.erhalte("Erbse", 438)
            mänx.erhalte("Truthahnfleisch", 50)
            mänx.erhalte("JOEL@þ", 1)
            t2(mänx)
        return Rückkehr.VERLASSEN

    def main(self, mänx: Mänx) -> None:
        malp("Martin Portulakk heißt Martin Portulakk und ist Bürger von Gäfdah.")
        super().main(mänx)
