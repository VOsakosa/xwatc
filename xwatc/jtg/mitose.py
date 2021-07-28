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
from xwatc.dorf import NSC, Dorf, Malp, NSCOptionen
from xwatc import weg
from xwatc import jtg
from xwatc import haendler
from xwatc.haendler import Preis
from xwatc.weg import Wegkreuzung
from typing import List, Tuple, Union, Sequence
__author__ = "jasper"

GEFUNDEN = "quest:saxaring:gefunden"


@register("jtg:saxa")
def erzeuge_saxa():
    n = NSC("Saxa Kautohoa", "Holzfällerin",
            startinventar={
                "Unterhose": 1,
                "Hemd": 1,
                "Strumpfhose": 1,
                "Socke": 1,
                "BH": 1,
                "Kappe": 1,
                "Hose": 1,
                "Gold": 14,
            }, vorstellen=[
                "Eine Holzfällerin von ungefähr 40 Jahren steht vor dir."])
    n.dialog("hallo", "Hallo", ["Hallo, ich bin Saxa."])
    n.dialog("bedrückt", "Bedrückt dich etwas?",
             [
                 "Ich habe beim Kräutersammeln meinen Ehering im Wald verloren.",
                 "Er hat uns beiden immer Glück gebracht.",
                 "Du bist doch ein Abenteurer, kannst du den Ring finden?"
             ], effekt=lambda n, m: m.welt.setze("quest:saxaring"))
    n.dialog("wo", "Wo warst du Kräuter sammeln?",
             ["Im Wald östlich von hier.",
              "Ein Pfad führt bis zur Stelle.",
              "Bei der Kreuzung musst du rechts abbiegen."], "bedrückt")

    def gefunden(n, m):
        n.add_freundlich(40, 100)
        n.erhalte("Saxas Ehering", von=m)
    n.dialog("gefunden", "Ich habe deinen Ring gefunden.",
             ["Danke!", "Das bedeutet uns sehr viel."],
             effekt=gefunden).wenn_var(GEFUNDEN).wenn(
                 lambda n, m: m.hat_item("Saxas Ehering"))
    n.dialog("verloren", "Ich habe deinen Ring gefunden, aber wieder verloren.",
             ["Was soll das jetzt heißen?", "Hast du ihn etwa verkauft?"],
             effekt=lambda n, m: n.add_freundlich(-30, -20)
             ).wenn_var(GEFUNDEN).wenn(
                 lambda n, m: not m.hat_item("Saxas Ehering"))
    return n


@weg.gebiet("jtg:mitose")
def erzeuge_norddörfer(mänx: Mänx):
    zur_mitte = weg.Gebietsende(
        None, "jtg:mitose", "mitose-mitte", "jtg:mitte")
    mitose = Dorf("Mitose")
    mitose_ort = mitose.orte[0]
    mitose_ort.verbinde(zur_mitte, "s")
    mitose_ort.beschreibungen.clear()
    mitose_ort.add_beschreibung([
        "Du bist im Ort Mitose.",
        "Ein Weg führt in Nord-Süd-Richtung durch das Dorf.",
        "Es gibt einen Pfad nach Osten in den Wald hinein."])
    mitose_ort.menschen.append(mänx.welt.obj("jtg:saxa"))
    mitose_ort.menschen.append(mänx.welt.obj("jtg:mädchen"))

    mitose_ort.verbinde(
        weg.Weg(
            0.5, weg.WegAdapter(None, t2_norden, "jtg:mitose:nord")), "n")

    kraut = Wegkreuzung(immer_fragen=True)
    kraut.add_effekt(kräutergebiet)
    kili = Wegkreuzung(immer_fragen=True)
    kili.add_effekt(mänx.welt.obj("jtg:kiliwolf").main)
    waldkreuz = Wegkreuzung()
    waldkreuz.add_beschreibung("Der Pfad gabelt sich.", nur="o")
    waldkreuz.add_beschreibung("Du kommst zurück an die Gabelung",
                               nur=["sw", "nw"])
    kraut.verbinde_mit_weg(waldkreuz, 0.25, "so", typ=weg.Wegtyp.PFAD)
    kili.verbinde_mit_weg(waldkreuz, 0.35, "no", typ=weg.Wegtyp.PFAD)
    waldkreuz.verbinde_mit_weg(mitose_ort, 0.4, "o", typ=weg.Wegtyp.PFAD)


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


def t2_norden(mänx: Mänx) -> None:
    """Das Dorf auf dem Weg nach Norden"""
    malp("Auf dem Weg kommen dir mehrfach Leute entgegen, und du kommst in ein kleines Dorf.")
    mädchen = mänx.welt.obj("jtg:mädchen")
    if mädchen.in_disnajenbum and not mädchen.tot:
        mädchen.main(mänx)
        malp("Das Mädchen verschwindet nach Norden.")
        mädchen.in_disnajenbum = False
        # TODO wohin?
    jtg.disnayenbum(mänx)


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
            "Rose": (1, Preis(10))
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
                        Malp("Das Mädchen zögert etwas."),
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
            self.sprich("Willst du für zehn Gold eine Rose kaufen?")
            mint("Das Mädchen spricht leise und vorsichtig, mit merkbar "
                 "schlechten Gewissen, denn eine Rose ist keine 10 Gold "
                 "wert.")
        else:
            self.sprich("Du hast mir mit dem Gold schon genug geholfen.")
            mint("Sie nickt mit dem Kopf, um dir zu danken.")

    def heißt(self, _mänx: Mänx):
        self.name = "Älen Kafuga"
        self.sprich("Älen, Älen Kafuga", warte=True)

    def helfen(self, mänx: Mänx):
        self.sprich('Willst du auch nach Gibon?')
        opts: List[Tuple[str, str, Sequence[Union[str, Malp]]]]
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
        malp("Am Wegesrand vor dem Dorfeingang siehst du ein Mädchen in Lumpen. "
              "Sie scheint zu frieren.")

    def get_preis(self, _) -> Preis:
        return Preis(0)

    def kampf(self, mänx: Mänx) -> None:
        malp("Das Mädchen ist schwach. Niemand hindert dich daran, sie "
              "auf offener Straße zu schlagen.")
        malp("Sie hat nichts außer ihren Lumpen.", end="")
        if self.hat_item("Rose"):
            malp(
                ", die Blume, die sie dir verkaufen wollte, ist beim Kampf zertreten worden.")
        else:
            malp(".")
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
        else:
            malp("Das Mädchen scheint alles an Kleidung zu brauchen.")
        return ans

    def kaufen(self, mänx: Mänx, name: str, anzahl: int=1)->bool:
        ans = super().kaufen(mänx, name, anzahl=anzahl)
        if ans and name == "Rose":
            malp("Das Mädchen ist dankbar für das Gold")
            self.freundlich += 10
        return ans
