from time import sleep
from xwatc import haendler
from xwatc import scenario
from xwatc import weg
from xwatc import system
from xwatc.system import (
    Mänx, minput, ja_nein, register, MenuOption,
    Spielende, mint, sprich, kursiv, malp, get_classes, Inventar, MänxFkt)
from xwatc import dorf
from xwatc.dorf import Dorf, ort, NSCOptionen, Dialog, HalloDialoge, Malp, Zeitpunkt
from random import randint
import random
from xwatc.jtg.ressourcen import zufälliger_name
from xwatc.jtg.tauern import land_der_kühe
from xwatc.jtg import groekrak, see, nord
from xwatc.jtg.groekrak import zugang_südost
from xwatc.jtg import eo_nw
from xwatc.untersystem.acker import Wildpflanze
from xwatc.jtg import mitose
from typing import List, Tuple
from xwatc.untersystem.verbrechen import Verbrechen, Verbrechensart
from xwatc.nsc import Person, StoryChar, NSC
from collections import defaultdict
from xwatc.weg import wegsystem


def t2(mänx: Mänx) -> None:
    """Jaspers Teilgeschichte"""
    malp("Es erwartet dich Vogelgezwitscher.")
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
def erzeuge_mitte(_mänx: Mänx, gebiet: weg.Gebiet) -> 'weg.Wegpunkt':
    westw = weg.Weg(2, weg.WegAdapter(groekrak.zugang_ost, "west", gebiet), None)
    bogen = weg.kreuzung("bogen", w=weg.Richtung(westw))
    bogen.add_beschreibung("Der Weg macht nach einer Weile eine Biegung "
                           "nach rechts.", nur="n")
    bogen.add_beschreibung("Der Weg macht einen Bogen nach links, nach Norden.",
                           nur="w")
    west = weg.kreuzung("west")
    west.verbinde_mit_weg(bogen, 0.4, "s", typ=weg.Wegtyp.WEG)

    nordw = weg.Weg(
        5, weg.Gebietsende(None, gebiet, "mitose-mitte", "jtg:mitose"))
    nordk = weg.kreuzung("nordk", n=weg.Richtung(nordw))
    nordk.add_beschreibung(
        ("Der kleine Pfad stößt spitz auf einen Weg von links.",),
        nur="s")
    nordk.add_beschreibung(
        ("Ein kleiner Pfad biegt nach links ab.",
         "Der Weg macht derweil eine leichte Biegung nach Südwesten."),
        nur="n")
    nordk.add_beschreibung(
        ("Ein kleiner Pfad führt von der rechten Seite des Weges nach Süden.",
         "Der Weg macht eine leichte Biegung nach Norden."), nur="sw")
    nordk.verbinde_mit_weg(west, 3, "sw", "n")

    süd = weg.WegAdapter(t2_süd)
    osten = weg.kreuzung("osten", immer_fragen=True)
    osten.add_beschreibung(("Das Gestrüpp wird immer dichter.",
                            "Hohe Brombeerhecken verstellen dir den Weg."))
    osten.add_effekt(beeren.main)
    osten.add_beschreibung("Du kommst hier nicht weiter. Umkehren?")

    lichtung = weg.kreuzung(
        "lichtung",
        s=weg.Richtung(süd, typ=weg.Wegtyp.PFAD),
        gucken=lichtung_gucken)
    lichtung.verbinde_mit_weg(nordk, 3, "n", typ=weg.Wegtyp.PFAD)
    lichtung.verbinde_mit_weg(west, 4, "w", typ=weg.Wegtyp.TRAMPELPFAD)
    lichtung.add_beschreibung(
        "Du befindest sich auf einer Lichtung in einem Wald.", nur=[None])
    lichtung.add_beschreibung(
        "Du kommst auf eine Lichtung.", außer=[None, "o"])
    lichtung.add_beschreibung((
        "Die Lichtung ist ungewöhnlich rund, mit einem Radius von 5 Metern.",
        "Daran schließt sich ein Mischwald an, weder besonders dicht noch licht."
    ))
    lichtung.add_beschreibung((
        "Ein schmaler Pfad führt nach Norden.",
        "Im Osten ist Dickicht.",
        "Im Westen und Süden ist nichts besonderes."
    ))

    osten.verbinde(lichtung, "w", typ=weg.Wegtyp.TRAMPELPFAD)
    lichtung.verbinde(osten, "o", typ=weg.Wegtyp.TRAMPELPFAD)
    return lichtung


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


def t2_süd(mänx: Mänx) -> None:
    malp("Der Wald wird immer dunkler.")
    mint("Ein kalter Wind weht. Das Vogelgezwitscher der Lichtung kommt dir nun "
         "wie ein kurzer Traum vor.")
    mint("Es wird immer dunkler.")
    if mänx.welt.ist("kennt:hexer"):
        malp("Diesmal siehst du das Licht nicht.")
        ende_des_waldes(mänx)
        return

    malp("Plötzlich siehst du ein Licht in der Ferne.")
    haus = ja_nein(mänx, "Gehst du zum Licht?")
    if haus:
        malp("Es ist eine einsame, einstöckige Hütte, aus der das Licht kam. "
             "Vor dir ist die Rückseite des Hauses, "
             "an der sich Feuerholz stapelt.")
        haus = ja_nein(mänx, "Klopfst du an die Tür?")
    if haus:
        malp("Ein junger Mann begrüßt dich an der Tür.")
        if mänx.rasse == "Skelett":
            hexer_skelett(mänx)
        else:
            aktion = mänx.minput(
                '?: "Ein Wanderer? Komm herein, du siehst ganz durchgefroren aus."[k/r/f]',
                list("krf"))
            if aktion == "f":
                malp("Du rennst weg, als hätte der bloße Anblick "
                     "des jungen Manns dich verschreckt.")
                malp('Jetzt denkt der Arme sich bestimmt: "Bin ich so hässlich '
                     'oder schrecklich, dass Leute auf den '
                     'ersten Blick abhauen?"')
                malp("Aber dir ist das egal, die unbekannte Gefahr ist abgewehrt.")
                ende_des_waldes(mänx)
            elif aktion == "k":
                malp('?: "Ein/e Inquisitor/in? Dafür musst du früher aufstehen!"')
                hexer_kampf(mänx)
            else:  # "r"
                haus_des_hexers(mänx)
    else:
        malp("Dem, der auch immer hinter dem Licht steckt, sollte man nicht "
             "trauen, befindest du und machst "
             "dich weiter "
             "auf den Weg durch den Wald.")
        ende_des_waldes(mänx)


def hexer_skelett(mänx: Mänx):
    mänx.welt.setze("kennt:hexer")
    sprich("?", "Ach hallo, ein Skelett! Fühl dich hier wie zu Hause.")
    leo = "Leo Berndoc"
    sprich(leo, "Ich habe ganz vergessen, mich vorzustellen!")
    sprich(leo, "Ich bin Leo Berndoc.", warte=True)
    sprich(leo, "Willst du hier übernachten?")
    sprich(leo, "Oder brauchst du das gar nicht, so als Skelett?")
    if mänx.ja_nein("Nimmst du sein Angebot an?"):
        mänx.welt.nächster_tag()
        malp("Du schläfst gut, zumindest für ein Skelett.")
        malp("Am nächsten Morgen begrüßt dich Leo.")
    sprich(leo, "Meine bescheidene Hütte ist hier mitten im Wald."
           "Im Norden sind die Dörfer Mitose und Disnajenbun."
           f"Im Süden ist {SÜD_DORF_NAME}.")
    sprich(leo, "Ich kann dich bringen.")
    sprich(leo, "Aber nicht begleiten.")
    mgn = [(a, a.lower(), a.lower())
           for a in ("Mitose", "Disnajenbun", SÜD_DORF_NAME)]
    ans = mänx.menu(mgn, "Wohin lässt du dich bringen?")
    if ans == "mitose":
        weg.wegsystem(mänx, "jtg:mitose")
    elif ans == "disnajenbun":
        disnayenbum(mänx)
    else:
        süd_dorf(mänx)


def haus_des_hexers(mänx: Mänx) -> None:
    malp("Er bittet dich an den Tisch und gibt dir einen warmen Punsch.")
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
        malp("Er sagt mit einem verschwörerischen Tonfall: \"Ich verstehe.\"")
        sprich(leo, "Bleibe ruhig noch die Nacht. Hier werden sie dich nicht finden.")
        malp("Du entschließt dich, mitzumachen. Am nächsten Tag verlässt du "
             "schnell das Haus, bevor der Schwindel "
             "auffliegt")
        ende_des_waldes(mänx, True)
    elif antwort == "verirrt" or antwort == "an":
        sprich(leo, "Soso.")
        sleep(1)
        sprich(leo, "...")
        sleep(1)
        sprich(leo, "Ich habe ein Gästebett. Da kannst du schlafen.")
        malp("Dein erstes Bett in dieser Welt ist schön weich.")
        sleep(3)
        malp("Als du am nächsten Morgen aufwachst, fühlst du dich schwach und kalt.")
        malp("Leo steht vor dir.")
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
                malp("Dein erstes Bett in dieser Welt ist schön weich.")
                sleep(5)
                ende_des_waldes(mänx, True)
    else:  # oase
        sprich(leo, "Interessant.")
        malp("Er wirkt sichtlich überfordert.")
        sprich(leo, "Das muss eine Tür der Qual sein..., oder war es Wal der Qual...")
        sleep(0.3)
        sprich(leo, "Aber was hat ein Wal hier zu suchen?")
        malp("Du hast ihn sichtlich verwirrt.")
        mint("Er zeigt noch auf ein Gästezimmer, dann geht er vor "
             "sich hin brabbelnd in sein Zimmer")
        mint("Im Bett denkst du über deinen heutigen Tag nach. Du sinkst "
             "in einen unruhigen Schlaf.")
        sleep(5)
        malp("Früh am Morgen verlässt du eilig das Haus.")
        mint("Aber du siehst noch einen Ring auf dem Tisch.")
        if ja_nein(mänx, "Steckst du ihn ein?"):
            mänx.erhalte("Ring des Berndoc")
        sprich(leo, "Ich hab's! Es ist ein Wahlqualportal!!!")
        ende_des_waldes(mänx, True)


def hexer_kampf(mänx):
    malp("Der Mann spricht einen schnellen Zauberspruch. Dir wird unglaublich kalt.")
    if mänx.get_kampfkraft() > 2000:
        malp("Aber du bist stärker.")
        malp("Du besiegst den Mann und plünderst sein Haus.")
        mänx.erhalte("Gold", 120)
        mänx.erhalte("Mantel", 3)
        mänx.erhalte("Unterhose", 7)
        mänx.erhalte("Banane", 1)
        mänx.erhalte("Menschenskelett", 3)
        malp("Du findest einen Ring. In ihm steht eingraviert: "
             "\"Ich hasse dich, Dongmin!\"")
        mänx.erhalte("Ring des Berndoc")
        malp("Du entscheidest dich, nach Süden weiter zu gehen.")
        sleep(2)
    else:
        malp("Du kannst dich kaum bewegen. Er tritt auf dich drauf.")
        sleep(0.5)
        malp("Dein Rücken tut weh")
        sleep(0.5)
        malp("Aber er zeigt Gnade. ", end="")
        hose = mänx.inventar["Unterhose"]
        if hose:
            malp("Er zieht dich bis auf die Unterhose aus", end="")

        else:
            malp("Er zieht dich aus, verzieht das Gesicht, als er sieht, "
                 "dass du keine Unterhose trägst", end="")
        malp(" und wirft dich im Süden des Waldes auf den Boden")
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


tobi = StoryChar("jtg:m:tobiac", ("Tobiac", "Berndoc", "Orgelspieler"), Person("m"), {},
                 vorstellen_fn=["Tobiac spielt auf der Orgel.",
                                "Die Melodie klingt ungewöhnlich, aber sehr schön."])


@tobi.dialog_deco("vor_reden", "--", zeitpunkt=Zeitpunkt.Ansprechen)
def tobi_vorstellen(self: NSC, _mänx: Mänx) -> None:
    malp("Tobiac spielt erst noch den Satz zu Ende.")
    sleep(2)
    malp("Er spricht mit leiser Stimme.")
    sprich(self.name, f"Hallo, ich bin {self.name}.")
    sprich("Du", "Ich bin $&%!")


tobi.dialog("leo", '"Was ist dein Verhältnis zu Leo Berndoc?"',
            ("Er ist mein Bruder, aber er hat sich in den "
             "Wald zurückgezogen. Ich habe lange nicht mehr von ihm gehört.",
             "Er war auch vorher sehr zurückgezogen.",
             "Warum fragst du?")).wenn_var("kennt:hexer")
tobi.dialog("wetter",
            '"Wie findest du das Wetter heute?"',
            ["(zögert kurz)", "Schön sonnig, nicht?",
             Malp("Draußen war es bewölkt."),
             Malp("Wie lange war Tobiac wohl nicht mehr draußen?")])
tobi.dialog('wo', '"Wo bin ich?"',
            f"Du bist in {SÜD_DORF_NAME}, im Reich Jotungard.")


@tobi.kampf
def tobi_kampf(self, mänx: Mänx) -> None:
    if mänx.hat_klasse("Waffe", "magische Waffe"):
        malp("Er ist so sehr in sein Orgelspiel vertieft, dass er seinen "
             "Tod nicht kommen sieht.")
        mint("Er fällt auf die Klaviatur, und "
             "sein letztes Lied endet jäh in einer langen Dissonanz.")
        mint("Er hatte nichts von Wert an sich.")
        self.tot = True
    else:
        malp("Du prügelst auf ihn ein, aber er wehrt sich nicht.")
        if ja_nein(mänx, "Machst du weiter?"):
            mint("Du schlägst ihn bewusstlos")


@tobi.dialog_deco("hören", "Ihm beim Spielen zuhören", zeitpunkt=Zeitpunkt.Option)
def zuhören(self, _mänx: Mänx) -> None:
    mint("Tobiac spielt einfach weiter Orgel.\n"
         "Du hast das Gefühl, er hat dich bemerkt, aber er lässt sich "
         "nichts anmerken.")
    sleep(2)
    mint("Du gibt dich der Melodie hin.")


@tobi.dialog_deco("orgel", '"Warum spielst du Orgel? Es ist doch nicht Gottesdienst gerade?"')
def reden_orgel(self, mänx: Mänx) -> None:
    sprich(self.name, "Ich spiele gerne Orgel. "
           "Es beruhigt mich ungemein.")
    sprich(self.name, "Wenn nur mein Sohn auch so gerne wie ich spielen würde.")
    sprich(self.name, "Ich bin nie zu Hause und spiele lieber Orgel. "
           "Und mein Sohn spielt lieber bei den Nachbarn nebenan.")
    if ja_nein(mänx, self.name + " :Ich bin ein schlechter Vater, nicht?"):
        mänx.titel.add("Respektloser")
        sprich(self.name, "Es tut irgendwie doch weh, es so zu hören.")
    else:
        sprich(self.name, "Danke.")


@tobi.dialog_deco("lernen", '"Kannst du mir beibringen, Orgel zu spielen?"')
def tobi_lernen(self, mänx: Mänx) -> None:
    sprich(self.name, "Ja, gerne!")
    mint("Tobiac ist sofort voll in seinem Element. Dir ist, als wäre "
         "er einsam und froh über deine Gesellschaft.")
    mint("Du bleibt einige Tage bei ihm und lernst sein Handwerk.")
    mänx.welt.nächster_tag(11)
    mint("Je länger du übst, desto mehr siehst du, dass er so gut spielt "
         "wie kein anderer.")
    mänx.fähigkeiten.add("Orgel")


def ring_zeigen(self, mänx: Mänx) -> bool:
    self.sprich("Das ist doch der Ring unserer Familie!")
    self.sprich("Warte. Ich werde nicht fragen, wo du ihn her hast.")
    malp("Du gibst ihm den Ring des Berndoc")
    self.inventar["Ring des Berndoc"] += 1
    mänx.inventar["Ring des Berndoc"] -= 1
    return True


tobi.dialog('ring', "Den Ring vorzeigen", ring_zeigen).wenn(
    lambda _n, m: m.hat_item("Ring des Berndoc"))


def zufällige_frau():
    name = zufälliger_name()
    person = Person("w")
    inventar: Inventar = defaultdict(int)
    verheiratet = random.random() > 0.4
    if verheiratet:
        inventar["Schnöder Ehering"] += 1
    elif random.random() > 0.5:
        inventar["Gänseblümchen"] += 5
    inventar["Einfaches Kleid"] += 1
    inventar["Unterhose"] += 1
    inventar["BH" if random.random() < 0.6 else "Großer BH"] += 1
    if random.random() > 0.8:
        inventar["Haarband"] += 1
        inventar["Armband"] += 2
    if random.random() > 0.8:
        inventar["Dolch"] += 1
    inventar["Socke"] += 2
    inventar["Gold"] += max(0, random.randint(-4, 10))
    char = StoryChar(None, (name, "Hausfrau"), person,
                     inventar, direkt_reden=True)
    char.dialoge.extend(HalloDialoge)

    nsc = char.zu_nsc()
    if not verheiratet:
        nsc.variablen.add("ledig")
    return nsc


def gar_kampf(nsc, mänx: Mänx) -> None:
    nsc.sprich("Hilfe!")
    nsc.freundlich -= 40
    if nsc.ort:
        # hilfe = nsc.ort.melde(mänx, Ereignis.KAMPF, [nsc])
        # if hilfe:
        # else:
        # malp("Gerade ist niemand da, der helfen könnte.")
        malp("Sofort eilen Leute zur Hilfe.")
        malp("Du siehst dich umzingelt.")
        if mänx.ja_nein("Ergibst du dich?"):
            nsc.sprich("Warum hast du mich angegriffen?")
            rechtfertigen(mänx, nsc)
        else:
            malp("Du wirst schnell überwältigt, aber weil du zu "
                 "stark bist, können sie dich leider nicht lebendig "
                 "fangen.")
            raise Spielende
        return

    else:
        malp("Hier ist niemand, der helfen könnte.")
    malp("Du bringst ihn um und plünderst ihn aus.")
    nsc.plündern(mänx)
    nsc.tot = True


def rechtfertigen(mänx: Mänx, nsc):
    opts = [
        ("Weil du lecker aussahst.", "lecker", "mord"),
        ("Mir war gerade danach", "danach", "mord"),
        ("Du hast mich schief angeguckt.", "schief", "mord"),
        ("Du hast mich bestohlen!", "diebstahl", "diebstahl"),
        ("Tut mir leid, kommt nie wieder vor!", "tut", "ent"),
        ("Du hast mich bespuckt!", "bespuckt", "bespuckt"),
    ]
    random.shuffle(opts)
    ans = mänx.menu(opts)
    helfer = "Wache"
    if ans == "mord":
        sprich(helfer, "Das ist keine gute Rechtfertigung!")
        sprich(helfer, "Mord dulden wir hier nicht.")
        mänx.verbrechen[Verbrechen(Verbrechensart.MORD)] += 1
        raise Spielende  # TODO: Verbrecher
    elif ans == "diebstahl":
        val = ""
        while not val:
            sprich(helfer, "Was soll er denn gestohlen haben?")
            val = mänx.minput("", lower=False)
        if {"Kleidung", "Nahrung"} & set(get_classes(val)):
            sprich(helfer, "Kleidung oder Essen zu stehlen ist kein Verbrechen,"
                   " das man "
                   "mit Waffengewalt lösen sollte.")
            sprich(helfer, "Wir lassen dich diesmal gehen.")
        else:
            sprich(helfer, "Durchsuchen wir ihn!")
            if nsc.hat_item(val):
                sprich(helfer, "Er hat tatsächlich ein/-e {val}")
                nsc.erhalte(val, von=nsc)
            else:
                sprich(helfer, "Du lügst. Der Junge ist unschuldig.")
                sprich(helfer, "Mord dulden wir hier nicht.")
                mänx.verbrechen[Verbrechen(Verbrechensart.MORD)] += 1
                raise Spielende
    elif ans == "ent":
        sprich(helfer, "Hoffen wir das mal.")
    else:  # ans == "bespuckt":
        sprich(helfer, "Das ist kein Grund, einfach auf jemanden loszugehen!")
        try:
            if nsc.ort.dorf.name == SÜD_DORF_NAME:
                sprich(helfer, "Tu das nie wieder!")
                return
        except AttributeError:
            pass
        sprich(helfer, "Du hast unseren kleinen Gaa angegriffen, das "
               "verzeihen wir dir nicht!")
        mänx.verbrechen[Verbrechen(Verbrechensart.MORD)] += 1
        raise Spielende


StoryChar("jtg:süd:garnichts", ("Gaa", "Nix", "Junge"), Person("m"), direkt_reden=True,
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
    vorstellen_fn=["Ein sommersprössiger Junge mit braunen Haaren "]
)


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
    if "ledig" in nsc.variablen:
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
    malp("Der Wald wird schnell viel weniger unheimlich.")
    if not morgen:
        malp("Erschöpft legst du dich auf den Waldboden schlafen.")
        sleep(2)
    malp("Im Süden siehst du ein Dorf.")
    süd_dorf(mänx)


def erzeuge_süd_dorf(mänx) -> Dorf:
    do = Dorf.mit_draußen(SÜD_DORF_NAME)
    kirche = ort("Kirche", do, [
        "Du bist in einer kleinen Kirche.",
        # Tobiac tot?
        "Im Hauptschiff ist niemand, aber du hörst die Orgel."
    ])
    mänx.welt.obj("jtg:m:tobiac").ort = kirche
    mänx.welt.obj("jtg:süd:garnichts").ort = kirche
    for _i in range(randint(2, 5)):
        w = zufällige_frau()
        w.template.dialoge.extend(SÜD_DORF_DIALOGE)
        w.ort = do.orte[0]
    # TODO weitere Objekte
    return do


def süd_dorf(mänx: Mänx):
    mänx.genauer(SÜD_DORF_GENAUER)
    mänx.welt.get_or_else("jtg:dorf:süd", erzeuge_süd_dorf, mänx).main(mänx)
    ziele: list[MenuOption[MänxFkt]] = [
        ("Den Weg nach Süden zur Hauptstadt", "hauptstadt", hauptstadt_weg),
        ("Den Weg nach Norden nach Tauern", "tauern", tauern_ww_süd),
        ("Den Weg nach Westen nach Grökrakchöl", "grökrakchöl", zugang_südost),
        #("Den Pfad in den Wald", "wald", wald)
    ]
    mänx.menu(ziele, frage="Wohin gehst du?")(mänx)


def hauptstadt_weg(mänx: Mänx):
    malp("Am Wegesrand siehst du ein Schild: \"Achtung Monster!\"")
    if mänx.ja_nein("Willst du wirklich weitergehen?"):
        mon = random.randint(1, 3)
        if mon == 2 or "Kinderfreund" in mänx.titel:
            malp("Plötzlich bemerkst du einen süßen Duft und ein sanftes "
                 "Leuchten im Wald zu deiner Rechten.")
            mint("Ehe du dich versiehst, bis du vom Weg abgekommen.")
            malp("Du hörst eine sanfte Stimme:")
            sprich("Dryade", "Hier ist es nicht sicher, Wanderer.")
            sprich("Dryade", "Nicht sicher für dich.", warte=True)
            sprich("Dryade", "Schreite durch dieses Portal!")
            if mänx.ja_nein("Ein Portal öffnet sich vor dir. Möchtest "
                            "du hindurch?"):
                malp("Du landest an einem vertrauten Ort.")
                mint("Es ist der Ort, wo deine Geschichte begonnen hat.")
                from xwatc.lg import mitte
                wegsystem(mänx, mitte.MITTE)
            else:
                sprich("Dryade", "Vertraust du mir nicht?")
                mint("Die Stimme verstummt, das Portal schließt sich und "
                     "der Duft verschwindet.")
                malp("Plötzlich bist du im dunklen Wald allein.")
                mint("Etwas schweres trifft dich an der Seite und wirft dich "
                     "zu Boden.")
                malp("Dass es ein Stein ist, siehst du im Fallen.")
                mint("Du kannst dich nicht mehr bewegen und du siehst im "
                     "Augenwinkel einen Bär auf dich zukommen.")
                raise Spielende
        elif mon == 1:
            mint("Ein Pack Wölfe greift dich an.")
            malp("Sie haben die umzingelt, bevor du sie bemerkt hast.")
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
            malp("Später wird dein Kopf als Schmuck gefunden.")
            raise Spielende
    else:
        süd_dorf(mänx)


def t2_no(mänx):
    malp("Du kommst an einen Wegweiser.")
    malp("Der Weg gabelt sich an einem kleinen Fluss, links führt der Weg "
         "den Fluss aufwärts zum 'Land der aufrechten Kühe' und rechts "
         "führt der Weg nach flussabwärts nach '" + SÜD_DORF_NAME + "'")
    if mänx.minput("Gehst du nach links oder rechts", ["links", "rechts"]) == "links":
        land_der_kühe(mänx)
    else:
        süd_dorf(mänx)


def tauern_ww_süd(mänx: Mänx):
    malp("Du folgst dem Weg sehr lange den Fluss aufwärts.")
    malp("Da kommst du an eine Kreuzung. Ein Weg führt den Fluss weiter aufwärts.")
    malp("Der Weg biegt nach links ab.")
    malp("Du siehst einen Wegweiser: Rechts ins 'Land der aufrechten Kühe', links "
         f"nach Disnayenbum. Du kommst von '{SÜD_DORF_NAME}'.")
    opts = [("Nach rechts (Land der aufrechten Kühe)", "rechts", True),
            ("Nach links (Disnayenbum)", "links", False)]
    if mänx.menu(opts):
        land_der_kühe(mänx)
    else:
        disnayenbum(mänx)


def tauern_ww_no(mänx: Mänx):
    malp("Du kommst an eine Wegkreuzung.")
    malp(f"Links biegt ein Weg, den Fluss entlang, nach '{SÜD_DORF_NAME}' ab.")
    malp("Dein Weg verlässt den Fluss in Richtung Disnayenbum.")
    opts = [("Nach rechts (Disnayenbum)", "rechts", 1),
            (f"Nach links ({SÜD_DORF_NAME})", "links", 2),
            ("Zurück", "zurück", 0)]
    a = mänx.menu(opts)
    if a == 1:
        disnayenbum(mänx)
    elif a == 2:
        süd_dorf(mänx)
    else:
        land_der_kühe(mänx)


if __name__ == '__main__':
    m = Mänx()
    m.inventar["Speer"] += 1
    t2(m)
