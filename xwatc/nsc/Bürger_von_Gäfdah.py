from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner
from xwatc.system import mint, kursiv, Mänx, ja_nein, minput

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
            if a=='d':
                mint("Du findest Kleidung, Fisch, Gemüse und Zeug.")
                #so ist es schöner
                # d = {"Socke": 8, "Hose":2}
                # for name, anzahl in d.items():
                #    mänx.inventar[name] += anzahl
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
            ("Reden", "reden", self.reden),
            ("Kämpfen", "kämpfen", self.kampf),
        ]

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und geht ernst und dienstbeflissen ihrer Arbeit nach.")
        super().main(mänx)
        
        
        
        
class RuboicHätxrik(Angestellte):
    def __init__(self) -> None:
        super().__init__("Ruboic Hätxrik", "Jäger")
        cls = type(self)
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
                    "Haste'n geseh'n",
                    cls.reden_suche1)
        self.dialog("suche2",
                    "Tag. "
                    "Ich hätte eine Frage. "
                    "Hier soll es einen Verrückten geben, "
                    "so einen sabbernden. Haben sie zufälligerweise einen gesehen? "!
                    "Wenn ja wäre es sehr nett, "
                    "wenn sie mit davon unterrichten würden. "
                    "Ich danke ihnen schon einmal im vorraus.",
                    cls.reden_suche2)

    def kampf(self, mänx: Mänx) -> None:
        self.dialog("bewusstlos",
                    '"bewusstlos schlagen"',
                    cls.kampf_bewusstlos)
        self.dialog("töten", '"töten"',
                    cls.kampf_töten)
        self.dialog("fliehen",
                    '"zurück"',
                    cls.kampf_fliehen)
        
    def kampf_bewusstlos(self, mänx: Mänx) -> None:
        print("Sie weicht aus.")
        print("Wer hätte gedacht, dass sie so schnell sein konnte?")
        mint("Dann schnellt ihr Messer vor und du verendest elendig röchelnd.")
        raise Spielende
        
    def kampf_töten(self, mänx: Mänx) -> None:
        if mänx.hat_klasse("Waffe"):
            mint("Du tötest sie.")
            self.tot
            
    def kampf_fliehen(self, mänx: Mänx) -> None:
        mint('"Was ist?"')
        



    def vorstellen(self, mänx: Mänx) -> None:
        mint('"Tag. Was ist?"')

    def reden_tom(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')
    
    def reden_makc(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')
            
    def reden_thierca(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')
            
    def reden_ares(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')
            
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