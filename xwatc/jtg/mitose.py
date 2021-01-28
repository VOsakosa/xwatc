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
from xwatc.system import Mänx, register, malp, HatMain
from xwatc.dorf import NSC, Dorf
from xwatc import weg
from xwatc import jtg
from xwatc.weg import Wegkreuzung
__author__ = "jasper"


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
            }, vorstellen="Eine Holzfällerin von ungefähr 40 Jahren steht vor dir.")
    n.dialog("hallo", "Hallo", "Hallo, ich bin Saxa.")
    n.dialog("bedrückt", "Bedrückt dich etwas?",
             [
                 "Ich habe beim Kräutersammeln meinen Ehering im Wald verloren.",
                 "Er hat uns beiden immer Glück gebracht.",
                 "Du bist doch ein Abenteurer, kannst du den Ring finden?"
             ])
    # Dialog für Ehering-Suche
    return n

@weg.gebiet("jtg:mitose")
def erzeuge_norddörfer(mänx: Mänx):
    zur_mitte = weg.Gebietsende(None, "jtg:mitose", "mitose-mitte", "jtg:mitte")
    mitose = Dorf("Mitose")
    mitose_ort = mitose.orte[0]
    mitose_ort.verbinde(zur_mitte, "s")
    
    mitose_ort.verbinde(
        weg.Weg(
            0.5, weg.WegAdapter(None, jtg.t2_norden, "jtg:mitose:nord")), "n")
    
    kraut = Wegkreuzung(immer_fragen=True)
    kraut.add_effekt(kräutergebiet)
    kili = Wegkreuzung(immer_fragen=True)
    kili.add_effekt(mänx.welt.obj("jtg:kiliwolf").main)
    waldkreuz = Wegkreuzung()
    kraut.verbinde_mit_weg(waldkreuz, 0.25, "so", typ=weg.Wegtyp.PFAD)
    kili.verbinde_mit_weg(waldkreuz, 0.35, "no", typ=weg.Wegtyp.PFAD)
    waldkreuz.verbinde_mit_weg(mitose_ort, 0.4, "o", typ=weg.Wegtyp.PFAD)


def kräutergebiet(mänx: Mänx):
    """Der Ort, wo Kräuter und der Ring zu finden sind."""
    malp("Der Weg endet an einer Lichtung, die mit Kräutern bewachsen ist.")
    ring = (
        mänx.welt.ist("quest:saxaring") and 
        not mänx.welt.ist("quest:saxaring:gefunden")
        )
    if ring:
        if mänx.ja_nein("Willst du nach dem Ring suchen?"):
            mänx.welt.tick(1/48)
            malp("Du suchst eine Weile, bis du ihn von einem Kraut verdeckt findest.")
            mänx.welt.setze("quest:saxaring:gefunden")
            mänx.erhalte("Saxas Ehering")
    if mänx.ja_nein("Pflückst du einige Kräuter?"):
        mänx.welt.tick(1/96)
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

