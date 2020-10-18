"""
NSCs für Disnajenbun
Created on 18.10.2020
"""
from xwatc.system import Mänx, mint, Spielende
from xwatc.dorf import NSC, Dorfbewohner, Rückkehr
import random
import re
from typing import Optional
from xwatc.scenario import Scenario
from xwatc import jtg
__author__ = "jasper"
REGISTER = {}


def register(name):
    def do_register(fkt):
        REGISTER[name] = fkt
        return fkt
    return do_register


def registrieren(mänx: Mänx):
    for name, fkt in REGISTER.items():
        if name not in mänx.welt:
            mänx.welt[name] = fkt()


def frage_melken(nsc: NSC, _mänx: Mänx):
    if nsc.freundlich >= 0:
        nsc.sprich("Aber nur weil du es bist.")
        print(f"{nsc.name} wirkt leicht beschämt.")
    else:
        nsc.sprich("Nein! Natürlich nicht!")
        print("Sie ist echt wütend!")


def kampf_in_disnayenbum(nsc: NSC, mänx: Mänx):
    mint(f"Du greifst {nsc.name} an.")
    if isinstance(mänx.context, Scenario):
        # mänx.context.warne_kampf(nsc, mänx)
        if "jtg:axtmann" in mänx.welt and not mänx.welt["jtg:axtmann"].tot:
            print("Aber das ist dem Mann mit der Axt nicht entgangen.")
            print("Er macht kurzen Prozess aus dir.")
            raise Spielende()
    mint("Ein leichter Kampf.")
    # TODO Tod berichten
    nsc.tot = True
    nsc.plündern(mänx)


@register("jtg:nomuh")
class NoMuh(NSC):
    def __init__(self):
        super().__init__("No Muh", "Kuh", freundlich=-10,
                         kampfdialog=kampf_in_disnayenbum)
        self.inventar["Glocke"] += 1
        self.dialog("hallo", '"Hallo"', ("Hallo.",))
        self.dialog("futter", '"Was hättest du gerne zu essen?"',
                    ("Erbsen natürlich."))
        self.dialog("melken", '"Darf ich dich melken?"', frage_melken)
        self.verstanden = False
        self.letztes_melken: Optional[int] = None

    def vorstellen(self, mänx: Mänx):
        print("Eine große Kuh frisst Gras.")
        self.sprich("Pfui, so jemand starrt mich an.")
        self.sprich("No nie so eine Schönheit gesehen, was?")

    def fliehen(self, mänx: Mänx):
        if self.freundlich < 0:
            if random.random() < 0.3:
                print("Beim Fliehen streift dich eines von NoMuhs Hörnern.")
                mint("Es tut verdammt weh.")
            else:
                mint("Du entkommst der wütenden NoMuh")

    def main(self, mänx: Mänx):
        self.verstanden = (mänx.hat_item("Mugel des Verstehens") or
                           mänx.hat_item("Talisman des Verstehens"))
        return super().main(mänx)

    def sprich(self, text: str, *args, **kwargs)->None:
        if self.verstanden:
            NSC.sprich(self, text, *args, **kwargs)
        else:
            text = re.sub(r"\w+", "Muh", text)
            NSC.sprich(self, "Muh", *args, **kwargs)

    def optionen(self, mänx: Mänx):
        yield from super().optionen(mänx)
        yield ("versuchen, NoMuh zu melken", "melken", self.melken)
        yield ("NoMuh füttern", "füttern", self.füttern)

    def füttern(self, mänx: Mänx):
        opts = [("Gras ausreißen", "gras", "gras")]
        if mänx.hat_item("Gänseblümchen"):
            opts.append(("Gänseblümchen", "gänseblümchen", "gb"))
        if mänx.hat_item("Erbse"):
            opts.append(("Erbsen", "erbsen", "eb"))
        if mänx.hat_item("Mantel"):
            opts.append(("Mantel", "mantel", "mt"))
        ans = mänx.menu(opts, frage="Was fütterst du sie?")
        if ans == "gras":
            print("NoMuh frisst das Gras aus deiner Hand")
            mint("und kaut gelangweilt darauf herum.")
        elif ans == "eb":
            print("NoMuh leckt dir die Erbsen schnell aus der Hand.")
            mänx.inventar["Erbse"] -= 1
            self.sprich("Endlich jemand, der mich versteht. Danke!")
            self.freundlich += 10
        elif ans == "mt":
            print("NoMuh beißt in deinen Mantel, dann reißt sie ihn.")
            mint("Der Mantel ist jetzt unbenutzbar.")
            mänx.inventar["Mantel"] -= 1
        else:
            assert ans == "gb"
            mänx.inventar["Gänseblümchen"] -= 1
            self.sprich("Frauen überzeugt man mit Blumen, was?")
            self.freundlich += 1

    def melken(self, mänx: Mänx):
        if self.freundlich >= 0:
            if self.letztes_melken is None or self.letztes_melken < mänx.welt.get_tag():
                self.letztes_melken = mänx.welt.get_tag()
                mänx.erhalte("magische Milch", 1)
            else:
                mint("No Muh wurde heute schon gemolken.")
        else:
            self.sprich("Untersteh dich, mich da anzufassen!")
            mint("NoMuh tritt dich ins Gesicht.")


def kampf_axtmann(nsc: NSC, mänx: Mänx):
    print("Ganz miese Idee, dich mit ihm anzulegen.")
    if mänx.ja_nein("Willst du es wirklich tun?"):
        if mänx.hat_klasse("legendäre Waffe") and random.random() > 0.97:
            print("Das Glück ist auf deiner Seite und in einem anstrengenden "
                  "Kampf bringst du ihn um.")
        elif not mänx.hat_klasse("Waffe"):
            mint("Du hast Glück")
            print("Nein, du hast nicht gewonnen. Aber du hast es geschafft, so"
                  " erbärmlich dich anzustellen, dass er es als Scherz sieht.")
            nsc.freundlich -= 10
        else:
            print("Ist ja nicht so, dass du nicht gewarnt worden wärst.")
            mint("Als Neuling einen Veteran anzugreifen...")
            raise Spielende
    else:
        print("Der Axtmann starrt dich mit hochgezogenen Augenbrauen an.")
        mint("Seine mächtigen Muskel waren nur für einen kurzen Augenblick "
             "angespannt.")


@register("jtg:axtmann")
def axtmann() -> NSC:
    n = NSC("?", "Axtmann", kampf_axtmann, startinventar={
        "mächtige Axt": 1,
        "Kettenpanzer": 1,
        "T-Shirt": 1,
        "Pausenbrot": 2,
        "Tomate": 1,
        "Ehering": 1,
        "Kapuzenmantel": 1,
        "Speisekarte": 1,
        "Lederhose": 1,
        "Gold": 3,
    })
    n.dialog("hallo", '"Hallo"', [".."])
    return n


@register("jtg:fred")
def fred() -> NSC:
    n = NSC("Fréd Fórmayr", "Dorfvorsteher", kampf_in_disnayenbum,
            startinventar={
                "Messer": 1,
                "Anzug": 1,
                "Anzugjacke": 1,
                "Lederschuh": 2,
                "Ledergürtel": 1,
                "Kräutersud gegen Achselgeruch": 2,
                "Armbanduhr": 1,
                "Unterhose": 1,
                "Ehering": 1,
                "Gold": 51
            })
    n.dialog("hallo", '"Hallo"', [
        "Willkommen in Disnajenbun! Ich bin der Dorfvorsteher Fred.",
        "Ruhe dich ruhig in unserem bescheidenen Dorf aus."])
    n.dialog("woruhen", '"Wo kann ich mich hier ausruhen?"',
             ["Frag Lina, gleich im ersten Haus direkt hinter mir."], "hallo")
    n.dialog("wege", '"Wo führen die Wege hier hin?"', [
        "Also...",
        "Der Weg nach Osten führt nach Tauern, aber du kannst auch nach " +
        jtg.SÜD_DORF_NAME + " abbiegen.",
        "Der Weg nach Süden führt, falls du das nicht schon weißt, nach " +
        "Grökrakchöl.",
        "Zuallerletzt gäbe es noch den Weg nach Westen...",
        "Da geht es nach Eo. Ich muss stark davon abraten, dahin zu gehen.",
        "Wenn Ihnen Ihr Leben lieb ist."
    ], "hallo")
    return n


@register("jtg:mieko")
def mieko() -> NSC:
    n = Dorfbewohner("Mìeko Rimàn", True, kampfdialog=kampf_in_disnayenbum)
    n.inventar.update(dict(
        Banane=1,
        Hering=4,
        Karabiner=11,
        Dübel=13,
        Schraubenzieher=2,
        Nagel=500,
        Schraube=12,
        Werkzeugkasten=1,
        Latzhose=1,
        Unterhose=1,
        Gold=14
    ))

    def gebe_nagel(n, m):
        n.sprich("Immer gern.")
        n.inventar["Nagel"] -= 1
        m.erhalte("Nagel", 1)

    n.dialog("nagel", '"Kannst du mir einen Nagel geben?"', gebe_nagel, "hallo"
             ).wiederhole(5)
    n.dialog("haus", '"Du hast aber ein schönes Haus."', [
        "Danke! Ich habe es selbst gebaut.",
        "Genau genommen habe ich alle Häuser hier gebaut.",
        "Vielleicht baue ich dir später, wenn du willst, auch ein Haus!"])
    return n


@register("jtg:kirie")
def kirie() -> NSC:
    n = NSC("Kirie Fórmayr", "Kind", kampfdialog=kampf_in_disnayenbum,
            startinventar=dict(
                Matschhose=1,
                Teddybär=1,
                Unterhose=1,
                BH=1,
                Mütze=1,
                Haarband=1,
                Nagel=4,
            ), direkt_reden=True)

    setattr(n, "vorstellen",
            lambda m: print("Ein junges Mädchen spielt im Feld."))

    def spielen(n, m):
        # Zeit vergeht
        print(f"Du spielst eine Weile mit {n.name}")
        m.sleep(10)
        if n.freundlich < 60:
            n.freundlich += 10

    def talisman(n, m):
        n.sprich("Das?")
        print("Kirie zeigt auf den Talisman um ihren Hals.")
        n.sprich("Das ist mein Schatz. Ich habe in gefunden. Damit kann ich mit "
                 "NoMuh reden.")
        n.sprich("Willst du auch mal?")
        if m.ja_nein("Nimmst du den Talisman?"):
            n.sprich("Gib ihn aber zurück, ja?")
            n.talisman_tag = m.welt.get_tag()
            n.sprich("Bis morgen, versprochen?")

    def talisman_zurück(n, m):
        n.sprich("Danke")
        if m.welt.get_tag() > n.talisman_tag + 1:
            n.sprich("Aber du bist zu spät.")
            n.freundlich -= 40
            n.sprich("Du bist nicht mehr mein/e Freund/in!")
        else:
            n.freundlich += 40
            n.sprich("Und? Wie war's? Konntet ihr Freunde werden?")

    n.dialog("hallo", '"Hallo"', ("Hallo, Alter!",))
    n.dialog("heißt", '"...und wie heißt du?',
             ["Kirie!"], "hallo").wiederhole(1)
    n.dialog("spielen", "spielen", spielen, "hallo")
    n.dialog("nomuh", '"Was ist mit der Kuh?"', [
        "Sie heißt NoMuh und ist meine beste Freundin",
        "Sie ist eine echte Lady."], "heißt")
    n.dialog("talisman", '"Was hast du da für einen Talisman?"', talisman).wenn(
        lambda n, m: n.freundlich > 10 and n.hat_item("Talisman des Verstehens"))
    n.dialog("talismanzurück", 'Talisman zurückgeben', talisman_zurück).wenn(
        lambda n, m: m.hat_item("Talisman des Verstehens"))
    return n


@register("jtg:lina")
def lina() -> NSC:
    n = NSC("Lína Fórmayr", "Bäuerin", kampfdialog=kampf_in_disnayenbum,
            startinventar=dict(
                Unterhose=1,
                Hose=1,
                Top=1,
                Ehering=1,
                Gold=14,
                Wischmopp=1,
                Schürze=1,
            ), freundlich=1, direkt_reden=True)
    n.inventar["Großer BH"] += 1
    n.wurde_bestarrt = False  # type: ignore

    def hallo(n, m):
        if n.freundlich > 0:
            n.sprich("Hallo! Ich bin Lina.")
            n.sprich("Du kannst dich hier gerne für die Nacht ausruhen, "
                     "wenn du willst.")
        else:
            n.sprich("Hallo, ich bin Lina.")
            m.sleep(1)
            n.sprich("Die Höflichkeit gebietet es mir, dich hier übernachten "
                     "zu lassen.")
    n.dialog("hallo", '"Hallo!"', hallo)

    def starren(n, m: Mänx):
        if n.freundlich > 0:
            n.freundlich -= 1
            print("Sie wirft dir einen Blick zu und du wendet schnell den Blick ab.")
        elif n.wurde_bestarrt:
            n.sprich("BRÀIN!")
            mint("Der Mann mit der Axt stürmt herein und gibt dir eines auf die "
                 "Mütze.")
            print("Du wirst ohnmächtig")
            m.sleep(12)
            m.welt.nächster_tag()
            mint("Du wachst erst am nächsten Tag auf.")
            return Rückkehr.VERLASSEN
        else:
            n.sprich("Freundchen, hör damit auf oder ich rufe Bràin.")
            n.wurde_bestarrt = True

    n.dialog("brüste", 'auf die Brüste starren', starren).wenn(
        lambda n, m: "Perversling" in m.titel)

    def übernachten(n, m):
        n.sprich("Ich führe dich sofort zu deinem Bett.")
        m.welt.nächster_tag()

    n.dialog("ruhen", "ruhen", übernachten, "hallo")

    return n
