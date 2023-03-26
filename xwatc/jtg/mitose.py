"""
Das Dorf zwischen der Lichtung und dem Disnayenbum.

Treffen auf Elen und Quest nach Ehering.

Ehering
-------

Die Holzfällerin Saxa hat beim Kräutersammeln im Wald westlich von Mitose
ihren Ehering verloren. Sie glaubt, dass der Ring ihr und ihrem Mann
Glück gebracht hat und sorgt sich. Der Ehering ist bei den Kräutern.
Links abbiegen führt zu Kiri-Wölfen=> Kampf

"""
from xwatc.system import Mänx, register, malp, HatMain, mint
from xwatc.dorf import Dorf, Malp, Dialog, Ort, Zeitpunkt
from xwatc import weg
from xwatc import jtg
from xwatc.haendler import Preis, mache_händler, HandelsFn
from xwatc.weg import kreuzung
from typing import List, Tuple, Sequence
from xwatc.nsc import Person, StoryChar, bezeichnung, NSC
__author__ = "jasper"

GEFUNDEN = "quest:saxaring:gefunden"
ABGEGEBEN = "quest:saxaring:abgegeben"


saxa = StoryChar("jtg:saxa", ("Saxa", "Kautohoa", "Holzfällerin"), Person("w"),
                 startinventar={
    "Unterhose": 1,
    "Hemd": 1,
    "Strumpfhose": 1,
    "Socke": 1,
    "BH": 1,
    "Kappe": 1,
    "Hose": 1,
    "Gold": 14,
}, vorstellen_fn=[
    "Eine Holzfällerin von ungefähr 40 Jahren steht vor dir."],
)

saxa.dialog("hallo", "Hallo", ["Hallo, ich bin Saxa."])
saxa.dialog("bedrückt", "Bedrückt dich etwas?",
            [
                "Ich habe beim Kräutersammeln meinen Ehering im Wald verloren.",
                "Er hat uns beiden immer Glück gebracht.",
                "Du bist doch ein Abenteurer, kannst du den Ring finden?"
            ], effekt=lambda n, m: m.welt.setze("quest:saxaring")).wenn(
    lambda n, m: not m.welt.ist(ABGEGEBEN))
saxa.dialog("wo", "Wo warst du Kräuter sammeln?",
            ["Im Wald östlich von hier.",
                  "Ein Pfad führt bis zur Stelle.",
                  "Bei der Kreuzung musst du rechts abbiegen."], "bedrückt")


def gefunden(n, m):
    n.add_freundlich(40, 100)
    n.erhalte("Saxas Ehering", von=m)
    m.welt.setze(ABGEGEBEN)


saxa.dialog("gefunden", "Ich habe deinen Ring gefunden.",
            ["Danke!", "Das bedeutet uns sehr viel."],
            effekt=gefunden).wenn_var(GEFUNDEN).wenn(
    lambda n, m: m.hat_item("Saxas Ehering"))

saxa.dialog("verloren", "Ich habe deinen Ring gefunden, aber wieder verloren.",
            ["Was soll das jetzt heißen?", "Hast du ihn etwa verkauft?"],
            effekt=lambda n, m: n.add_freundlich(-30, -20)
            ).wenn(
    lambda n, m: (
        m.welt.ist(GEFUNDEN)
        and not m.welt.ist(ABGEGEBEN)
        and not m.hat_item("Saxas Ehering")))


@weg.gebiet("jtg:mitose")
def erzeuge_norddörfer(mänx: Mänx) -> weg.Wegpunkt:
    zur_mitte = weg.Gebietsende(
        None, "jtg:mitose", "mitose-mitte", "jtg:mitte")
    mitose = Dorf("Mitose")
    mitose_ort = mitose.orte[0]
    mitose_ort.verbinde(zur_mitte, "s")
    mitose_ort.beschreibungen.clear()
    mitose_ort.add_beschreibung([
        "Du bist im Ort Mitose.",
        "Ein Weg führt in Nord-Süd-Richtung durch das Dorf.",
        "Es gibt einen Pfad nach Westen in den Wald hinein."])
    mitose_ort.menschen.append(mänx.welt.obj("jtg:saxa"))
    mitose_ort.menschen.append(mänx.welt.obj("jtg:mädchen"))

    mitose_ort.verbinde(
        weg.Weg(
            0.5, weg.WegAdapter(None, jtg.disnayenbum, "jtg:mitose:nord")), "n")
    hinterhof = Ort("Hinterhof", mitose,
                    "Ein unkrautbewucherter Hinterhof des Rathaus.")
    mitose_ort.verbinde(hinterhof)

    kraut = kreuzung("kraut", immer_fragen=True)
    kraut.add_effekt(kräutergebiet)
    kili = kreuzung("kili", immer_fragen=True)
    kili.add_effekt(mänx.welt.obj("jtg:kiliwolf").main)
    waldkreuz = kreuzung("waldkreuz")
    waldkreuz.add_beschreibung("Der Pfad gabelt sich.", nur="o")
    waldkreuz.add_beschreibung("Du kommst zurück an die Gabelung",
                               nur=["sw", "nw"])
    kraut.verbinde_mit_weg(waldkreuz, 0.25, "so", typ=weg.Wegtyp.PFAD)
    kili.verbinde_mit_weg(waldkreuz, 0.35, "no", typ=weg.Wegtyp.PFAD)
    waldkreuz.verbinde_mit_weg(mitose_ort, 0.4, "o", typ=weg.Wegtyp.PFAD)
    return mitose_ort


def kräutergebiet(mänx: Mänx):
    """Der Ort, wo Kräuter und der Ring zu finden sind."""
    malp("Der Weg endet an einer Lichtung, die mit Kräutern bewachsen ist.")
    ring = (
        mänx.welt.ist("quest:saxaring") and
        not mänx.welt.ist(GEFUNDEN)
    )
    if ring:
        if mänx.ja_nein("Willst du nach dem Ring suchen?"):
            mänx.welt.tick(1 / 48)
            malp("Du suchst eine Weile, bis du ihn von einem Kraut verdeckt findest.")
            mänx.welt.setze("quest:saxaring:gefunden")
            mänx.erhalte("Saxas Ehering")
    if mänx.ja_nein("Pflückst du einige Kräuter?"):
        mänx.welt.tick(1 / 96)
        treffen = False
        if mänx.welt.is_nacht():
            treffen = mänx.welt.obj("jtg:kiliwolf").main(mänx)
        if not treffen:
            mänx.erhalte("Xaozja", 14)


@register("jtg:kiliwolf")
class Kiliwolf(HatMain):
    def __init__(self):
        super().__init__()
        self.auftauchen = 0.0

    def main(self, mänx: Mänx) -> bool:
        if mänx.welt.tag >= self.auftauchen:
            self.auftauchen = mänx.welt.tag + 4
            malp("Ein Pack Kiliwölfe greift dich an.")
            malp("Kiliwölfe sehen aus wie Wölfe, haben aber Scheren statt "
                 "Vorderpfoten.")
            # TODO
            return True
        return False


def in_disnayenbum(nsc: NSC, _mänx: Mänx) -> bool:
    return "gefährte" not in nsc.variablen


def als_gefährte(nsc: NSC, _mänx: Mänx) -> bool:
    return "gefährte" in nsc.variablen


älen = StoryChar("jtg:mädchen", "Mädchen", Person("w"), {
    "BH": 1,
    "Unterhose": 1,
    "Socke": 2,
    "Schuh": 2,
    "Lumpen": 1,
})

älen.dialog("vorstellen", "Vorstellen", [
    Malp("Am Wegesrand vor dem Dorfeingang siehst du ein Mädchen in Lumpen."),
    Malp("Sie scheint zu frieren."),
    Malp("Sie verkauft Rosen.")
], zeitpunkt=Zeitpunkt.Vorstellen).wenn(in_disnayenbum)

handel = mache_händler(älen, kauft=["Kleidung"], verkauft={
    "Rose": (1, Preis(10))
}, aufpreis=0.).wenn(in_disnayenbum)


älen.dialog("rose", "Woher hast du die Rose?",
            ["Die Rosen wachsen hier im Wald, aber es ist gefährlich,"
             " sie zu holen."], "hallo").wenn(in_disnayenbum)
älen.dialog("woher", "Woher kommst du?",
                     ["Ich komme aus Grökrakchöl, das liegt im Süden."],
                     "hallo", wiederhole=1)
älen.dialog("allein", "Warum bist du allein? Hast du einen Grund, nicht nach "
            "*Grökaköl zurückkehren zu können?",
            [
                Malp("Das Mädchen zögert etwas."),
                "Ich ...",
                "Ich bin geflohen. Nach dem Tod meiner Mutter hatte "
                "meine Familie finanzielle Schwierigkeiten.",
                "Ich sollte verheiratet werden.",
                "Darüber gerieten wir in Streit, und ich floh, um "
                "zu meinen Großeltern in Gibon zu kommen."
            ], "woher", min_freundlich=10, wiederhole=1)


@älen.dialog_deco("hallo", "Hallo, kann ich dir helfen?")
def älen_hallo(self: NSC, _mänx: Mänx):
    if not self.hat_item("Gold"):
        self.sprich("Willst du für zehn Gold eine Rose kaufen?")
        mint("Das Mädchen spricht leise und vorsichtig, mit merkbar "
             "schlechten Gewissen, denn eine Rose ist keine 10 Gold "
             "wert.")
    else:
        self.sprich("Du hast mir mit dem Gold schon genug geholfen.")
        mint("Sie nickt mit dem Kopf, um dir zu danken.")


@älen.dialog_deco("heißt", "Wie heißt du?", "hallo")
def heißt(self: NSC, _mänx: Mänx):
    self.bezeichnung = bezeichnung(("Älen", "Kafuga", "Mädchen"))
    self.sprich("Älen, Älen Kafuga", warte=True)


@älen.dialog_deco("helfen", "Das ist ja schrecklich! Ich helfe dir, nach  Gibon zu kommen.",
                  "allein", wiederhole=1)
def helfen(self: NSC, mänx: Mänx):
    self.sprich('Willst du auch nach Gibon?')
    opts: List[Tuple[str, str, Sequence[str | Malp]]]  # @UnusedVariable
    opts = [
        ('»irgendwann«', "irgendwann",
         [Malp('"Nein, ich erkunde hier die Gegend, irgendwann werde ich '
               'nach Gibon kommen."'),
          "Kann ich dann trotzdem mit dir mit? Es macht mir nichts aus, "
          "wenn wir nicht direkt nach Gibon gehen."]),
        ("»ja«", 'ja', "Dann gehe ich mit dir mit."),
        ("»nein«", '»Nein, aber ich kann dich trotzdem dahin bringen.«',
         "Ist das wirklich in Ordnung? Danke!")
    ]
    antwort = mänx.menu(opts)  # TODO kaputt
    self.sprich(antwort)
    self.variablen.add("gefährte")
    mänx.add_gefährte(self)


älen.dialog("gibon", '"Wo ist Gibon eigentlich?"',
                     ["In Tauern, direkt hinter der Grenze.",
                      "Tauern liegt im Nordosten von Jotungard."], "helfen")

älen.dialog("großeltern", '"Wie sind deine Großeltern so?"',
            ["Mein Aba ist ein strenger Mann. Er schätzt Disziplin "
             "über alles, aber er ist eigentlich ganz nett.",
             "Meine Ama ist emotional sehr intelligent. Sie ergänzen "
             "sich echt gut.",
             "Ich habe sie selten gesehen, weil sie weit weg wohnen "
             "und sie meinen Vater nicht schätzten."
             ], "helfen")
älen.dialog("grökrakchöl", '„Hast du keine Bekannten mehr in Grökrakchöl?"',
            ["Nein, zumindest keine, die ich sehr gut kenne.",
             ], "helfen")
älen.dialog("waffe", '', [
            "Ich hätte gerne eine Waffe.",
            "Ich muss mich doch irgendwie wehren können."
            "Dann kann ich dir auch helfen."
            ], "helfen", zeitpunkt=Zeitpunkt.Ansprechen, wiederhole=0).wenn(
    lambda n, __: not n.hat_klasse("Waffe"))


@älen.dialog_deco("umarmen", '"Kann ich dich umarmen?"', "helfen", min_freundlich=30)
def umarmen(self: NSC, mänx: Mänx) -> None:
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


@älen.kampf
def älen_kampf(self, mänx: Mänx) -> None:
    malp("Das Mädchen ist schwach. Niemand hindert dich daran, sie "
         "auf offener Straße zu schlagen.")
    malp("Sie hat nichts außer ihren Lumpen.", end="")
    if self.hat_item("Rose"):
        malp(
            ", die Blume, die sie dir verkaufen wollte, ist beim Kampf zertreten worden.")
        del self.inventar["Rose"]
    else:
        malp(".")
    self.plündern(mänx)
    self.tot = True


älen_kampf.wenn(in_disnayenbum)

handel_fn = handel.geschichte
assert isinstance(handel_fn, HandelsFn)


@handel_fn.verkaufen_hook
def verkaufen(nsc: NSC, mänx: Mänx, name: str, preis: Preis, anzahl: int = 1) -> None:
    if name == "Unterhose":
        malp("Das Mädchen ist sichtlich verwirrt, dass "
             "du ihr eine Unterhose gegeben hast.")
        mint("Es hält sie vor sich und mustert sie. Dann sagt sie artig danke.")
        mänx.titel.add("Perversling")
    elif name == "Mantel":
        malp("Das Mädchen bedeutet dir, dass sie nur den halben Mantel braucht.")
        malp("Du schneidest den Mantel entzwei, und gibst ihr nur die Hälfte.")
        mänx.inventar["halber Mantel"] += 1
        mänx.titel.add("Samariter")
        nsc.freundlich += 10
    else:
        malp("Das Mädchen scheint alles an Kleidung zu brauchen.")


@handel_fn.kaufen_hook
def kaufen(nsc: NSC, mänx: Mänx, name: str, preis: Preis, anzahl: int = 1) -> None:
    if name == "Rose":
        nsc.freundlich += 10
        malp("Das Mädchen ist dankbar für das Gold.")


if __name__ == '__main__':
    import xwatc.anzeige
    xwatc.anzeige.main(erzeuge_norddörfer)
