from time import sleep
from xwatc import haendler
from xwatc import scenario
from xwatc import weg
from xwatc import system
from xwatc.system import (Mänx, minput, ja_nein, register,
                          Spielende, mint, sprich, kursiv, malp, get_classes)
from xwatc import dorf
from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner, Dialog
from random import randint
import random
from xwatc.jtg.ressourcen import zufälliger_name
from xwatc.jtg.tauern import land_der_kühe
from xwatc.jtg import groekrak, see, nord
from xwatc.haendler import Preis
from xwatc.jtg.groekrak import zugang_südost
from xwatc.jtg import eo_nw
from xwatc.untersystem.acker import Wildpflanze
from xwatc.weg import Ereignis
from typing import List, Tuple


def t2(mänx: Mänx) -> None:
    """Jaspers Teilgeschichte"""
    print("Es erwartet dich Vogelgezwitscher.")
    weg.wegsystem(mänx, "jtg:mitte")


def lichtung_gucken(mänx: Mänx):
    if not mänx.welt.ist("jtg:var:gänseblümchen"):
        mänx.welt.setze("jtg:var:gänseblümchen")
        mint("Du findest Blumen auf der Lichtung.")
        mänx.erhalte("Gänseblümchen", 3)
    mint("Wenn du genau hinsiehst, erkennst du, dass hier ein Pfad von "
         "Norden nach Süden auf einen von Westen trifft. Im Osten sind "
         "nur Büsche.")


@system.register("jtg:beeren")
def beeren() -> Wildpflanze:
    return Wildpflanze(2, {"Beere": 10}, "Du findest Beeren.")


@weg.gebiet("jtg:mitte")
def erzeuge_mitte(_mänx: Mänx) -> 'weg.Wegpunkt':
    westw = weg.Weg(2, weg.WegAdapter(None, groekrak.zugang_ost,
                                      "jtg:mitte:west"), None)
    bogen = weg.Wegkreuzung(w=weg.Richtung(westw))
    bogen.add_beschreibung("Der Weg macht nach einer Weile eine Biegung "
                           "nach rechts.", nur="n")
    bogen.add_beschreibung("Der Weg macht einen Bogen nach links, nach Norden.",
                           nur="w")
    west = weg.Wegkreuzung()
    west.verbinde_mit_weg(bogen, 0.4, "s", typ=weg.Wegtyp.WEG)

    nordw = weg.Weg(5, weg.WegAdapter(None, t2_norden, "jtg:mitte:nord"), None)
    nordk = weg.Wegkreuzung(n=weg.Richtung(nordw))
    nordk.verbinde_mit_weg(west, 3, "sw", "n")

    süd = weg.WegAdapter(None, t2_süd)
    osten = weg.Wegkreuzung()
    osten.add_effekt(system.Besuche("jtg:beeren").main)
    osten.add_beschreibung("Du kommst hier nicht weiter. Umkehren?")

    lichtung = weg.Wegkreuzung(
        s=weg.Richtung(süd, typ=weg.Wegtyp.PFAD),
        gucken=lichtung_gucken)
    lichtung.verbinde_mit_weg(nordk, 3, "n", typ=weg.Wegtyp.PFAD)
    lichtung.verbinde_mit_weg(west, 4, "w", typ=weg.Wegtyp.TRAMPELPFAD)
    lichtung.add_beschreibung(
        "Du befindest sich auf einer Lichtung in einem Wald.", nur=[None])
    lichtung.add_beschreibung(
        "Du kommst auf eine Lichtung.", außer=[None, "o"])
    lichtung.add_beschreibung((
        "Ein schmaler Pfad führt nach Norden.",
        "Im Osten ist Dickicht.",
        "Im Westen und Süden ist nichts besonderes."
    ))

    osten.verbinde(lichtung, "w", weg.Wegtyp.TRAMPELPFAD)
    lichtung.verbinde(osten, "o", weg.Wegtyp.TRAMPELPFAD)
    return lichtung

# TODO: print("Der kleine Pfad stößt spitz auf einen Weg von links.")


@register("jtg:mädchen")
class Mädchen(haendler.Händler):
    """Mädchen am Weg nach Norden.

    Stand: Bürger
    Familie: Vater, Onkel, Opa, Oma
    Hintergrund: Nach dem Tod ihrer Mutter (Kauffrau) wollte ihr Vater
        (Sekretär)
         sie schnell loswerden
        und dazu an den nächstbesten verheiraten. Sie floh nach Norden.
    """

    def __init__(self) -> None:
        super().__init__("Mädchen", kauft=["Kleidung"], verkauft={
            "Rose": (1, Preis(1))
        }, gold=Preis(0), art="Mädchen",
            direkt_handeln=True, startinventar={
                "BH": 1,
                "Unterhose": 1,
                "Socke": 2,
                "Schuh": 2,
                "Lumpen": 1,
        })
        self.in_disnajenbum = True
        self.dialog("hallo", "Hallo, kann ich dir helfen?", Mädchen.hallo)
        self.dialog("rose", "Woher hast du die Rose?",
                    ["Die Rosen wachsen hier im Wald, aber es ist gefährlich,"
                     " sie zu holen."], "hallo")
        self.dialog("woher", "Woher kommst du?",
                    ["Ich komme aus Grökrakchöl, das liegt im Süden."],
                    "hallo", wiederhole=1)
        self.dialog("heißt", "Wie heißt du?", Mädchen.heißt, "hallo")
        self.dialog("allein", "Warum bist du allein? Hast du einen Grund, nicht nach "
                    "*Grökaköl zurückkehren zu können?",
                    [
                        dorf.Malp("Das Mädchen zögert etwas."),
                        "Ich ...",
                        "Ich bin geflohen. Nach dem Tod meiner Mutter hatte "
                        "meine Familie finanzielle Schwierigkeiten.",
                        "Ich sollte verheiratet werden.",
                        "Darüber gerieten wir in Streit, und ich floh, um "
                        "zu meinen Großeltern in Gibon zu kommen."
                    ], "woher", min_freundlich=10, wiederhole=1)
        self.dialog("helfen", "Das ist ja schrecklich! Ich helfe dir, nach "
                    "Gibon zu kommen.", Mädchen.helfen, "allein")

    def hallo(self, _mänx: Mänx):
        if self.hat_item("Rose"):
            self.sprich("Willst du für ein Gold eine Rose kaufen?")
            mint("Das Mädchen spricht leise und vorsichtig, mit merkbar "
                 "schlechten Gewissen, denn eine Rose ist kein ganzes Gold "
                 "wert.")
        else:
            self.sprich("Du hast mir mit dem Gold schon genug geholfen.")
            mint("Sie nickt mit dem Kopf, um dir zu danken.")

    def heißt(self, _mänx: Mänx):
        self.name = "Älen Kafuga"
        self.sprich("Älen, Älen Kafuga", warte=True)

    def helfen(self, mänx: Mänx):
        self.sprich('Willst du auch nach Gibon?')
        opts: List[Tuple[str, str, str]]
        opts = [
            ('»irgendwann«', "irgendwann",
             '"Nein, ich erkunde hier die Gegend, irgendwann werde ich nach Gibon kommen."'
             "Kann ich dann trotzdem mit dir mit? Es macht mir nichts aus, "
             "wenn wir nicht direkt nach Gibon gehen."),
            ("»ja«", 'ja', "Dann gehe ich mit dir mit."),
            ("»nein«", '»Nein, aber ich kann dich trotzdem dahin bringen.«', 
             "Ist das wirklich in Ordnung? Danke!")
        ]
        antwort = mänx.menu(opts)
        self.sprich(antwort)
        self.werde_gefährte()
        mänx.add_gefährte(self)

    def werde_gefährte(self):
        """Mache das Mädchen zum Gefährten."""
        self.dialoge.clear()
        self.dialog("gibon", '"Wo ist Gibon eigentlich?"',
                    ["In Tauern, direkt hinter der Grenze.",
                     "Tauern liegt im Nordosten von Jotungard."])
        self.dialog("umarmen", '"Kann ich dich umarmen?"', Mädchen.umarmen,
                    min_freundlich=30)
        self.dialog("großeltern", '"Wie sind deine Großeltern so?"',
                    ["Mein Aba ist ein strenger Mann. Er schätzt Disziplin "
                     "über alles, aber er ist eigentlich ganz nett.",
                     "Meine Ama ist emotional sehr intelligent. Sie ergänzen "
                     "sich echt gut.",
                     "Ich habe sie selten gesehen, weil sie weit weg wohnen "
                     "und sie meinen Vater nicht schätzten."
                     ])
        self.dialog("grökrakchöl", '„Hast du keine Bekannten mehr in Grökrakchöl?"',
                    ["Nein, zumindest keine, die ich sehr gut kenne.",
                     ])
        self.dialog("waffe", '', [
            "Ich hätte gerne eine Waffe.",
            "Ich muss mich doch irgendwie wehren können."
            "Dann kann ich dir auch helfen."
        ], direkt=True, wiederhole=0).wenn(
            lambda n, __: not n.hat_klasse("Waffe"))
        self.in_disnajenbum = False

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        if self.in_disnajenbum:
            yield ("handeln", "handel", self.handeln)
        yield from NSC.optionen(self, mänx)

    def umarmen(self, mänx: Mänx):
        if self.freundlich >= 80:
            self.sprich("Gerne?")
            malp("Ihr umarmt euch")
            return
        opts = [
            ("einfach so", '"Einfach so."', "e"),
            ("einsam", '"Ich bin etwas einsam."', "einsam"),
            ("mag", '"Ich mag dich."', "mag"),
            ("kalt", '"Mir ist kalt."', "kalt"),
        ]
        ans = mänx.menu(opts, '„Warum?"')
        if ans == "e":
            self.sprich("Äh, okay...")
            malp("Du umarmst sie kurz. Sie schaut weg.")
        elif ans == "einsam":
            self.sprich("..")
            malp("Ihr umarmt euch.")
            self.sprich("Ich auch.", wie="flüstert")
            self.add_freundlich(10, 60)
        elif ans == "mag":
            if self.freundlich >= 60:
                self.sprich("Das ist so plötzlich", wie="errötet")
                self.sprich("..")
                self.sprich("Ich mag dich auch.")
                # unverbindlich?
                malp("Ihr umarmt euch")
                self.freundlich += 20
            else:
                self.sprich("Sagst du so etwas zu jedem Mädchen, das dir "
                            "über den Weg läuft?", warte=True)
                malp("Sie stößt dich weg.")
                self.add_freundlich(-2, 30)
        else:  # "kalt"
            if len(mänx.gefährten) <= 2:
                self.sprich("Naja, mir ist auch kalt.")
                malp("Ihr wärmt euch gegenseitig.")
                self.add_freundlich(5, 40)
            else:
                self.sprich("Hier sind genug andere Ninen. Warum mich?")
                malp("Sie geht davon.")

    def vorstellen(self, mänx):
        print("Am Wegesrand vor dem Dorfeingang siehst du ein Mädchen in Lumpen. "
              "Sie scheint zu frieren.")

    def get_preis(self, _) -> Preis:
        return Preis(0)

    def kampf(self, mänx: Mänx) -> None:
        print("Das Mädchen ist schwach. Niemand hindert dich daran, sie "
              "auf offener Straße zu schlagen.")
        print("Sie hat nichts außer ihren Lumpen.", end="")
        if self.hat_item("Rose"):
            print(
                ", die Blume, die sie dir verkaufen wollte, ist beim Kampf zertreten worden.")
        else:
            print(".")
        del self.inventar["Rose"]
        self.plündern(mänx)

    def verkaufen(self, mänx: Mänx, name: str, preis: Preis, anzahl: int=1)->bool:
        ans = super().verkaufen(mänx, name, preis, anzahl=anzahl)
        if ans and name == "Unterhose":
            malp("Das Mädchen ist sichtlich verwirrt, dass "
                 "du ihr eine Unterhose gegeben hast.")
            mint("Es hält sie vor sich und mustert sie. Dann sagt sie artig danke.")
            mänx.titel.add("Perversling")
        elif ans and name == "Mantel":
            malp("Das Mädchen bedeutet dir, dass sie nur den halben Mantel braucht.")
            malp("Du schneidest den Mantel entzwei, und gibst ihr nur die Hälfte.")
            mänx.inventar["halber Mantel"] += 1
            mänx.titel.add("Samariter")
            self.freundlich += 10
        return ans

    def kaufen(self, mänx: Mänx, name: str, anzahl: int=1)->bool:
        ans = super().kaufen(mänx, name, anzahl=anzahl)
        if ans and name == "Rose":
            malp("Das Mädchen ist dankbar für das Stück Gold")
            self.freundlich += 10
        return ans


def t2_norden(mänx: Mänx) -> None:
    """Das Dorf auf dem Weg nach Norden"""
    print("Auf dem Weg kommen dir mehrfach Leute entgegen, und du kommst in ein kleines Dorf.")
    mädchen = mänx.welt.obj("jtg:mädchen")
    if mädchen.in_disnajenbum and not mädchen.tot:
        mädchen.main(mänx)
        malp("Das Mädchen verschwindet nach Süden.")
        mädchen.in_disnajenbum = False
        # TODO wohin?
    disnayenbum(mänx)


def disnayenbum(mänx: Mänx):
    mint("Du kommst im Dorf Disnayenbun an.")
    nex = scenario.lade_scenario(mänx, "disnajenbun")
    if "osten" == nex:
        mint("Du verlässt das Dorf Richtung Osten.")
        t2_no(mänx)
    elif nex == "westen":
        mint("Du verlässt das Dorf Richtung Nordwesten.")
        eo_nw.eo_ww_o(mänx)
    else:  # süden
        mint("Du verlässt das Dorf Richtung Süden.")
        weg.wegsystem(mänx, "jtg:mitte:nord")


def t2_süd(mänx) -> None:
    print("Der Wald wird immer dunkler.")
    mint("Ein kalter Wind weht. Das Vogelgezwitscher der Lichtung kommt dir nun "
         "wie ein kurzer Traum vor.")
    mint("Es wird immer dunkler.")
    print("Plötzlich siehst du ein Licht in der Ferne.")
    haus = ja_nein(mänx, "Gehst du zum Licht?")
    if haus:
        print("Es ist eine einsame, einstöckige Hütte, aus der das Licht kam. "
              "Vor dir ist die Rückseite des Hauses, "
              "an der sich Feuerholz stapelt.")
        haus = ja_nein(mänx, "Klopfst du an die Tür?")
    if haus:
        print("Ein junger Mann begrüßt dich an der Tür.")
        if mänx.rasse == "Skelett":
            hexer_skelett(mänx)
        else:
            aktion = mänx.minput(
                '?: "Ein Wanderer? Komm herein, du siehst ganz durchgefroren aus."[k/r/f]',
                list("krf"))
            if aktion == "f":
                print("Du rennst weg, als hätte der bloße Anblick "
                      "des jungen Manns dich verschreckt.")
                print('Jetzt denkt der Arme sich bestimmt: "Bin ich so hässlich '
                      'oder schrecklich, dass Leute auf den '
                      'ersten Blick abhauen?"')
                print("Aber dir ist das egal, die unbekannte Gefahr ist abgewehrt.")
                ende_des_waldes(mänx)
            elif aktion == "k":
                print('?: "Ein/e Inquisitor/in? Dafür musst du früher aufstehen!"')
                hexer_kampf(mänx)
            else:  # "r"
                haus_des_hexers(mänx)
    else:
        print("Dem, der auch immer hinter dem Licht steckt, sollte man nicht "
              "trauen, befindest du und machst "
              "dich weiter "
              "auf den Weg durch den Wald.")
        ende_des_waldes(mänx)


def hexer_skelett(mänx: Mänx):
    mänx.welt.setze("kennt:hexer")
    sprich("?", "Ach hallo, ein Skelett! Fühl dich hier wie zu Hause.")
    leo = "Leo Berndoc"
    sprich(leo, "Ich habe ganz vergessen, mich vorzustellen!")
    sprich(leo, "Ich bin Leo Berndoc.")
    ende_des_waldes(mänx, True)


def haus_des_hexers(mänx: Mänx)-> None:
    print("Er bittet dich an den Tisch und gibt dir einen warmen Punsch.")
    mänx.welt.setze("kennt:hexer")
    leo = 'Leo Berndoc'
    sprich(leo, "Ich bin Leo Berndoc.")
    sprich(leo, "Was suchst du in diesem Wald?")
    opts = [
        (o, v, v) for (o, v) in zip((
            "Halloli! Was mach ich wohl in deinem Haus? ",
            "Ich habe mich hier verirrt.",
            "Ich bin nur auf der Durchreise.",
            "Die große Liebe!",

            "Das gehst dich doch nichts an!",
        ),
            ["halloli", "verirrt", "durchreise", "liebe", "an"])
    ]
    if mänx.welt.ist("jtg:t2"):
        opts.append(("Ich bin einfach in den Osten ­– weil da keine Menschen sind – gegangen, "
                     "und dann war da diese Oase. Da waren zwei Türen. "
                     "Ich habe mir ein Herz gefasst, bin durch die Tür gegangen und hier "
                     "bin ich. Plötzlich.", "oase", "oase"))
    antwort = mänx.menu(opts)
    if antwort == "halloli":
        print("Er sagt mit einem verschwörerischen Tonfall: \"Ich verstehe.\"")
        sprich(leo, "Bleibe ruhig noch die Nacht. Hier werden sie dich nicht finden.")
        print("Du entschließt dich, mitzumachen. Am nächsten Tag verlässt du "
              "schnell das Haus, bevor der Schwindel "
              "auffliegt")
        ende_des_waldes(mänx, True)
    elif antwort == "verirrt" or antwort == "an":
        sprich(leo, "Soso.")
        sleep(1)
        sprich(leo, "...")
        sleep(1)
        sprich(leo, "Ich habe ein Gästebett. Da kannst du schlafen.")
        print("Dein erstes Bett in dieser Welt ist schön weich.")
        sleep(3)
        print("Als du am nächsten Morgen aufwachst, fühlst du dich schwach und kalt.")
        print("Leo steht vor dir.")
        sprich(leo, "Du bist jetzt eine wandelnde Leiche und gehorchst meinem Willen")
        raise Spielende()
    elif antwort == "durchreise":
        sprich(leo, "Schade. Trotzdem–Schön, dich getroffen zu haben. Im Süden ist ein Dorf, "
               "da kannst du als nächstes hin.")
        sprich(leo, "Du musst einfach immer geradeaus dem schmalen Pfad folgen.")
        ende_des_waldes(mänx)
    elif antwort == "liebe":
        sprich(
            leo, "Glaubst du denn an die wahre Liebe, die, die alle Widrigkeiten überwindet?")
        if ja_nein(mänx, "Ja/Nein"):
            sprich(leo, "Du bist also eine/r von denen!")
            sprich(leo, "Ich schwöre auf meinen Namen, ich werde dich hier auslöschen!")
            sleep(1)
            sprich(leo + "(flüstert)", "Ich werde Lena rächen.")
            hexer_kampf(mänx)
        else:
            sprich(leo, "Und warum nicht?")
            ant = mänx.minput(
                "Weil Liebe Ordnung haben muss. Auch die Liebe kann sich nicht über "
                "alles hinwegsetzen.[1]/\n"
                "Dass sie alles Widrigkeiten überwindet, das ist zu optimistisch. Aber "
                "ich werde nie aufgeben.[2]/\n"
                "Diese Liebe meine ich nicht. Ich meine die Nächstenliebe, das Gute im "
                "Menschen und die Güte Gottes. Die habe ich in deiner Gastfreundschaft "
                "gefunden.[3]")
            if ant == "2":
                sprich(leo, "Du bist also eine/r von denen!")
                sprich(leo, "Du denkst, nur weil du liebst, kann du "
                       "die Ehre der Berndoc ignorieren und "
                            "mit ihr zusammenkommen!")
                sleep(0.5)
                sprich(
                    leo, "Ich schwöre auf meinen Namen, ich werde dich hier auslöschen!")
                hexer_kampf(mänx)
            else:
                sprich(leo, "Interessant.")
                sprich(leo, "Ich habe ein Gästebett. Da kannst du schlafen.")
                sprich(leo, "Im Süden ist ein Dorf, lauf einfach weiter geradeaus.")
                print("Dein erstes Bett in dieser Welt ist schön weich.")
                sleep(5)
                ende_des_waldes(mänx, True)
    else:  # oase
        sprich(leo, "Interessant.")
        print("Er wirkt sichtlich überfordert.")
        sprich(leo, "Das muss eine Tür der Qual sein..., oder war es Wal der Qual...")
        sleep(0.3)
        sprich(leo, "Aber was hat ein Wal hier zu suchen?")
        print("Du hast ihn sichtlich verwirrt.")
        mint("Er zeigt noch auf ein Gästezimmer, dann geht er vor "
             "sich hin brabbelnd in sein Zimmer")
        mint("Im Bett denkst du über deinen heutigen Tag nach. Du sinkst "
             "in einen unruhigen Schlaf.")
        sleep(5)
        print("Früh am Morgen verlässt du eilig das Haus.")
        mint("Aber du siehst noch einen Ring auf dem Tisch.")
        if ja_nein(mänx, "Steckst du ihn ein?"):
            mänx.erhalte("Ring des Berndoc")
        sprich(leo, "Ich hab's! Es ist ein Wahlqualportal!!!")
        ende_des_waldes(mänx, True)


def hexer_kampf(mänx):
    print("Der Mann spricht einen schnellen Zauberspruch. Dir wird unglaublich kalt.")
    if mänx.get_kampfkraft() > 2000:
        print("Aber du bist stärker.")
        print("Du besiegst den Mann und plünderst sein Haus.")
        mänx.erhalte("Gold", 120)
        mänx.erhalte("Mantel", 3)
        mänx.erhalte("Unterhose", 7)
        mänx.erhalte("Banane", 1)
        mänx.erhalte("Menschenskelett", 3)
        print("Du findest einen Ring. In ihm steht eingraviert: "
              "\"Ich hasse dich, Dongmin!\"")
        mänx.erhalte("Ring des Berndoc")
        print("Du entscheidest dich, nach Süden weiter zu gehen.")
        sleep(2)
    else:
        print("Du kannst dich kaum bewegen. Er tritt auf dich drauf.")
        sleep(0.5)
        print("Dein Rücken tut weh")
        sleep(0.5)
        print("Aber er zeigt Gnade. ", end="")
        hose = mänx.inventar["Unterhose"]
        if hose:
            print("Er zieht dich bis auf die Unterhose aus", end="")

        else:
            print("Er zieht dich aus, verzieht das Gesicht, als er sieht, "
                  "dass du keine Unterhose trägst", end="")
        print(" und wirft dich im Süden des Waldes auf den Boden")
        mänx.inventar.clear()
        mänx.inventar["Unterhose"] = hose
    ende_des_waldes(mänx)


SÜD_DORF_GENAUER = [
    "Das Dorf besteht aus einer Handvoll Holzhütten sowie zwei Fachwerkhäusern.",
    "Die meisten Dorfbewohner glauben an den Gott des Marschlandes, "
    "wie an den Schnitzereien an den Türrahmen erkennbar",
    "Die Dorfbewohner haben größtenteils schwarze Haare und leicht gebräunte "
    "Haut.",
    "Im Süden des Dorfes ist ein kleiner Fluss."
]
SÜD_DORF_NAME = "Scherenfeld"


@register("jtg:m:tobiac")
class TobiacBerndoc(NSC):
    def __init__(self) -> None:
        super().__init__("Tobiac Berndoc", "Orgelspieler")
        cls = type(self)
        self.dialog("orgel",
                    '"Warum spielst du Orgel? Es ist doch nicht Gottesdienst gerade?"',
                    cls.reden_orgel)
        self.dialog("lernen",
                    '"Kannst du mir beibringen, Orgel zu spielen?"',
                    cls.reden_lernen)
        self.dialog("leo", '"Was ist dein Verhältnis zu Leo Berndoc?"',
                    cls.reden_leo).wenn(lambda n, m: m.welt.ist("kennt:hexer"))
        self.dialog("wetter",
                    '"Wie findest du das Wetter heute?"', cls.reden_wetter)
        self.dialog('ring',
                    "Den Ring vorzeigen", cls.ring_zeigen).wenn(
                        lambda n, m: m.hat_item("Ring des Berndoc"))
        self.dialog('wo', '"Wo bin ich?"', cls.reden_wo_bin_ich)

    def kampf(self, mänx: Mänx) -> None:
        if mänx.hat_klasse("Waffe", "magische Waffe"):
            print("Er ist so sehr in sein Orgelspiel vertieft, dass er seinen "
                  "Tod nicht kommen sieht.")
            mint("Er fällt auf die Klaviatur, und "
                 "sein letztes Lied endet jäh in einer langen Dissonanz.")
            mint("Er hatte nichts von Wert an sich.")
            self.tot = True
        else:
            print("Du prügelst auf ihn ein, aber er wehrt sich nicht.")
            if ja_nein(mänx, "Machst du weiter?"):
                mint("Du schlägst ihn bewusstlos")

    def zuhören(self, _mänx: Mänx) -> None:
        mint("Tobiac spielt einfach weiter Orgel.\n"
             "Du hast das Gefühl, er hat dich bemerkt, aber er lässt sich "
             "nichts anmerken.")
        sleep(2)
        mint("Du gibt dich der Melodie hin.")

    def vorstellen(self, mänx: Mänx) -> None:
        print("Tobiac spielt erst noch den Satz zu Ende.")
        sleep(2)
        print("Er spricht mit leiser Stimme.")
        sprich(self.name, f"Hallo, ich bin {self.name}.")
        sprich("Du", "Ich bin $&%!")

    def reden_orgel(self, mänx: Mänx) -> None:
        sprich(self.name, "Ich spiele gerne Orgel. "
               "Es beruhigt mich ungemein.")
        sprich(self.name, "Wenn nur mein Sohn auch so gerne wie ich spielen würde.")
        sprich(self.name, "Ich bin nie zu Hause und spiele lieber Orgel. "
               "Und mein Sohn spielt lieber bei den Nachbarn nebenan.")
        if ja_nein(mänx, self.name + " :Ich bin ein schlechter Vater, nicht?"):
            sprich(self.name, "Es tut irgendwie doch weh, es so zu hören.")
        else:
            sprich(self.name, "Danke.")

    def reden_lernen(self, mänx: Mänx) -> None:
        sprich(self.name, "Ja, gerne!")
        mint("Tobiac ist sofort voll in seinem Element. Dir ist, als wäre "
             "er einsam und froh über deine Gesellschaft.")
        mint("Du bleibt einige Tage bei ihm und lernst sein Handwerk.")
        mänx.welt.nächster_tag(11)
        mint("Je länger du übst, desto mehr siehst du, dass er so gut spielt "
             "wie kein anderer.")
        mänx.fähigkeiten.add("Orgel")

    def reden_wetter(self, mänx: Mänx) -> None:  # pylint: disable=unused-argument
        sprich(self.name + "(zögert kurz)", "Schön sonnig, nicht?")
        print("Draußen war es bewölkt.")
        mint("Wie lange war Tobiac wohl nicht mehr draußen?")

    def reden_leo(self, mänx: Mänx):  # pylint: disable=unused-argument
        sprich(self.name, "Er ist mein Bruder, aber er hat sich in den "
               "Wald zurückgezogen. Ich habe lange nicht mehr von ihm gehört.")
        sprich(self.name, "Er war auch vorher sehr zurückgezogen.")
        sprich(self.name, "Warum fragst du?")
        return True

    def ring_zeigen(self, mänx: Mänx) -> bool:
        self.sprich("Das ist doch der Ring unserer Familie!")
        self.sprich("Warte. Ich werde nicht fragen, wo du ihn her hast.")
        print("Du gibst ihm den Ring des Berndoc")
        self.inventar["Ring des Berndoc"] += 1
        mänx.inventar["Ring des Berndoc"] -= 1
        return True

    def reden_wo_bin_ich(self, mänx: Mänx) -> bool:  # pylint: disable=unused-argument
        self.sprich(f"Du bist in {SÜD_DORF_NAME}, im Reich Jotungard.")
        return True

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        yield from super().optionen(mänx)
        yield ("Ihm beim Spielen zuhören", "hören", self.zuhören)

    def main(self, mänx: Mänx) -> None:
        print("Tobiac spielt auf der Orgel.")
        print("Die Melodie klingt ungewöhnlich, aber sehr schön.")
        super().main(mänx)


class Waschweib(Dorfbewohner):
    def __init__(self):
        name = zufälliger_name()
        super().__init__(name, geschlecht=False)
        self.art = "Hausfrau"
        self.verheiratet = random.random() > 0.4
        if self.verheiratet:
            self.inventar["Schnöder Ehering"] += 1
        elif random.random() > 0.5:
            self.inventar["Gänseblümchen"] += 5
        self.inventar["Einfaches Kleid"] += 1
        self.inventar["Unterhose"] += 1
        self.inventar["BH" if random.random() < 0.6 else "Großer BH"] += 1
        if random.random() > 0.8:
            self.inventar["Haarband"] += 1
            self.inventar["Armband"] += 2
        self.inventar["Socke"] += 2
        self.gold += max(0, random.randint(-4, 10))
        self.direkt_reden = True


def gar_kampf(nsc, mänx: Mänx) -> None:
    nsc.sprich("Hilfe!")
    nsc.freundlich -= 40
    if nsc.ort:
        hilfe = nsc.ort.melde(mänx, Ereignis.KAMPF, [nsc])
        if hilfe:
            malp("Sofort eilen Leute zur Hilfe.")
            malp("Du siehst dich umzingelt.")
            if mänx.ja_nein("Ergibst du dich?"):
                nsc.sprich("Warum hast du mich angegriffen?")
                rechtfertigen(mänx, nsc, hilfe)
            else:
                malp("Du wirst schnell überwältigt, aber weil du zu "
                     "stark bist, können sie dich leider nicht lebendig "
                     "fangen.")
                raise Spielende
            return
        else:
            malp("Gerade ist niemand da, der helfen könnte.")
    else:
        malp("Hier ist niemand, der helfen könnte.")
    malp("Du bringst ihn um und plünderst ihn aus.")
    nsc.plündern(mänx)
    nsc.tot = True


def rechtfertigen(mänx: Mänx, nsc, hilfe):
    opts = [
        ("Weil du lecker aussahst.", "lecker", "mord"),
        ("Mir war gerade danach", "danach", "mord"),
        ("Du hast mich schief angeguckt.", "schief", "mord"),
        ("Er hat mich bestohlen!", "diebstahl", "diebstahl"),
        ("Tut mir leid, kommt nie wieder vor!", "tut", "ent"),
        ("Er hat mich bespuckt!", "bespuckt", "bespuckt"),
    ]
    random.shuffle(opts)
    ans = mänx.menu(opts)
    if ans == "mord":
        hilfe[0].sprich("Das ist keine gute Rechtfertigung!")
        hilfe[0].sprich("Mord dulden wir hier nicht.")
        raise Spielende  # TODO: Verbrecher
    elif ans == "diebstahl":
        val = ""
        while not val:
            val = mänx.minput(hilfe[0].name + ': "Was soll er denn gestohlen haben?"',
                              lower=False)
        if {"Kleidung", "Nahrung"} & set(get_classes(val)):
            hilfe[0].sprich("Kleidung oder Essen zu stehlen ist kein Verbrechen,"
                            " das man "
                            "mit Waffengewalt lösen sollte.")
            hilfe[0].sprich("Wir lassen dich diesmal gehen.")
        else:
            hilfe[0].sprich("Durchsuchen wir ihn!")
            if nsc.hat_item(val):
                hilfe[0].sprich("Er hat tatsächlich ein/-e {val}")
                nsc.erhalte(val, von=nsc)
            else:
                hilfe[0].sprich("Du lügst. Der Junge ist unschuldig.")
                hilfe[0].sprich("Mord dulden wir hier nicht.")
                raise Spielende
    elif ans == "ent":
        hilfe[0].sprich("Hoffen wir das mal.")
        for helfer in hilfe:
            helfer.freundlich -= 40
    else:  # ans == "bespuckt":
        hilfe[0].sprich("Das ist kein Grund, einfach auf jemanden loszugehen!")
        try:
            if nsc.ort.dorf.name == SÜD_DORF_NAME:
                hilfe[0].sprich("Tu das nie wieder!")
                return
        except AttributeError:
            pass
        hilfe[0].sprich("Du hast unseren kleinen Gaa angegriffen, das "
                        "verzeihen wir dir nicht!")
        raise Spielende


@register("jtg:süd:garnichts")
def garnichts() -> NSC:
    nichts = NSC("Gaa Nix", "Junge", gar_kampf, direkt_reden=True,
                 startinventar=dict(
                     Schuh=1,
                     Socke=2,
                     Tomate=4,
                     Banane=2,
                     Ring=1,
                     Lederhose=1,
                     Unterhose=1,
                     Leinenhemd=1,
                     Oberhemd=1,
                 ),
                 vorstellen=[
                     "Ein sommersprössiger Junge mit braunen Haaren "
                 ])
    return nichts


zufälliges_waschweib = Waschweib


def süd_dorf_wo(nsc: NSC, _mänx: Mänx):
    nsc.sprich("Dieses Dorf ist " + SÜD_DORF_NAME + ".")
    nsc.sprich("Dort (zeigt nach Osten) geht es nach Disnayenbum und "
               "nach Tauern.")
    nsc.sprich("Dort (zeigt nach Süden) geht es zur Hauptstadt. Ich würde da "
               "nicht hingehen, wenn ich du wäre. Da sind zu viele Monster.")
    nsc.sprich("Und zuletzt geht es noch da (zeigt nach Westen) nach "
               "Grökrakchöl.")
    mint("Grö-Kra-krö?")
    nsc.sprich("Nein, Gröh-Kra-Kchöhl. Das ist eine Grenzbefestigung.")
    return True


def süd_dorf_grenzen(nsc: NSC, _mänx: Mänx):
    nsc.sprich("Nach Tauern und Eo natürlich.")
    nsc.sprich("In Tauern leben Taurer, das sind keine Menschen, sondern Wesen "
               "mit Köpfen, die Kühen ähneln.")
    if isinstance(nsc, Waschweib):
        nsc.sprich("Ich finde Kühe aber niedlicher.")
    nsc.sprich("Und Eo...")
    nsc.sprich("Wir führen zwar keinen Krieg gegen sie, aber die Beziehungen "
               "sind schlecht. Sie lassen uns nicht herein.")
    return True


def süd_dorf_norden(nsc: NSC, _mänx: Mänx):
    nsc.sprich("Meinst du den Wald?")
    nsc.sprich("Da würde ich nicht hineingehen. Da lebt ein Hexer oder so.")
    nsc.sprich("Aber er hält uns die Monster vom Leib. Ist also nicht so, als "
               "ob das nur schlecht wäre.")
    return True


SÜD_DORF_DIALOGE = [
    Dialog("wo", '"Wo bin ich hier?"', süd_dorf_wo),
    Dialog("grenzen", '"Welche Grenzen?"', süd_dorf_grenzen, "wo"),
    Dialog("norden", '"Was ist mit dem Norden?"', süd_dorf_norden, "wo"),
]


def ende_des_waldes(mänx, morgen=False):
    mänx.welt.nächster_tag()
    print("Der Wald wird schnell viel weniger unheimlich")
    if not morgen:
        print("Erschöpft legst du dich auf den Waldboden schlafen.")
        sleep(2)
    print("Im Süden siehst du ein Dorf")
    süd_dorf(mänx)


def erzeuge_süd_dorf(mänx) -> Dorf:
    do = Dorf(SÜD_DORF_NAME)
    kirche = Ort("Kirche", do, [
        "Du bist in einer kleinen Kirche.",
        # Tobiac tot?
        "Im Hauptschiff ist niemand, aber du hörst die Orgel"
    ])
    mänx.welt.obj("jtg:m:tobiac").ort = kirche
    mänx.welt.obj("jtg:süd:garnichts").ort = kirche
    for _i in range(randint(2, 5)):
        w = Waschweib()
        w.dialoge.extend(SÜD_DORF_DIALOGE)
        w.ort = do.orte[0]
    # TODO weitere Objekte
    return do


def süd_dorf(mänx: Mänx):
    mänx.genauer(SÜD_DORF_GENAUER)
    mänx.welt.get_or_else("jtg:dorf:süd", erzeuge_süd_dorf, mänx).main(mänx)
    ziele = [
        ("Den Weg nach Süden zur Hauptstadt", "hauptstadt", hauptstadt_weg),
        ("Den Weg nach Norden nach Tauern", "tauern", tauern_ww_süd),
        ("Den Weg nach Westen nach Grökrakchöl", "grökrakchöl", zugang_südost),
        #("Den Pfad in den Wald", "wald", wald)
    ]
    mänx.menu(ziele, frage="Wohin gehst du?")(mänx)


def hauptstadt_weg(mänx: Mänx):
    print("Am Wegesrand siehst du ein Schild: \"Achtung Monster!\"")
    if mänx.ja_nein("Willst du wirklich weitergehen?"):
        mon = random.randint(1, 3)
        if mon == 2 or "Kinderfreund" in mänx.titel:
            print("Plötzlich bemerkst du einen süßen Duft und ein sanftes "
                  "Leuchten im Wald zu deiner Rechten.")
            mint("Ehe du dich versiehst, bis du vom Weg abgekommen.")
            print("Du hörst eine sanfte Stimme:")
            sprich("Dryade", "Hier ist es nicht sicher, Wanderer.")
            sprich("Dryade", "Nicht sicher für dich.", warte=True)
            sprich("Dryade", "Schreite durch dieses Portal!")
            if mänx.ja_nein("Ein Portal öffnet sich vor dir. Möchtest "
                            "du hindurch?"):
                print("Du landest an einem vertrauten Ort.")
                mint("Es ist der Ort, wo deine Geschichte begonnen hat.")
                import xwatc_Hauptgeschichte
                xwatc_Hauptgeschichte.himmelsrichtungen(mänx)
            else:
                sprich("Dryade", "Vertraust du mir nicht?")
                mint("Die Stimme verstummt, das Portal schließt sich und "
                     "der Duft verschwindet.")
                print("Plötzlich bist du im dunklen Wald allein.")
                mint("Etwas schweres trifft dich an der Seite und wirft dich "
                     "zu Boden.")
                print("Dass es ein Stein ist, siehst du im Fallen.")
                mint("Du kannst dich nicht mehr bewegen und du siehst im "
                     "Augenwinkel einen Bär auf dich zukommen.")
                raise Spielende
        elif mon == 1:
            mint("Ein Pack Wölfe greift dich an.")
            print("Sie haben die umzingelt, bevor du sie bemerkt hast.")
            if mänx.gefährten:
                mint("Deine Gefährten sterben nach und nach.")
            if mänx.hat_klasse("Waffe"):
                mint("Einen Wolf kannst du noch umbringen, aber einer beißt "
                     "dich von hinten und du sackst zusammen.")
            else:
                mint("Du bist den Wölfen wehrlos ausgeliefert.")
            raise Spielende
        else:  # mon == 3
            mint("Du läufst mitten in einen Hinterhalt der Kobolde.")
            print("Später wird dein Kopf als Schmuck gefunden.")
            raise Spielende
    else:
        süd_dorf(mänx)


def t2_no(mänx):
    print("Du kommst an einen Wegweiser.")
    print("Der Weg gabelt sich an einem kleinen Fluss, links führt der Weg "
          "den Fluss aufwärts zum 'Land der aufrechten Kühe' und rechts "
          "führt der Weg nach flussabwärts nach '" + SÜD_DORF_NAME + "'")
    if mänx.minput("Gehst du nach links oder rechts", ["links", "rechts"]) == "links":
        land_der_kühe(mänx)
    else:
        süd_dorf(mänx)


def tauern_ww_süd(mänx: Mänx):
    print("Du folgst dem Weg sehr lange den Fluss aufwärts.")
    mint("Da kommst du an eine Kreuzung. Ein Weg führt den Fluss weiter aufwärts")


if __name__ == '__main__':
    m = Mänx()
    m.inventar["Speer"] += 1
    t2(m)
