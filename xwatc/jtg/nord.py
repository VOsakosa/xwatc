"""
NSCs für Disnajenbun
Created on 18.10.2020
"""
from __future__ import annotations

from attrs import define
from collections.abc import Iterable
import random
import re
from xwatc import _, weg
from xwatc import nsc
from xwatc.effect import Cooldown
from xwatc.jtg import eo_nw
from xwatc.jtg import osten, mitose
from xwatc.nsc import StoryChar, bezeichnung, NSC, Rückkehr, Malp, Dialog, Zeitpunkt
from xwatc.scenario import ScenarioWegpunkt
from xwatc.system import Mänx, mint, Spielende, InventarBasis, sprich, malp, register
from xwatc.weg import Eintritt
from typing_extensions import Self
from xwatc.untersystem.variablen import Variable, MethodSave





__author__ = "jasper"

eintritt_süd = Eintritt("jtg:disnayenbum", "süd")
eintritt_ost = Eintritt("jtg:disnayenbum", "ost")
eintritt_west = Eintritt("jtg:disnayenbum", "west")


@weg.gebiet("jtg:disnayenbum")
def disnayenbum(_mänx: Mänx, gb: weg.Gebiet):
    ScenarioWegpunkt(gb, "disnajenbun", "disnajenbun", {
        "osten": gb.ende(eintritt_ost, osten.no_dis),
        "westen": gb.ende(eintritt_west, eo_nw.eo_nw_ost),
        "süden": gb.ende(eintritt_süd, mitose.eingang_nord)
    })


def kampf_in_disnayenbum(nsc: nsc.NSC, mänx: Mänx):
    axtmann_da = False
    if isinstance(mänx.context, ScenarioWegpunkt):
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


nomuh = StoryChar("jtg:nomuh", ("No Muh", "Kuh"),
                  person=None, startinventar={"Glocke": 1})


def nm_sprich(nsc: NSC, txt: str) -> None:
    if "verstanden" not in nsc.variablen:
        txt = re.sub(r"\w+", "Muh", txt)
    nsc.sprich(txt)


nomuh.kampf(kampf_in_disnayenbum)


@nomuh.dialog_deco("hallo", '"Hallo"')
def hallo(nsc: NSC, _m) -> None:
    nm_sprich(nsc, "Hallo")


@nomuh.dialog_deco("futter", '"Was hättest du gerne zu essen?"', "hallo")
def futter(nsc: NSC, _m) -> None:
    nm_sprich(nsc, "Erbsen natürlich.")


@nomuh.dialog_deco("melken", '"Darf ich dich melken?"', "hallo")
def frage_melken(nsc: NSC, _mänx: Mänx) -> None:
    if nsc.freundlich >= 10:
        nm_sprich(nsc, "Aber nur weil du es bist.")
        malp(f"{nsc.name} wirkt leicht beschämt.")
    else:
        nm_sprich(nsc, "Nein! Natürlich nicht!")
        malp("Sie ist echt wütend!")


@nomuh.vorstellen
def nomuh_vorstellen(nsc: NSC, mänx: Mänx) -> None:
    malp("Eine große Kuh frisst Gras.")
    if mänx.hat_item("Mugel des Verstehens") or mänx.hat_item("Talisman des Verstehens"):
        nsc.variablen.add("verstanden")
    else:
        try:
            nsc.variablen.remove("verstanden")
        except KeyError:
            pass
    nm_sprich(nsc, "Pfui, so jemand starrt mich an.")
    nm_sprich(nsc, "No nie so eine Schönheit gesehen, was?")


@nomuh.dialog_deco("fliehen", "Fliehen", zeitpunkt=Zeitpunkt.Option)
def nomuh_fliehen(self, mänx: Mänx):
    if self.freundlich < 0:
        if random.random() < 0.3:
            malp("Beim Fliehen streift dich eines von NoMuhs Hörnern.")
            mint("Es tut verdammt weh.")
        else:
            mint("Du entkommst der wütenden NoMuh")
    return Rückkehr.VERLASSEN


@nomuh.dialog_deco("NoMuh füttern", "füttern", zeitpunkt=Zeitpunkt.Option)
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
        mänx.erhalte("Erbse", -1)
        nm_sprich(self, "Endlich jemand, der mich versteht. Danke!")
        self.freundlich += 10
    elif ans == "mantel":
        malp("NoMuh beißt in deinen Mantel, dann reißt sie ihn an.")
        mint("Der Mantel ist jetzt unbenutzbar.")
        mänx.erhalte("Mantel", -1)
    elif ans == "karotte":
        nm_sprich(self, "Bin ich ein Kaninchen oder was?")
        mint("NoMuh will keine Karotten.")
    elif ans == "banane":
        mint("NoMuh würdigt dich keinen Blickes.")
    else:
        assert ans == "gänseblümchen"
        mänx.erhalte("Gänseblümchen", -1)
        nm_sprich(self, "Frauen überzeugt man mit Blumen, was?")
        self.freundlich += 1


@nomuh.dialog_deco("versuchen, NoMuh zu melken", "melken", zeitpunkt=Zeitpunkt.Option)
def melken(self: NSC, mänx: Mänx) -> None:
    if self.freundlich >= 10:
        mänx.titel.add("Kuhflüsterer")
        if Cooldown("jtg:nord:nomuh:gemolken", 1)(mänx):
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


def dlg_brian(nsc, _m):
    nsc.bezeichnung = bezeichnung(("Brían", "Axtmann"))
    malp("Brían nickt leicht.")
    nsc.sprich("..", warte=True)


brian = StoryChar("jtg:axtmann", ("?", "Axtmann"), startinventar={
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
}, vorstellen_fn=[
    "Ein großer Mann hat eine Kapuze tief ins Gesicht gezogen.",
    "Auffällig ist eine große Axt, die er in der Hand hält."
], dialoge=[
    Dialog("hallo", '"Hallo"', [".."]),
    Dialog("axt", '"Du hast aber ein große Axt."', [
           Malp("Der Mann wirkt ein wenig stolz.")]),
    Dialog("heißt", '"Wie heißt du?"', [".."], "hallo"),
    Dialog("brian", '"Du heißt Brían, oder?"',
           dlg_brian).wenn_var("kennt:jtg:axtmann")
])
brian.kampf(kampf_axtmann)


fred = StoryChar(
    "jtg:fred", ("Fréd Fórmayr", "Dorfvorsteher"),
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
    }, vorstellen_fn=["Ein Mann in Anzug lächelt dich unverbindlich an."],
    dialoge=[
        Dialog("hallo", '"Hallo"', [
            "Willkommen in Disnajenbun! Ich bin der Dorfvorsteher Fred.",
            "Ruhe dich ruhig in unserem bescheidenen Dorf aus."]),
        Dialog("woruhen", '"Wo kann ich mich hier ausruhen?"',
               ["Frag Lina, gleich im ersten Haus direkt hinter mir."], "hallo"),
        Dialog("wege", '"Wo führen die Wege hier hin?"', [
            _("Also..."),
            _("Der Weg nach Osten führt nach Tauern, aber du kannst auch nach " +
              "Scherenfeld abbiegen."),
            _("Der Weg nach Süden führt, falls du das nicht schon weißt, nach "
              "Grökrakchöl."),
            _("Zuallerletzt gäbe es noch den Weg nach Westen..."),
            _("Da geht es nach Eo. Ich muss stark davon abraten, dahin zu gehen. "
              "Wenn Ihnen Ihr Leben lieb ist.")
        ], "hallo")])
fred.kampf(kampf_in_disnayenbum)


def gebe_nagel(n, m):
    n.sprich("Immer gern.")
    n.inventar["Nagel"] -= 1
    m.erhalte("Nagel", 1)


mieko = StoryChar(
    "jtg:mieko", ("Mìeko", "Rimàn", "Dorfbewohner"),
    vorstellen_fn=[
        "Ein Handwerker bastelt gerade an seiner Werkbank."],
    startinventar=dict(
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
    ), dialoge=[
        Dialog("nagel", '"Kannst du mir einen Nagel geben?"', gebe_nagel, "hallo"
               ).wiederhole(5),
        Dialog("haus", '"Du hast aber ein schönes Haus."', [
            "Danke! Ich habe es selbst gebaut.",
            "Genau genommen habe ich alle Häuser hier gebaut.",
            "Vielleicht baue ich dir später, wenn du willst, auch ein Haus!"]),
        Dialog("tür", 'von der magischen Tür erzählen', [
            "Das ist aber interessant.",
            "Vielleicht finde ich einen Magier, und wir gründen gemeinsam ein Geschäft:",
            "Ich mache die Türen, und er macht sie magisch.",
        ], "hallo").wenn_var("jtg:t2"),
        Dialog("flimmern", "vom der Höhle erzählen", [
            "Und du warst plötzlich hier?",
            "Das ist aber interessant.",
        ]).wenn_var("jtg:flimmern")

    ]
)
mieko.kampf(kampf_in_disnayenbum)
talisman_tag = Variable("jtg:nord:talisman_tag", 0, float)


def kirie_dlg() -> Iterable[Dialog]:
    def spielen(n: NSC, m: Mänx):
        # Zeit vergeht
        malp(f"Du spielst eine Weile mit {n.name}")
        m.sleep(10)
        if n.freundlich < 60:
            n.freundlich += 10
        if n.freundlich > 60:
            m.titel.add("Kinderfreund")

    def talisman(n: NSC, m: Mänx):
        n.sprich("Das?")
        malp("Kirie zeigt auf den Talisman um ihren Hals.")
        n.sprich("Das ist mein Schatz. Ich habe in gefunden. Damit kann ich mit "
                 "NoMuh reden.")
        n.sprich("Willst du auch mal?")
        if m.ja_nein("Nimmst du den Talisman?"):
            n.sprich("Gib ihn aber zurück, ja?")
            m.welt.setze_var(talisman_tag, m.welt.get_tag())
            n.sprich("Bis morgen, versprochen?")
            m.erhalte("Talisman des Verstehens", von=n)

    def talisman_zurück(n: NSC, m: Mänx):
        n.sprich("Danke")
        if m.welt.get_tag() > m.welt.obj(talisman_tag) + 1:
            n.sprich("Aber du bist zu spät.")
            n.freundlich -= 40
            n.sprich("Du bist nicht mehr mein/e Freund/in!")
            m.titel.add(_("Unzuverlässig"))
        else:
            m.titel.add(_("Bewahrer des großen Ehrenworts"))
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
    yield Dialog("talismanzurück", 'Talisman zurückgeben', talisman_zurück).wenn_mänx(
        lambda m: m.hat_item("Talisman des Verstehens"))
    yield Dialog("axtmann", '"Wie heißt der Mann mit der Axt?"', axtmann_r).wenn_mänx(
        lambda m: m.welt.am_leben("jtg:axtmann"))


kirie = StoryChar("jtg:kirie", ("Kirie", "Fórmayr", "Kind"),
                  startinventar={
    "Matschhose": 1,
    "Teddybär": 1,
    "Unterhose": 1,
    "BH": 1,
    "Mütze": 1,
    "Haarband": 1,
    "Nagel": 4,
    "Talisman des Verstehens": 1,
}, direkt_reden=True,
    vorstellen_fn=["Ein junges Mädchen spielt im Feld."], dialoge=list(kirie_dlg()))

kirie.kampf(kampf_in_disnayenbum)


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
@define
class Kiste:
    fach1: InventarBasis
    fach2: InventarBasis
    lina: NSC | None = None
    
    @classmethod
    def erzeuge(cls, _mänx: 'Mänx', /) -> Self:
        self = cls(InventarBasis(), InventarBasis())
        self.fach1.inventar.update({
            "Erbse": 4,
            "Karotte": 5,
            "Bohne": 13,
            "Reisportion": 2,
            "Tomate": 2,
        })
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
        return self

    def main(self, mänx: Mänx):
        if isinstance(mänx.context, ScenarioWegpunkt) and mänx.welt.am_leben("jtg:lina"):
            self.lina = mänx.welt.obj("jtg:lina")
        else:
            self.lina = None
        opts = [
            ("Fach 1 öffnen", "f1", self.öffne_fach1),
            ("Fach 2 öffnen", "f2", self.öffne_fach2),
            ("zerstören", "k", self.kampf),
            ("reden", "r", self.reden),
            ("zurück", "f", lambda m: Rückkehr.VERLASSEN)]
        mint("Du stehst vor einer Kiste.")
        while mänx.menu(opts, save=MethodSave(self.main))(mänx) == Rückkehr.WEITER_REDEN:
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
