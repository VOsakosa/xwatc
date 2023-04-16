import random
from xwatc import _
from xwatc.jtg import t2
from xwatc.lg import mitte
from xwatc.lg.norden import gäfdah
from xwatc.nsc import StoryChar, NSC, Person, Rückkehr
from xwatc.system import mint, kursiv, Mänx, ja_nein, Spielende, malp, sprich, Fortsetzung
from xwatc.untersystem.person import Fähigkeit
from xwatc.lg.norden.gefängnis_von_gäfdah import gefängnis_von_gäfdah


ruboic = StoryChar("nsc:freiwild:ruboic", ("Ruboic", "Hätxrik", "Äntor"),
                   Person("m"), startinventar={
    "Äntorenmantel": 1,
    "Äntorenstiefel": 2,
    "Gold": 89,
    "Saphir": 1,
    "Äntorenhelm": 1,
    "Lederbeutel": 1,
    "Dolch": 1,
    "Messer": 5,
    "Bozear": 8,
    "Dicke Unterhose": 1,
    "Äntorenhose": 1,
    "Ring der Medusa": 1,
    "Äntorenklinge": 1,
    "Äntorenlangbogen": 1,
    "Äntorenkurzbogen": 1,
    "Pfeile": 198,
    "Brot": 3,
    "Salzhering": 5,
    "Salzlachs": 3,
    "Salami": 3,
    "Zähe Bohne": 2,
    "Äntorenmedaille": 1,
})


def sgh(nsc: NSC, mänx: Mänx) -> Rückkehr | Fortsetzung:
    """Das passiert, nachdem Ruboic vor dir tot umfällt."""
    # gäfdah = mänx.welt.obj("Gäfdah")
    if ja_nein(mänx, "Durchsuchst du den Mann?"):
        if not mänx.hat_fähigkeit(Fähigkeit.Schnellplündern):
            malp("Zwei Männer kommen zufällig herein und erwischen dich.")
            sprich(_("Junger Mann"), _("He! Was machst du da mit Ruboic?"))
            sprich(_("Junger Mann"), _("Wachen!"))
            mint("Die Wachen kommen und führen dich ab.")
            return gefängnis_von_gäfdah
        else:
            malp("Du plünderst schnell den Mann.")
            nsc.plündern(mänx)
            malp("Kaum nachdem du fertig bist, kommen zwei junge Männer hinein.")
    else:
        mint("OK, dann nicht.")
            
    sprich(_("Junger Mann"), _("Oh, Verdammt"))
    sprich(_("Junger Mann"), _(
        'Ruboic hat schon wieder einen Anfall! Der Arzt hat ihm zwar gesagt, '
        'er soll mit dem Trinken aufhören, doch was hat er gemacht? Ach Verdammt, '
        'dieses Mal scheints wirklich richtig übel zu sein...'))
    mint("Die beiden Männer tragen Hätxrik vorsichtig aus der Taverne.")
    nsc.ort = None
    if ja_nein(mänx, "Folgst du ihnen?"):
        mint("Du versuchst ihnen zu folgen, doch als du auf die Straße "
             "trittst, sind sie bereits nicht mehr zu sehen.")
        if ja_nein(mänx, "Gehst du zurück in die Taverne?"):
            mint("Du gehst zurück in die Taverne")
            return gäfdah.eintritt_schenke
        else:
            mint("Du bleibst draußen")
            return gäfdah.eintritt_gäfdah
    else:
        return Rückkehr.VERLASSEN


@ruboic.kampf
def ruboic_kampf(self: NSC, mänx: Mänx):
    a = random.randint(1, 500)
    if a == 1:
        ("Bevor du ihn angreifen konntest, fiel der Mann einfach tot um")
        self.tot = True
        return sgh(self, mänx)
    else:
        if ja_nein(mänx, "Der Mann richtet seine Armbrust auf dich. "
                         "Willst du immer noch kämpfen?"):
            mint("Er drückt ab.")
            raise Spielende

        else:
            mint("Gut...")


@ruboic.vorstellen
def ruboic_vorstellen(self: NSC, mänx: Mänx) -> Rückkehr | None:
    malp('Der Mensch, welchen du ansprachest, ist in einen dicken '
         'Bärenpelzmantel gekleidet.')
    mint("Er ist wohl ein Äntor, ein Jäger.")
    a = random.randint(1, 500)
    if a == 1:
        malp("Bevor du mit ihm reden konntest, fiel der Mann einfach tot um")
        self.tot = True
        return Rückkehr.VERLASSEN
    self.sprich('Tag. Äch ben Hätrik')
    return None


def ruboic_reden_makc(self: NSC, mänx: Mänx):
    mint('"makc ja?, ich hatte mall so nen soon." '
         'Der Mann drückt dir etwas in die Hand. '
         'Dann, '
         'ganz plötzlich fällt er um und beginnt röchelnd zu verenden.  ')
    self.tot = True
    mänx.erhalte("Aphrodiikensamen", 5)
    return sgh(self, mänx)


def ruboic_reden_thierca(self: NSC, mänx: Mänx):
    mint('"thiersca ja?, du erinnnest mich an men Tochterle. Wisst de?!" '
         'Der Mann drückt dir etwas in die Hand. '
         'Dann, '
         'ganz plötzlich fängt er an zu röcheln und fällt tot um.  ')
    self.tot = True
    mänx.erhalte("Bantoriitensamen", 5)
    return sgh(self, mänx)


def ruboic_reden_ares(self: NSC, mänx: Mänx) -> Rückkehr | Fortsetzung:
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
            mint("", kursiv(r"Komm zu mir, komm/komm/komm/komm/"
                            r"komm/komm/komm\komm\komm\komm\komm\/"
                            r"komm\komm\komm\komm\komm\komm\komm/\/"
                            r"komm\komm/komm\komm/komm zu mir"), "")
            if ja_nein(mänx, "Willst du mitkommen?"):
                malp('Irgendwo schien jemand sich zu freuen.')
                kursiv('"Du wirst es sicherlich nicht bereuen."')
                b = random.randint(1, 4)
                if b == 1:
                    return gefängnis_von_gäfdah
                elif b == 2:
                    return mitte.MITTE_EINTRITT
                else:
                    return t2
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
    return sgh(self, mänx)


def ruboic_reden_agaga(self: NSC, mänx: Mänx) -> None:
    malp("Der Mann runzelt die Stirn.")
    mint('"Was willst du?"')
    malp("Dann weiten sich seine Augen und er rennt davon.")
    self.tot = True


def ruboic_reden_suche1(self: NSC, mänx: Mänx) -> None:
    mint("...")
    malp("Der Mann scheint Angst zu haben.")
    malp("Du kannst seine Angst förmlich",
         kursiv(" riechen"), ".")
    malp("Schließlich rennt er weg")
    self.tot = True


def ruboic_reden_suche2(self: NSC, mänx: Mänx) -> None:
    malp("Der Mann blickt zu dir hoch")
    malp("Angst steht in seinen Augen geschrieben.")
    mänx.sleep(4, stunden=0)
    mint("Von der einen Sekunde auf die andere ist er verschwunden.")
    self.tot = True


ruboic.dialog("hallo1",
              '"Hallo Ich heiße Tom"',
              ["Tja mi kans egal sän"], gruppe="bluu")

ruboic.dialog("hallo2",
              '"Hallo Ich heiße Makc"',
              ruboic_reden_makc, gruppe="bluu")

ruboic.dialog("hallo3",
              '"Hallo Ich heiße Thierca"',
              ruboic_reden_thierca, gruppe="bluu")

ruboic.dialog("hallo4",
              '"Hallo Ich heiße Ares"',
              ruboic_reden_ares, gruppe="bluu")

ruboic.dialog("hallo5",
              '"Hallo, wie heißt du?"',
              "Äch ben Hätrik", wiederhole=1)

ruboic.dialog("geht", '"Wie geht es dir?"', "Mi gätc gout.")
ruboic.dialog("wetter",
              '"Wie findest du das Wetter heute?"',
              "Gut, ne und?")
ruboic.dialog("agaga",
              "Aggagagaggagrrrrrrrr!!!!  Ähäsifowipppfff Ich binne v'ückt bööö...",
              ruboic_reden_agaga)
ruboic.dialog("suche",
              "Hallo Ich such so 'nen sabbernden Verrückten. "
              "Haste'n geseh'n?",
              ruboic_reden_suche1)
ruboic.dialog("suche2",
              "Tag. "
              "Ich hätte eine Frage. "
              "Hier soll es einen Verrückten geben, "
              "so einen sabbernden. Haben sie zufälligerweise einen gesehen? "
              "Wenn ja wäre es sehr nett, "
              "wenn sie mich davon unterrichten würden. "
              "Ich danke ihnen schon einmal im vorraus.",
              ruboic_reden_suche2)
