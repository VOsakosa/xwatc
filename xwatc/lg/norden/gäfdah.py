from time import sleep
from xwatc import haendler
from xwatc import scenario
from xwatc.system import Mänx, minput, ja_nein, Spielende, mint, sprich
from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner, Dialog
from random import randint
from . Maria_Fischfrisch import Fischerfrau
import random
from xwatc.jtg.ressourcen import FRAUENNAMEN
from xwatc.jtg import TobiacBerndoc, zufälliges_waschweib


GÄFDA_NAME = "Gäfda"


def erzeuge_Gäfdah(mänx) -> Dorf:
    d = Dorf(GÄFDA_NAME)
    kirche = Ort("Kirche", [
        "Du bist in einer Kirche.",
    
    ])
    
    schmiede = Ort("Schmiede", [
        "Du kommst in einen warmen, kleinen Raum, der irgendwie gemütlich wirkt und nach Schweiß riecht."
        
        "Hinter der Theke steht ein bulliger Mann und verkauft wohl Waffen, Rüstungen und Anderes."
    
    ])
    
    rathaus = Ort("Rathaus", [
        "Du kommst in ein großes Haus mit Marmorfußboden.",
        
        "Drei Wachen kommen auf dich zu."
        
    
    ])
    
    haus1 = Ort("Haus Nummer1", [
        "Du kommst in ein kleines Haus."
    
    ])
    kirche.menschen.append(mänx.welt.get_or_else(
        "lg:norden:Maria_Fischfrisch:maria_fischfrisch", Fischerfrau))
    d.orte.append(kirche)
    schmiede.menschen.append(mänx.welt.get_or_else(
        "jtg:m:tobiac", TobiacBerndoc))
    d.orte.append(schmiede)
    rathaus.menschen.append(mänx.welt.get_or_else(
        "jtg:m:tobiac", TobiacBerndoc))
    d.orte.append(rathaus)
    haus1.menschen.append(mänx.welt.get_or_else(
        "jtg:m:tobiac", TobiacBerndoc))
    d.orte.append(haus1)
    for _i in range(randint(2, 5)):
        w = zufälliges_waschweib()
        d.orte[0].menschen.append(w)
    # TODO weitere Objekte
    return d

if __name__ == '__main__':
    mänx = Mänx()
    mänx.welt.get_or_else("Gäfdah", erzeuge_Gäfdah, mänx).main(mänx)