from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner, Rückkehr
from xwatc.system import mint, kursiv, Mänx, ja_nein, minput, Spielende
import random
from xwatc.jtg import t2
from xwatc.lg.norden.gefängnis_von_gäfdah import gefängnis_von_gäfdah
import xwatc_Hauptgeschichte


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
                 '"', kursiv("Wachen!"), '", '
                 'und schon ist das Haus umstellt...')

        else:
            print("Du stürzt auf ihn zu und schlägst auf ihn ein.")
            print('Doch dann schreit er: ', kursiv('"Wache!"'),
                  ', und schon ist das Haus umstellt...')

    def reden(self, mänx: Mänx) -> Rückkehr:
        print('(ängstlich) "Was machst du in meinem Haus?!')
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
            print("Der Wachmann reagiert nicht.")
            if ja_nein(mänx, " Beharrst du auf deine Frage?"):
                mint("Die Wache seufzt. Ich heiße Mario. Mario Wittenpfäld.")
            else:
                mint(self.name, "Du lässt die Wache in Ruhe.")
        elif opt == 1:
            print('Der Mann entspannte sich. "Nein" Siegbert wohnt in Haus Nr.5')

        elif opt == 2:
            mint('Ängstlich blickte der Mann sich um. "Schön... ',
                 kursiv('Wachen!'), '"')
            print("Kaum rief er war das Haus schon umstellt.")

        elif opt == 3:
            mint('Ängstlich blickte der Mann sich um. "Gut... ',
                 kursiv('Wachen!'), '"')
            print("Kaum rief er war das Haus schon umstellt.")

        elif opt == 4:
            mint('', kursiv('"Hilfe! Wachen!"'),
                 ', schrie der Mann aus voller Kehle')
            print("Und kaum rief er war das Haus schon umstellt.")

        elif opt == 5:
            mint('Unsicher blickte der Mann sich um. "Gut... ',
                 kursiv('Wachen!'), '"')
            print("Kaum rief er war das Haus schon umstellt.")

        elif opt == 6:
            mint('Still und ängstlich quetschte der Mann sich in eine Ecke seines Hauses.')
            print("Was tust du nun?")
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
        print("Martin Portulakk heißt Martin Portulakk und ist Bürger von Gäfdah.")
        super().main(mänx)


class RuboicHätxrik(NSC):
    def __init__(self) -> None:
        super().__init__("Ruboic Hätxrik", "Jäger")
        cls = type(self)
        a = random.randint(1, 500)
        if a == 1:
            ("Bevor du mit ihm reden konntest, fiel der Mann einfach tot um")
            self.tot = True
        else:
            self.dialog("hallo1",
                        '"Hallo Ich heiße Tom"',
                        cls.reden_tom)

        self.dialog("hallo2",
                    '"Hallo Ich heiße Makc"',
                    cls.reden_makc)

        self.dialog("hallo3",
                    '"Hallo Ich heiße Thierca"',
                    cls.reden_thierca)

        self.dialog("hallo4",
                    '"Hallo Ich heiße Ares"',
                    cls.reden_ares)

        self.dialog("hallo5",
                    '"Hallo, wie heißt du?"',
                    cls.reden_hallo)

        self.dialog("geht", '"Wie geht es dir?"',
                    cls.reden_geht)
        self.dialog("wetter",
                    '"Wie findest du das Wetter heute?"', cls.reden_wetter)
        self.dialog("agaga",
                    "Aggagagaggagrrrrrrrr!!!!  Ähäsifowipppfff Ich binne v'ückt bööö...",
                    cls.reden_agaga)
        self.dialog("suche",
                    "Hallo Ich such so 'nen sabbernden Verrückten. "
                    "Haste'n geseh'n?",
                    cls.reden_suche1)
        self.dialog("suche2",
                    "Tag. "
                    "Ich hätte eine Frage. "
                    "Hier soll es einen Verrückten geben, "
                    "so einen sabbernden. Haben sie zufälligerweise einen gesehen? "
                    "Wenn ja wäre es sehr nett, "
                    "wenn sie mit davon unterrichten würden. "
                    "Ich danke ihnen schon einmal im vorraus.",
                    cls.reden_suche2)

    def kampf(self, mänx: Mänx) -> None:
        a = random.randint(1, 500)
        if a == 1:
            ("Bevor du ihn angreifen konntest, fiel der Mann einfach tot um")
            self.tot = True
        else:
            if ja_nein(mänx, "Der Mann richtet seine Armbrust auf dich. "
                       "Willst du immer noch kämpfen?"):
                mint("Er drückt ab.")
                raise Spielende

            else:
                mint("Gut...")

    def vorstellen(self, mänx: Mänx) -> None:
        mint('"Tag. Was ist?"')

    def reden_tom(self, mänx: Mänx) -> None:
        mint("Tja mi kans egal sän")

    def reden_makc(self, mänx: Mänx) -> None:
        mint('"makc ja?, ich hatte mall so nen soon." '
             'Der Mann drückt dir etwas in die Hand. '
             'Dann, '
             'ganz plötzlich fängt er an zu röcheln und fällt tot um.  ')
        self.tot = True
        mänx.erhalte("Aphrodiikensamen", 5)

    def reden_thierca(self, mänx: Mänx) -> None:
        mint('"thiersca ja?, du erinnnest mich an men Tochterle. Wisst de?!" '
             'Der Mann drückt dir etwas in die Hand. '
             'Dann, '
             'ganz plötzlich fängt er an zu röcheln und fällt tot um.  ')
        self.tot = True
        mänx.erhalte("Bantoriitensamen", 5)

    def reden_ares(self, mänx: Mänx) -> None:
        mint("Ares?", kursiv("Du?!"), "bist es?")
        a = random.randint(1, 500)
        if a == 1:
            ("Plötzlich fiel der Mann einfach tot um")
            self.tot = True
        else:
            a = random.randint(1, 40)
            if a == 1:
                print("Plötzlich sprach der Mann mit einer monotonen, hölzernen Stimme.")
                mint('"HALLO;ENTITÄT §===(§"/F LANGE '
                     '', kursiv("ggrrrpfft"), 'NICHT MEHR GESE'
                     '', kursiv("bbpfftgr"), 'HEN'
                     '', kursiv("ährrkrtg"), '"')
                mänx.erhalte("Leere", 5)
                mänx.erhalte("NOEL@þ", 1)
                mänx.erhalte("Lichtschwert", 1)
                mänx.erhalte("Honigpastete", 5)
                print("NOEL hinterlässt dir eine Nachricht:")
                mint("", kursiv("Komm zu mir, komm/komm/komm/komm/"
                                "komm/komm/komm\komm\komm\komm\komm\/"
                                "komm\komm\komm\komm\komm\komm\komm/\/"
                                "komm\komm/komm\komm/komm zu mir"), "")
                if ja_nein(mänx, "Willst du mitkommen?"):
                    print('Irgendwo schien jemand sich zu freuen.')
                    kursiv('"Du wirst es sicherlich nicht bereuen."')
                    b = random.randint(1, 4)
                    if b == 1:
                        gefängnis_von_gäfdah
                    if b == 2:
                        xwatc_Hauptgeschichte.himmelsrichtungen(mänx)

    def reden_hallo(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')

    def reden_geht(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')

    def reden_agaga(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')

    def reden_suche1(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')

    def reden_suche2(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')

    def reden_geht(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')

    def main(self, mänx: Mänx) -> None:
        print('"Tag. Was ist?"')
        super().main(mänx)
