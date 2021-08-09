"""
Das Dorf Gibon, direkt am Anfang von Tauern.


Created on 09.08.2021
"""
from xwatc.dorf import Dorf, Ort
from xwatc.system import register


@register("jtg:tau:gibon")
def erzeuge_gibon():
    gibon = Dorf("gibon", [])
    osttor = Ort("Osttor", gibon, "Ein kleines Stadttor")
    westtor = Ort("Westtor", gibon, "Ein belebtes Stadttor")
    platz = Ort("Anger", gibon, "Ein großer Platz, über der die Kirche thront.")
    osttor - platz - westtor
    kirche = Ort("Kirche", gibon)
    platz - kirche
    return gibon
