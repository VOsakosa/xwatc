"""
NSCs für Disnajenbun
Created on 18.10.2020
"""
from __future__ import annotations

from collections.abc import Sequence
import random
import re
from xwatc import jtg, weg
from xwatc import nsc
from xwatc.dorf import NSC, Rückkehr, Malp, Dialog
from xwatc.nsc import StoryChar, bezeichnung
from xwatc.scenario import Scenario, ScenarioWegpunkt
from xwatc.system import Mänx, mint, Spielende, InventarBasis, sprich, malp, register
from xwatc.weg import Eintritt

from typing import Optional, Iterable
from xwatc.jtg import osten, mitose
from xwatc.jtg import eo_nw
__author__ = "jasper"

eintritt_süd = Eintritt(("jtg:disnayenbum", "süd"))
eintritt_ost = Eintritt(("jtg:disnayenbum", "ost"))
eintritt_west = Eintritt(("jtg:disnayenbum", "west"))


@weg.gebiet("jtg:disnayenbum")
def disnayenbum(_mänx: Mänx, gb: weg.Gebiet):
    ScenarioWegpunkt("disnajenbun", "disnajenbun", {
        "osten": gb.ende(eintritt_ost, osten.no_dis),
        "westen": gb.ende(eintritt_west, eo_nw.eo_nw_ost),
        "süden": gb.ende(eintritt_süd, mitose.eingang_nord)
    })


def frage_melken(nsc: NSC, _mänx: Mänx):
    if nsc.freundlich >= 0:
        nsc.sprich("Aber nur weil du es bist.")
        malp(f"{nsc.name} wirkt leicht beschämt.")
    else:
        nsc.sprich("Nein! Natürlich nicht!")
        malp("Sie ist echt wütend!")


def kampf_in_disnayenbum(nsc: nsc.NSC, mänx: Mänx):
    axtmann_da = False
    if isinstance(mänx.context, Scenario):
        axtmann_da = mänx.welt.am_leben("jtg:axtmann")
    if axtmann_da:
        malp("Du spürst den Blick des Axtmannes im Rücken.")
        if not mänx.ja_nein("Willst du wirklich jemand wehrloses angreifen?"):
            return
    mint(f"Du greifst {nsc.name} an.")
    if axtmann_da:
        malp("Aber das ist dem Mann mit der Axt nicht entgangen.")
        malp("Er macht kurzen Prozess aus dir.")
        raise Spielende()
    mint("Ein leichter Kampf.")
    # TODO Tod berichten
    nsc.tot = True
    nsc.plündern(mänx)


@register("jtg:nomuh")
class NoMuh(NSC):
    def __init__(self):
        super().__init__("No Muh", "Kuh", freundlich=-10,
                         kampfdialog=kampf_in_disnayenbum, dlg=self.dlg)
        self.inventar["Glocke"] += 1
        self.verstanden = False
        self.letztes_melken: Optional[int] = None

    @staticmethod
    def dlg():
        return [
            Dialog("hallo", '"Hallo"', ("Hallo.",)),
            Dialog("futter", '"Was hättest du gerne zu essen?"',
                   ("Erbsen natürlich.", )),
            Dialog("melken", '"Darf ich dich melken?"', frage_melken),  # type: ignore
        ]

    def vorstellen(self, mänx: Mänx):
        malp("Eine große Kuh frisst Gras.")
        self.sprich("Pfui, so jemand starrt mich an.")
        self.sprich("No nie so eine Schönheit gesehen, was?")

    def fliehen(self, mänx: Mänx):
        if self.freundlich < 0:
            if random.random() < 0.3:
                malp("Beim Fliehen streift dich eines von NoMuhs Hörnern.")
                mint("Es tut verdammt weh.")
            else:
                mint("Du entkommst der wütenden NoMuh")

    def main(self, mänx: Mänx):
        self.verstanden = (mänx.hat_item("Mugel des Verstehens") or
                           mänx.hat_item("Talisman des Verstehens"))
        return super().main(mänx)

    def sprich(self, text: str | Sequence[str | Malp], *args, **kwargs) -> None:
        if self.verstanden:
            NSC.sprich(self, text, *args, **kwargs)  # type: ignore
        else:
            if isinstance(text, str):
                text = re.sub(r"\w+", "Muh", text)
            else:
                text = [re.sub(r"\w+", "Muh", str(t)) for t in text]
            NSC.sprich(self, text, *args, **kwargs)

    def optionen(self, mänx: Mänx):
        yield from super().optionen(mänx)
        yield ("versuchen, NoMuh zu melken", "melken", self.melken)
        yield ("NoMuh füttern", "füttern", self.füttern)

    def füttern(self, mänx: Mänx):
        opts = [("Gras ausreißen", "gras", "gras")]
        for item in ("Gänseblümchen", "Erbse", "Mantel", "Karotte", "Banane"):
            if mänx.hat_item(item):
                opts.append((item, item.lower(), item.lower()))
        ans = mänx.menu(opts, frage="Was fütterst du sie?")
        if ans == "gras":
            malp("NoMuh frisst das Gras aus deiner Hand")
            mint("und kaut gelangweilt darauf herum.")
        elif ans == "erbse":
            malp("NoMuh leckt dir die Erbsen schnell aus der Hand.")
            mänx.inventar["Erbse"] -= 1
            self.sprich("Endlich jemand, der mich versteht. Danke!")
            self.freundlich += 10
        elif ans == "mantel":
            malp("NoMuh beißt in deinen Mantel, dann reißt sie ihn an.")
            mint("Der Mantel ist jetzt unbenutzbar.")
            mänx.inventar["Mantel"] -= 1
        elif ans == "karotte":
            self.sprich("Bin ich ein Kaninchen oder was?")
            mint("NoMuh will keine Karotten.")
        elif ans == "banane":
            mint("NoMuh würdigt dich keinen Blickes.")
        else:
            assert ans == "gänseblümchen"
            mänx.inventar["Gänseblümchen"] -= 1
            self.sprich("Frauen überzeugt man mit Blumen, was?")
            self.freundlich += 1

    def melken(self, mänx: Mänx):
        if self.freundlich >= 0:
            mänx.titel.add("Kuhflüsterer")
            if self.letztes_melken is None or self.letztes_melken < mänx.welt.get_tag():
                self.letztes_melken = mänx.welt.get_tag()
                mänx.erhalte("magische Milch", 1)
            else:
                mint("No Muh wurde heute schon gemolken.")
        else:
            self.sprich("Untersteh dich, mich da anzufassen!")
            mint("NoMuh tritt dich ins Gesicht.")


def kampf_axtmann(nsc: nsc.NSC, mänx: Mänx):
    malp("Ganz miese Idee, dich mit ihm anzulegen.")
    if mänx.ja_nein("Willst du es wirklich tun?"):
        if mänx.hat_klasse("legendäre Waffe") and random.random() > 0.97:
            malp("Das Glück ist auf deiner Seite und in einem anstrengenden "
                 "Kampf bringst du ihn um.")
        elif not mänx.hat_klasse("Waffe"):
            mint("Du hast Glück")
            malp("Nein, du hast nicht gewonnen. Aber du hast es geschafft, so"
                 " erbärmlich dich anzustellen, dass er es als Scherz sieht.")
            nsc.freundlich -= 10
        else:
            malp("Ist ja nicht so, dass du nicht gewarnt worden wärst.")
            mint("Als Neuling einen Veteran anzugreifen...")
            raise Spielende
    else:
        malp("Der Axtmann starrt dich mit hochgezogenen Augenbrauen an.")
        mint("Seine mächtigen Muskel waren nur für einen kurzen Augenblick "
             "angespannt.")


@register("jtg:axtmann")
def axtmann() -> NSC:
    return NSC("?", "Axtmann", kampf_axtmann, startinventar={
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
    }, vorstellen=["Ein großer Mann hat eine Kapuze tief ins Gesicht gezogen.",
                   "Auffällig ist eine große Axt, die er in der Hand hält."],
        dlg=brian_dlg)


def brian_dlg() -> Iterable[Dialog]:
    yield Dialog("hallo", '"Hallo"', [".."])
    yield Dialog("axt", '"Du hast aber ein große Axt."',
                 [Malp("Der Mann wirkt ein wenig stolz.")])
    yield Dialog("heißt", '"Wie heißt du?"', [".."], "hallo")

    def dlg_brian(nsc, _m):
        nsc.bezeichnung = bezeichnung(("Brían", "Axtmann"))
        malp("Brían nickt leicht.")
        nsc.sprich("..", warte=True)
    yield Dialog("brian", '"Du heißt Brían, oder?"', dlg_brian
                 ).wenn_var("kennt:jtg:axtmann")


@register("jtg:fred")
def fred() -> NSC:
    return NSC("Fréd Fórmayr", "Dorfvorsteher", kampf_in_disnayenbum,
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
               }, vorstellen=["Ein Mann in Anzug lächelt dich unverbindlich an."],
               dlg=fred_dlg)


def fred_dlg():
    yield Dialog("hallo", '"Hallo"', [
        "Willkommen in Disnajenbun! Ich bin der Dorfvorsteher Fred.",
        "Ruhe dich ruhig in unserem bescheidenen Dorf aus."])
    yield Dialog("woruhen", '"Wo kann ich mich hier ausruhen?"',
                 ["Frag Lina, gleich im ersten Haus direkt hinter mir."], "hallo")
    yield Dialog("wege", '"Wo führen die Wege hier hin?"', [
        "Also...",
        "Der Weg nach Osten führt nach Tauern, aber du kannst auch nach " +
        jtg.SÜD_DORF_NAME + " abbiegen.",
        "Der Weg nach Süden führt, falls du das nicht schon weißt, nach " +
        "Grökrakchöl.",
        "Zuallerletzt gäbe es noch den Weg nach Westen...",
        "Da geht es nach Eo. Ich muss stark davon abraten, dahin zu gehen.",
        "Wenn Ihnen Ihr Leben lieb ist."
    ], "hallo")


@register("jtg:mieko")
def mieko() -> NSC:
    return NSC("Mìeko Rimàn", "Dorfbewohner", kampfdialog=kampf_in_disnayenbum,
               vorstellen=[
                   "Ein Handwerker bastelt gerade an seiner Werkbank."],
               dlg=mieko_dlg, startinventar=dict(
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


def mieko_dlg():
    def gebe_nagel(n, m):
        n.sprich("Immer gern.")
        n.inventar["Nagel"] -= 1
        m.erhalte("Nagel", 1)

    yield Dialog("nagel", '"Kannst du mir einen Nagel geben?"', gebe_nagel, "hallo"
                 ).wiederhole(5)
    yield Dialog("haus", '"Du hast aber ein schönes Haus."', [
        "Danke! Ich habe es selbst gebaut.",
        "Genau genommen habe ich alle Häuser hier gebaut.",
        "Vielleicht baue ich dir später, wenn du willst, auch ein Haus!"])
    yield Dialog("tür", 'von der magischen Tür erzählen', [
        "Das ist aber interessant.",
        "Vielleicht finde ich einen Magier, und wir gründen gemeinsam ein Geschäft:",
        "Ich mache die Türen, und er macht sie magisch.",
    ], "hallo").wenn_var("jtg:t2")
    yield Dialog("flimmern", "vom der Höhle erzählen", [
        "Und du warst plötzlich hier?",
        "Das ist aber interessant.",
    ]).wenn_var("jtg:flimmern")


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

            ), direkt_reden=True,
            vorstellen=["Ein junges Mädchen spielt im Feld."], dlg=kirie_dlg)
    n.inventar["Talisman des Verstehens"] += 1
    return n


def kirie_dlg() -> Iterable[Dialog]:
    def spielen(n, m):
        # Zeit vergeht
        malp(f"Du spielst eine Weile mit {n.name}")
        m.sleep(10)
        if n.freundlich < 60:
            n.freundlich += 10
        if n.freundlich > 60:
            m.titel.add("Kinderfreund")

    def talisman(n, m):
        n.sprich("Das?")
        malp("Kirie zeigt auf den Talisman um ihren Hals.")
        n.sprich("Das ist mein Schatz. Ich habe in gefunden. Damit kann ich mit "
                 "NoMuh reden.")
        n.sprich("Willst du auch mal?")
        if m.ja_nein("Nimmst du den Talisman?"):
            n.sprich("Gib ihn aber zurück, ja?")
            n.talisman_tag = m.welt.get_tag()
            n.sprich("Bis morgen, versprochen?")
            m.erhalte("Talisman des Verstehens", von=n)

    def talisman_zurück(n, m):
        n.sprich("Danke")
        if m.welt.get_tag() > n.talisman_tag + 1:
            n.sprich("Aber du bist zu spät.")
            n.freundlich -= 40
            n.sprich("Du bist nicht mehr mein/e Freund/in!")
        else:
            n.freundlich += 40
            n.sprich("Und? Wie war's? Konntet ihr Freunde werden?")
        m.inventar["Talisman des Verstehens"] -= 1
        n.inventar["Talisman des Verstehens"] += 1

    def axtmann_r(n, m):
        m.welt.setze("kennt:jtg:axtmann")
        n.sprich("Meinst du Brían?")
        n.sprich("Er heißt Brían und beschützt unser Dorf.", warte=True)

    yield Dialog("hallo", '"Hallo"', ("Hallo, Alter!",))
    yield Dialog("heißt", '"...und wie heißt du?',
                 ["Kirie!"], "hallo").wiederhole(1)
    yield Dialog("spielen", "spielen", spielen, "hallo")
    yield Dialog("nomuh", '"Was ist mit der Kuh?"', [
        "Sie heißt NoMuh und ist meine beste Freundin",
        "Sie ist eine echte Lady."], "heißt")
    yield Dialog("talisman", '"Was hast du da für einen Talisman?"', talisman).wenn(
        lambda n, m: n.freundlich > 10 and n.hat_item("Talisman des Verstehens"))
    yield Dialog("talismanzurück", 'Talisman zurückgeben', talisman_zurück).wenn(
        lambda n, m: m.hat_item("Talisman des Verstehens"))
    yield Dialog("axtmann", '"Wie heißt der Mann mit der Axt?"', axtmann_r).wenn(
        lambda n, m: m.welt.am_leben("jtg:axtmann"))


lina = StoryChar("jtg:lina", ("Lína", "Fórmayr", "Bäuerin"),
                 startinventar={
    "Großer BH": 1,
    "Unterhose": 1,
    "Hose": 1,
    "Top": 1,
    "Ehering": 1,
    "Gold": 14,
    "Wischmopp": 1,
    "Schürze": 1,
    "Sachbuch": 2,
}, direkt_reden=True,
    vorstellen_fn=["Eine Frau von ca. 170cm mit großen Brüsten und "
                   "braunem Haar sitzt auf einem Stuhl und liest."]
)

lina.kampf(kampf_in_disnayenbum)


def lina_hallo(n, m):
    if n.freundlich > -1:
        n.sprich("Hallo! Ich bin Lina.")
        n.sprich("Du kannst dich hier gerne für die Nacht ausruhen, "
                 "wenn du willst.", warte=True)
    else:
        n.sprich("Hallo, ich bin Lina.")
        m.sleep(1)
        n.sprich("Die Höflichkeit gebietet es mir, dich hier übernachten "
                 "zu lassen.", warte=True)


lina.dialog("hallo", '"Hallo!"', lina_hallo)


def starren(n, m: Mänx):
    if n.freundlich >= 0:
        n.freundlich -= 1
        malp("Sie wirft dir einen Blick zu und du wendest schnell den Blick ab.")
    elif "wurde_bestarrt" in n.variablen:
        n.sprich("BRíAN!")
        m.welt.setze("kennt:jtg:axtmann")
        mint("Der Mann mit der Axt stürmt herein und gibt dir eines auf die "
             "Mütze.")
        malp("Du wirst ohnmächtig")
        m.sleep(12)
        m.welt.nächster_tag()
        mint("Du wachst erst am nächsten Tag auf.")
        return Rückkehr.VERLASSEN
    else:
        m.welt.setze("kennt:jtg:axtmann")
        n.sprich("Freundchen, hör damit auf oder ich rufe Brían.")
        n.variablen.add("wurde_bestarrt")


lina.dialog("brüste", 'auf die Brüste starren', starren).wenn(
    lambda n, m: "Perversling" in m.titel)


def übernachten(n, m):
    n.sprich("Ich führe dich sofort zu deinem Bett.")
    malp("Du legst dich schlafen.")
    m.sleep(6)
    m.welt.nächster_tag()
    return Rückkehr.VERLASSEN


lina.dialog("ruhen", "ruhen", übernachten, "hallo")
lina.dialog("kiste", '"Kann ich an die Kiste?"', [
    "Ja, du kannst dir gerne Essen aus dem ersten Fach der Kiste holen."],
    "hallo")


@register("jtg:obj:kiste")
class Kiste:
    def __init__(self):
        self.fach1 = InventarBasis()
        self.fach1.inventar.update({
            "Erbse": 4,
            "Karotte": 5,
            "Bohne": 13,
            "Reisportion": 2,
            "Tomate": 2,
        })
        self.fach2 = InventarBasis()
        self.fach2.inventar.update({
            "Großer BH": 2,
            "Kleid": 1,
            "Anzugjacke": 2,
            "Anzug": 3,
            "Axt": 1,
            "Unterhose": 12,
            "Amulett": 1,
            "Kleid (Kind)": 1,
            "Gummistiefel": 2,
        })
        self.lina = None

    def main(self, mänx: Mänx):
        if isinstance(mänx.context, Scenario) and mänx.welt.am_leben("jtg:lina"):
            self.lina = mänx.welt.objekte["jtg:lina"]
        else:
            self.lina = None
        opts = [
            ("Fach 1 öffnen", "f1", self.öffne_fach1),
            ("Fach 2 öffnen", "f2", self.öffne_fach2),
            ("zerstören", "k", self.kampf),
            ("reden", "r", self.reden),
            ("zurück", "f", lambda m: Rückkehr.VERLASSEN)]
        mint("Du stehst vor einer Kiste.")
        while mänx.menu(opts)(mänx) == Rückkehr.WEITER_REDEN:
            pass

    def öffne_fach1(self, mänx: Mänx) -> Rückkehr:
        mänx.inventar_zugriff(self.fach1)
        return Rückkehr.WEITER_REDEN

    def öffne_fach2(self, mänx: Mänx) -> Rückkehr:
        if self.lina:
            self.lina.sprich("Falsches Fach!")
            if mänx.ja_nein("Lässt du das Fach offen?"):
                malp("Du siehst folgenden Inhalt:")
                malp(self.fach2.inventar_zeigen())
                self.lina.freundlich -= 1
                self.lina.sprich("Mach das Fach sofort zu.")
                if mänx.ja_nein("Willst du etwas aus dem Fach nehmen?"):
                    mänx.inventar_zugriff(self.fach2)
                    self.lina.sprich("DIEB!")
                    self.ruf_axtmann(mänx)
                    return Rückkehr.VERLASSEN
                else:
                    mint("Du machst das Fach brav zu. Lina ist trotzdem wütend.")
                    return Rückkehr.WEITER_REDEN
            else:
                mint("Du tust so, als wäre es Zufall gewesen")
                return Rückkehr.WEITER_REDEN
        else:
            malp("Scheint das falsche Fach zu sein.")
            mint("Aber ist ja keiner da.")
            mänx.inventar_zugriff(self.fach2)
            return Rückkehr.WEITER_REDEN

    def kampf(self, mänx: Mänx) -> Rückkehr:
        mint("He-ya!")
        if mänx.hat_klasse("Waffe"):
            malp("Nur ein Kratzer bleibt auf der Kiste.")
        else:
            malp("Deine Faust tut dir weh.")
        if self.lina:
            self.lina.sprich("Was tust du da?")
        return Rückkehr.WEITER_REDEN

    def reden(self, _mänx: Mänx) -> Rückkehr:
        sprich("Du", "Hallo Kiste!")
        return Rückkehr.WEITER_REDEN

    def ruf_axtmann(self, mänx):
        if mänx.welt.am_leben("jtg:axtmann"):
            malp("Der Axtmann stürmt in das Haus und spaltet deinen Schädel.")
            malp("Ziemlich intolerant gegenüber Verbrechern, diese",
                 "Disnajenbuner")
            raise Spielende
        else:
            malp("Der Axtmann ist nicht da. Scheint so, als könnte Lina "
                 "allein dich nicht groß hindern")
            if self.lina:
                self.lina.freundlich -= 10
