from time import sleep
from xwatc import haendler
from xwatc import scenario
from xwatc.system import Mänx, minput, ja_nein, Spielende, mint, sprich
from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner
from random import randint
import random
from xwatc.jtg.ressourcen import FRAUENNAMEN


def t2(mänx: Mänx) -> None:
    """Jaspers Teilgeschichte"""
    print("Hinter der Tür ist es warm und sonnig.")
    sleep(1)
    print("Es erwartet dich Vogelgezwitscher.")
    sleep(1)
    print("Du befindest sich auf einer Lichtung in einem Wald.")
    print("Ein schmaler Pfad führt nach Norden.")
    print("Im Osten ist Dickicht.")
    print("Im Westen und Süden ist nichts besonderes.")
    beeren = False
    cont = True
    while cont:
        cont = False
        richtung = minput(mänx, "Gehst du nach Norden, Osten, Westen oder Süden? norden/süden/westen/"
                          "osten", ["osten", "süden", "westen", "norden"])
        if richtung == "norden":
            print("Der kleine Pfad stößt spitz auf einen Weg von links.")
            weiter = minput(
                mänx, "Willst du dem Weg folgen [f] oder scharf links abbiegen?[abb]", ["f", "abb"])
            if weiter == "f":
                t2_norden(mänx)
            else:
                t2_west(mänx)
        elif richtung == "osten":
            if not beeren:
                print("Du findest Beeren.")
                mänx.inventar["Beere"] += 10
                print("Aber du kommst hier nicht weiter")
            minput(mänx, "Umkehren?")
            cont = True
            beeren = True
        elif richtung == "süden":
            t2_süd(mänx)
        else:  # Westen
            print("Du triffst auf einen Weg.")
            if mänx.minput("Rechts oder Links?", ["r", "l"]) == "r":
                t2_norden(mänx)
            else:
                t2_west(mänx)


class Mädchen(haendler.Händler):
    def __init__(self):
        super().__init__("Mädchen", kauft=["Kleidung"], verkauft={
            "Rose": [1, 1]}, gold=0, art="Mädchen")

    def vorstellen(self, mänx):
        print("Am Wegesrand siehst du ein Mädchen in Lumpen. "
              "Sie scheint zu frieren.")

    def get_preis(self, _):
        return 0

    def kampf(self, mänx: Mänx) -> None:
        print("Das Mädchen ist schwach. Niemand hindert dich daran, sie "
              "auf offener Straße zu schlagen.")
        print("Sie hat nichts außer ihren Lumpen.", end="")
        if self.verkauft["Rose"]:
            print(
                ", die Blume, die sie dir verkaufen wollte, ist beim Kampf zertreten worden.")
        else:
            print(".")
        del self.verkauft["Rose"]
        self.plündern(mänx)


def t2_norden(mänx) -> None:
    """Das Dorf auf dem Weg nach Norden"""
    print("Auf dem Weg kommen dir mehrfach Leute entgegen, und du kommst in ein kleines Dorf")
    mädchen = mänx.welt.get_or_else("jtg:mädchen", Mädchen)
    if "k" == mädchen.main(mänx):
        mädchen.kampf(mänx)
    elif "Mantel" in mädchen.verkauft:
        print("Das Mädchen bedeutet dir, dass sie nur den halben Mantel braucht.")
        print("Du schneidest den Mantel entzwei, und gibst ihr nur die Hälfte.")
        mänx.inventar["halber Mantel"] += 1
        mänx.titel.add("Samariter")
    elif mädchen.verkauft["Rose"][0] == 0:
        print("Das Mädchen ist dankbar für das Stück Gold")
    if "Unterhose" in mädchen.verkauft:
        print(
            "Das Mädchen ist sichtlich verwirrt, dass du ihr eine Unterhose gegeben hast.")
        print("Es hält sie vor sich und mustert sie. Dann sagt sie artig danke.")
        mänx.titel.add("Perversling")
    mint("Du kommst im Dorf Disnayenbun an.")
    if "osten" == scenario.lade_scenario(mänx, "disnajenbun"):
        t2_no(mänx)
    else:
        t2_nw(mänx)


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


def haus_des_hexers(mänx)-> None:
    print("Er bittet dich an den Tisch und gibt dir einen warmen Punsch.")
    mänx.welt.setze("kennt:hexer")
    leo = 'Leo Berndoc'
    sprich(leo, "Ich bin Leo Berndoc.")
    sprich(leo, "Was suchst du in diesem Wald?")
    antwort = mänx.minput("",
        "Halloli! Was mach ich wohl in deinem Haus?[halloli]/ "
        "Ich habe mich hier verirrt.[verirrt]/ "
        "Ich bin nur auf der Durchreise.[durchreise]/ "
        "Die große Liebe![liebe]/ "
        "Ich bin einfach in den Osten ­– weil da keine Menschen sind – gegangen, "
        "und dann war da diese Oase. Da waren zwei Türen. "
        "Ich habe mir ein Herz gefasst, bin durch die Tür gegangen und hier "
        "bin ich. Plötzlich.[oase]/ "
        "Das gehst dich doch nichts an![an]",
        ["verirrt", "halloli", "durchreise", "liebe", "oase", "an"])
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
        sprich(leo, "Schade. Trotzdem-Schön, dich getroffen zu haben. Im Süden ist ein Dorf, "
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
        self.sprich("Warte. Ich werde nicht fragen, wo du ihn herhast.")
        print("Du gibst ihm den Ring des Berndoc")
        self.inventar["Ring des Berndoc"] += 1
        mänx.inventar["Ring des Berndoc"] -= 1
        return True

    def reden_wo_bin_ich(self, mänx: Mänx) -> bool: # pylint: disable=unused-argument
        self.sprich(f"Du bist in {SÜD_DORF_NAME}, im Reich Jotungard.")
        return True

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        return NSC.optionen(self, mänx) + [
            ("Ihm beim Spielen zuhören", "hören", self.zuhören)
        ]

    def main(self, mänx: Mänx) -> None:
        print("Tobiac spielt auf der Orgel.")
        print("Die Melodie klingt ungewöhnlich, aber sehr schön.")
        super().main(mänx)



class Waschweib(Dorfbewohner):
    def __init__(self, name: str):
        super().__init__(name, geschlecht=False)
        self.art = "Waschweib"
        self.inventar["Schnöder Ehering"] += 1
        self.inventar["Einfaches Kleid"] += 1
        self.inventar["Unterhose"] += 1

def zufälliges_waschweib() -> Waschweib:
    name = "{} {}tochter".format(
        random.choice(FRAUENNAMEN), random.choice(FRAUENNAMEN))
    w = Waschweib(name)
    if random.random() > 0.8:
        w.inventar["Haarband"] += 1
    w.gold += max(0, random.randint(-4, 10))
    return w

def ende_des_waldes(mänx, morgen=False):
    print("Der Wald wird schnell viel weniger unheimlich")
    if not morgen:
        print("Erschöpft legst du dich auf den Waldboden schlafen.")
        sleep(2)
    süd_dorf(mänx)

def erzeuge_süd_dorf(mänx) -> Dorf:
    d = Dorf(SÜD_DORF_NAME)
    kirche = Ort("Kirche", [
        "Du bist in einer kleinen Kirche.",
        # Tobiac tot?
        "Im Hauptschiff ist niemand, aber du hörst die Orgel"
    ])
    kirche.menschen.append(mänx.welt.get_or_else("jtg:m:tobiac", TobiacBerndoc))
    d.orte.append(kirche)
    for _i in range(randint(2,5)):
        d.orte[0].menschen.append(zufälliges_waschweib())
    # TODO weitere Objekte
    return d

def süd_dorf(mänx):
    print("Im Süden siehst du ein Dorf")
    mänx.genauer(SÜD_DORF_GENAUER)
    mänx.welt.get_or_else("jtg:dorf:süd", erzeuge_süd_dorf, mänx).main(mänx)


def t2_west(mänx):
    pass


def t2_no(mänx):
    print("Du kommst an einen Wegweiser.")
    print("Der Weg gabelt sich an einem kleinen Fluss, links führt der Weg "
          "den Fluss aufwärts zum 'Land der aufrechten Kühe' und rechts "
          "führt der Weg nach flussabwärts nach '" + SÜD_DORF_NAME + "'")
    if mänx.minput("Gehst du nach links oder rechts", ["links", "rechts"]) == "links":
        land_der_kühe(mänx)
    else:
        süd_dorf(mänx)


def t2_nw(mänx):
    pass


def land_der_kühe(mänx):
    pass


if __name__ == '__main__':
    m = Mänx()
    m.inventar["Speer"] += 1
    t2(m)
