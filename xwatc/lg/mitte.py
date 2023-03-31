"""
Das Zentrum der LG, die Stelle, wo man seine erste Himmelsrichtung wählt.
Created on 30.03.2023
"""
from xwatc.weg import gebiet, Gebiet, Wegkreuzung, WegAdapter, Eintritt, Gebietsende
from xwatc.system import Mänx
from xwatc.lg.norden import norden  # @UnusedImport
from xwatc.lg.westen import westen
from xwatc.lg.osten import osten # @UnusedImport
from xwatc.lg.süden import süden
__author__ = "jasper"


@gebiet("lg:mitte")
def himmelsrichtungen(mänx: Mänx, gb: Gebiet) -> Wegkreuzung:
    mitte = gb.neuer_punkt((0, 0), "Start")
    mitte.add_beschreibung([
        "Wohin gehst du jetzt? "
        "In Richtung Norden ist das nächste Dorf, im Süden warten "
        "Monster auf dich, im Westen liegt "
        "das Meer und der Osten ist unentdeckt."])
    mitte.verbinde(Gebietsende(None, gb, "norden", "lg:norden", "süden"), "n")
    mitte.verbinde(WegAdapter(None, süden.süden, "süden", gb), "s")
    mitte.verbinde(Gebietsende(None, gb, "osten", "lg:osten", "start"), "o")
    mitte.verbinde(WegAdapter(None, westen.westen, "westen", gb), "w")
    return mitte


MITTE = "lg:mitte"
MITTE_EINTRITT = Eintritt(MITTE)
