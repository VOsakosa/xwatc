"""
Das Dorf Gibon, direkt am Anfang von Tauern.


Created on 09.08.2021
"""
from xwatc.dorf import Dorf, ort
from xwatc.system import register


@register("jtg:tau:gibon")
def erzeuge_gibon():
    gibon = Dorf.mit_struktur("gibon", [])
    osttor = ort("Osttor", gibon, "Ein kleines Stadttor")
    westtor = ort("Westtor", gibon, "Ein belebtes Stadttor")
    platz = ort("Anger", gibon, "Ein großer Platz, über der die Kirche thront.")
    osttor - platz - westtor
    kirche = ort("Kirche", gibon)
    platz - kirche
    return gibon
