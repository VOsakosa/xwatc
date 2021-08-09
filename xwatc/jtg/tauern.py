"""
Tauern, das Land der aufrechten Kühe.
Created on 15.10.2020
"""
from xwatc import weg
from xwatc.dorf import NSC
__author__ = "jasper"
from xwatc.system import Mänx, register
from xwatc.weg import gebiet, WegAdapter, Wegkreuzung, Wegtyp

ZOLL_PREIS = 10

KRIEGER_INVENTAR = {
    "Axt": 1,
    "Lederrüstung": 1,
    "Lederhose": 1,
    "Lendenschurz": 1,
    "Leibchen": 1,
    "Armband": 1,
    "Sandalen": 1,
    "Gold": 10
}


def land_der_kühe(mänx: Mänx):
    return weg.wegsystem(mänx, "jtg:tauern")


def rückweg(mänx: Mänx):
    """Gehe aus Tauern wieder zurück."""
    import xwatc.jtg
    xwatc.jtg.tauern_ww_no(mänx)


@gebiet("jtg:tauern")
def erzeuge_tauern(__) -> WegAdapter:
    ein_adap = WegAdapter(None, rückweg)
    eintritt = Wegkreuzung("eintritt", sw=ein_adap)
    eintritt.add_beschreibung([
        "Der Weg führt weiter am Fluss entlang, das Land wird hügeliger.",
        "Die Vegetation wird spärlicher.",
    ], nur="sw")
    eintritt.add_beschreibung([
        "Der Weg folgt dem Fluss in einen Wald."], nur="no")

    vorbrück = Wegkreuzung("vorbrück")
    vorbrück.verbinde_mit_weg(eintritt, 0.3, "sw", None, Wegtyp.WEG, "Jotungard",
                              "Tauern")
    vorbrück.add_beschreibung([
        "Der Weg überquert den Fluss in einer hölzernen Brücke, "
        "sie ist aber durch ein Zollhaus gesichert.",
        "Ein Trampelpfad führt aber weiter den Fluss entlang."], nur="sw")
    vorbrück.add_beschreibung([
        "Der Weg nach Jotungard folgt dem Fluss auf der rechten Seite.",
        "Die Brücke führt nach Tauern."], außer="sw")
    vorbrück.add_beschreibung(
        "Ein Trampelpfad führt den Fluss entlang nach rechts.", nur="brücke")

    steilwand = Wegkreuzung("steilwand", immer_fragen=True)
    vorbrück.verbinde_mit_weg(
        steilwand, 0.05, "no", None, Wegtyp.TRAMPELPFAD, beschriftung_zurück="Brücke"
    )
    steilwand.add_beschreibung(
        "Du kommst an einen steilen Berg, der in den Fluss "
        "ragt. Ohne Kletterkünste ist hier kein Vorbeikommen.")

    zoll = weg.WegSperre(None, None, zoll_fn, zoll_fn)
    vorbrück.verbinde(zoll, "o", ziel="Über die Brücke")
    
    hinterbrück = Wegkreuzung("hinterbrück", immer_fragen=True, w=zoll)
    hinterbrück.add_beschreibung("Vor dir liegt nun Tauern.", "w")
    hinterbrück.add_beschreibung("Du kommst an eine Zollbrücke.", "o")

    return ein_adap


def zoll_fn(mänx: Mänx):
    wächter = mänx.welt.obj("jtg:tau:wächter")
    if wächter.tot:
        mänx.ausgabe.malp("Das Zollhaus ist leer.")
        return True
    kosten = (1 + len(mänx.gefährten)) * ZOLL_PREIS
    wächter.sprich(f"Das macht dann {kosten} Gold.")
    if mänx.ja_nein("Zahlst du das Geld?"):
        mänx.erhalte("Gold", -kosten)
        return True
    else:
        return False


@register("jtg:tau:wächter")
class Zollwärter(NSC):
    """Der Zollwärter bewacht die Brücke."""

    def __init__(self):
        super().__init__("Federico", "Pestalozzi",
                         startinventar=KRIEGER_INVENTAR)
        self.inventar["Uniform"] += 1
        self.rasse = "Mumin"


if __name__ == '__main__':
    import xwatc.anzeige
    xwatc.anzeige.main(land_der_kühe)
