from xwatc.dorf import NSC
from xwatc.system import mint, kursiv, Mänx, ja_nein, minput, Spielende, malp, sprich
import random
from xwatc.jtg import t2
from xwatc.lg.norden.gefängnis_von_gäfdah import gefängnis_von_gäfdah
import xwatc_Hauptgeschichte
from time import sleep


class RuboicHätxrik(NSC):
    def __init__(self) -> None:
        super().__init__("Ruboic Hätxrik", "Äntor")
        cls = type(self)

        self.dialog("hallo1",
                    '"Hallo Ich heiße Tom"',
                    ["Tja mi kans egal sän"], gruppe="bluu")

        self.dialog("hallo2",
                    '"Hallo Ich heiße Makc"',
                    cls.reden_makc, gruppe="bluu")

        self.dialog("hallo3",
                    '"Hallo Ich heiße Thierca"',
                    cls.reden_thierca, gruppe="bluu")

        self.dialog("hallo4",
                    '"Hallo Ich heiße Ares"',
                    cls.reden_ares, gruppe="bluu")

        self.dialog("hallo5",
                    '"Hallo, wie heißt du?"',
                    cls.reden_hallo, wiederhole=1)

        self.dialog("geht", '"Wie geht es dir?"', cls.reden_geht)
        self.dialog("wetter",
                    '"Wie findest du das Wetter heute?"',
                    cls.reden_wetter)
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
                    "wenn sie mich davon unterrichten würden. "
                    "Ich danke ihnen schon einmal im vorraus.",
                    cls.reden_suche2)

    @staticmethod
    def sgh(mänx):
        gäfdah = mänx.welt.obj("Gäfdah")
        if ja_nein(mänx, "Durchsuchst du den Mann?"):
            mänx.erhalte("Äntorenmantel", 1)
            mänx.erhalte("Äntorenstiefel", 2)
            mänx.erhalte("Socken", 4)
            mänx.erhalte("Gold", 89)
            mänx.erhalte("Saphir", 1)
            mänx.erhalte("Äntorenhelm", 1)
            mänx.erhalte("Lederbeutel", 1)
            mänx.erhalte("Dolch", 1)
            mänx.erhalte("Messer", 5)
            mänx.erhalte("Bozear", 8)
            mänx.erhalte("Dicke Unterhose", 1)
            mänx.erhalte("Äntorenhose", 1)
            mänx.erhalte("Ring der Medusa", 1)
            mänx.erhalte("Äntorenklinge", 1)
            mänx.erhalte("Äntorenlangbogen", 1)
            mänx.erhalte("Äntorenkurzbogen", 1)
            mänx.erhalte("Pfeile", 198)
            mänx.erhalte("Brot", 3)
            mänx.erhalte("Salzhering", 5)
            mänx.erhalte("Salzlachs", 3)
            mänx.erhalte("Salami", 3)
            mänx.erhalte("Zähe Bohne", 2)
            mänx.erhalte("Äntorenmedaille", 1)
            if mänx.hat_fähigkeit("Schnellplündern"):
                mint(
                    'Junger Mann: "Oh, Verdammt". Zwei junge Männer stehen eilig von ihren Stühlen auf.')
                sprich("Junger Mann", 'Ruboic hat schon wieder einen Anfall! Der Arzt hat ihm zwar gesagt, '
                                      'er soll mit dem Trinken aufhören, doch was hat er gemacht? Ach Verdammt, '
                                      'dieses Mal scheints wirklich richtig übel zu sein...', warte=True)
                mint("Die beiden Männer tragen Hätxrik vorsichtig aus der Taverne.")
                if ja_nein(mänx, "Folgst du ihnen"):
                    mint("Du versuchst ihnen zu folgen, doch als du auf die Straße "
                         "trittst, sind sie bereits nicht mehr zu sehen.")
                    if ja_nein(mänx, "Gehst du zürück in die Taverne?"):
                        mint("Du gehst zurück in die Taverne")
                    else:
                        mint("Du bleibst draußen")
                        return mänx.context.get_ort("draußen")
                else:
                    pass
            else:
                pass
        else:
            mint("OK, dann nicht.")

        return False

    def kampf(self, mänx: Mänx):
        a = random.randint(1, 500)
        if a == 1:
            ("Bevor du ihn angreifen konntest, fiel der Mann einfach tot um")
            self.tot = True
            return self.sgh(mänx)
        else:
            if ja_nein(mänx, "Der Mann richtet seine Armbrust auf dich. "
                             "Willst du immer noch kämpfen?"):
                mint("Er drückt ab.")
                raise Spielende

            else:
                mint("Gut...")

    def vorstellen(self, mänx: Mänx) -> None:
        a = random.randint(1, 500)
        if a == 1:
            malp("Bevor du mit ihm reden konntest, fiel der Mann einfach tot um")
            self.tot = True
        mint('"Tag. Äch ben Hätrik"')

    def reden_makc(self, mänx: Mänx):
        mint('"makc ja?, ich hatte mall so nen soon." '
             'Der Mann drückt dir etwas in die Hand. '
             'Dann, '
             'ganz plötzlich fällt er um und beginnt röchelnd zu verenden.  ')
        self.tot = True
        mänx.erhalte("Aphrodiikensamen", 5)
        return self.sgh(mänx)

    def reden_thierca(self, mänx: Mänx):
        mint('"thiersca ja?, du erinnnest mich an men Tochterle. Wisst de?!" '
             'Der Mann drückt dir etwas in die Hand. '
             'Dann, '
             'ganz plötzlich fängt er an zu röcheln und fällt tot um.  ')
        self.tot = True
        mänx.erhalte("Bantoriitensamen", 5)
        return self.sgh(mänx)

    def reden_ares(self, mänx: Mänx) -> None:
        mint("Ares?", kursiv("Du?!"), "bist es?")
        a = random.randint(1, 500)
        if a == 1:
            malp("Plötzlich fiel der Mann einfach tot um")
        else:
            a = random.randint(1, 40)
            if a == 1:
                malp("Plötzlich sprach der Mann mit einer monotonen, hölzernen Stimme.")
                mint('"HALLO;ENTITÄT §===(§"/F LANGE '
                     '', kursiv("ggrrrpfft"), 'NICHT MEHR GESE'
                                              '', kursiv("bbpfftgr"), 'HEN'
                                                                      '', kursiv("ährrkrtg"), '"')
                mänx.erhalte("Leere", 5)
                mänx.erhalte("NOEL@þ", 1)
                mänx.erhalte("Lichtschwert", 1)
                mänx.erhalte("Honigpastete", 5)
                malp("NOEL hinterlässt dir eine Nachricht:")
                mint("", kursiv("Komm zu mir, komm/komm/komm/komm/"
                                "komm/komm/komm\komm\komm\komm\komm\/"
                                "komm\komm\komm\komm\komm\komm\komm/\/"
                                "komm\komm/komm\komm/komm zu mir"), "")
                if ja_nein(mänx, "Willst du mitkommen?"):
                    malp('Irgendwo schien jemand sich zu freuen.')
                    kursiv('"Du wirst es sicherlich nicht bereuen."')
                    b = random.randint(1, 4)
                    if b == 1:
                        gefängnis_von_gäfdah
                    elif b == 2:
                        xwatc_Hauptgeschichte.himmelsrichtungen(mänx)
                    else:
                        t2(mänx)
                else:
                    mint("", kursiv("Das"), "wirst du bereuen.")
                    raise Spielende
            elif a == 2:
                mänx.erhalte("Apfel", 5)
                mänx.erhalte("Kometenstein", 1)
                mänx.erhalte("Speer", 1)
                mänx.erhalte("Honigpastete", 5)

            elif a == 3:
                mänx.erhalte("Leere", 5)
                mänx.erhalte("Spielzeugauto", 1)
                mänx.erhalte("Holzente", 1)
                mänx.erhalte("Hering", 5)

            elif a == 4:
                mänx.erhalte("Gänseblümchen", 5)
                mänx.erhalte("Rose", 1)
                mänx.erhalte("Löwenzahn", 1)
                mänx.erhalte("Distelblüte", 5)

            elif a == 5:
                mänx.erhalte("Mächtige Axt", 1)
                mänx.erhalte("Schwert", 1)
                mänx.erhalte("Lichtschwert", 1)
                mänx.erhalte("Speer", 1)

            else:
                mänx.erhalte("Mantel", 5)
                mänx.erhalte("Hose", 1)
                mänx.erhalte("Unterhose", 1)
                mänx.erhalte("Honigpastete", 5)

            mint("Der Mann stirbt")
        self.tot = True
        return self.sgh(mänx)

    def reden_hallo(self, mänx: Mänx) -> None:
        mint('"Äch ben Hätrik"')

    def reden_geht(self, mänx: Mänx) -> None:
        mint("Mi gätc gout.")

    def reden_agaga(self, mänx: Mänx) -> None:
        malp("Der Mann runzelt die Stirn.")
        mint('"Was willst du?"')
        malp("Dann weiten sich seine Augen und er rennt davon.")
        self.tot = True

    def reden_suche1(self, mänx: Mänx) -> None:
        mint("...")
        malp("Der Mann scheint Angst zu haben.")
        malp("Du kannst seine Angst förmlich",
             kursiv(" riechen"), ".")
        malp("Schließlich rennt er weg")
        self.tot = True

    def reden_suche2(self, mänx: Mänx) -> None:
        malp("Der Mann blickt zu dir hoch")
        malp("Angst steht in seinen Augen geschrieben.")
        sleep(4)
        mint("Von der einen Sekunde auf die andere ist er verschwunden.")
        self.tot = True

    def reden_wetter(self, mänx: Mänx) -> None:
        mint("Gut, ne und?")

    def main(self, mänx: Mänx) -> None:
        malp('"Der Mensch, welchen du ansprachest, ist in einen dicken '
             'Bärenpelzmantel gekleidet."')
        mint("Er ist wohl ein Äntor, ein Jäger.")
        super().main(mänx)