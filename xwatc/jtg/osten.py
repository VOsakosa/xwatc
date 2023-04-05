"""
Der Osten von JTG. Zunächst einmal leer bis auf die Wege von Disnayenbum, Scherenfeld und Gibon,
die sich hier treffen.

Created on 05.04.2023
"""
from xwatc.weg import Eintritt
from xwatc import weg
from xwatc import jtg
from xwatc.system import Mänx
from xwatc.jtg import tauern
from xwatc.jtg import nord
__author__ = "jasper"

GEBIET = "jtg:osten"
no_tauern = Eintritt(GEBIET, "tauern")
no_dis = Eintritt(GEBIET, "disnayenbum")
no_süd = Eintritt(GEBIET, "süd")


@weg.gebiet(GEBIET)
def erzeuge_osten(mänx: Mänx, gb: weg.Gebiet) -> None:
    ng = gb.neuer_punkt((0, 1), "nach_disnayenbum", immer_fragen=False)
    # TODO: Dieser Punkt darf nicht nach Norden verbunden werden.
    ng.verbinde(gb.ende(no_dis, nord.eintritt_ost), "w")
    ng.bschr("Der Weg windet sich aus dem Wald heraus, an den Rand einer windigen Hügelebene.",
             nur="w")

    abzweig = gb.neuer_punkt((2, 1), "Abzweig")
    abzweig.bschr(
        "Du folgst dem Weg sehr lange den Fluss aufwärts.", nur="o")
    abzweig.bschr("Du kommst an einen Wegweiser.")
    abzweig.bschr("Der Weg gabelt sich an einem kleinen Fluss, links führt der Weg "
                  "den Fluss aufwärts zum 'Land der aufrechten Kühe' und rechts "
                  f"führt der Weg flussabwärts nach '{jtg.SÜD_DORF_NAME}'", nur="w")
    abzweig.bschr((
        "Ein Weg führt nach Westen nach 'Disnayenbum'.",
        "Der Weg, auf dem du warst führt vom 'Land der aufrechten Kühe' im Nordosten "
        f"nach '{jtg.SÜD_DORF_NAME}' im Süden."
                   ), nur=("s", "o"))
    gb.neuer_punkt((3,1), "nach_tauern", immer_fragen=False).verbinde(
        gb.ende(no_tauern, tauern.land_der_kühe), "nw")
    gb.neuer_punkt((2, 8), "Bogen Süd", immer_fragen=False).bschr(
        "Zusammen mit dem Fluss macht der Weg einen Bogen in Richtung Westen", nur="n").bschr(
        "Zusammen mit dem Fluss macht der Weg einen Bogen in Richtung Norden", nur="w")
    gb.neuer_punkt((0,8), "Zugang Süd", immer_fragen=False).verbinde(
        gb.ende(no_süd, jtg.süd_dorf_ost), "w")


if __name__ == '__main__':
    from xwatc.anzeige import main
    main(no_tauern)
