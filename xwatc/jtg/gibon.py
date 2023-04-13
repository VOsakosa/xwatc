"""
Das Dorf Gibon, direkt am Anfang von Tauern.

Notizen
- Die Göttin der Kirche heißt Ridna, Göttin des Mondes.

Created on 09.08.2021
"""
from xwatc.weg.dorf import Dorf, ort
from xwatc.nsc import Person, Rasse, StoryChar
from xwatc.effect import TextGeschichte, Warten
from xwatc.system import Mänx
from xwatc import weg


def erzeuge_gibon(mänx: Mänx, gebiet: weg.Gebiet) -> Dorf:
    gibon = Dorf.mit_struktur("gibon", gebiet, [])
    osttor = ort("Osttor", gibon, "Ein kleines Stadttor.")
    westtor = ort("Westtor", gibon, "Ein belebtes Stadttor.")
    platz = ort("Anger", gibon, "Ein großer Platz, über der die Kirche thront.")
    osttor - platz - westtor
    kirche = ort("Kirche", gibon, "Du betrittst die Kirche, ein riesiges Gebäude. "
                 "An den Seiten sind Bilder und Statuen von Frauen, die alle den gleichen "
                 "runden Kopfschmuck tragen.")
    platz - kirche
    kirche.add_option("Beten", "beten", TextGeschichte(
        ("Du betest für die Göttin dieser Kirche.", Warten(5)), titel="Anhänger Ridnas"))
    assert pastorin.id_
    kirche.add_char(mänx.welt, pastorin)
    return gibon


pastorin = StoryChar(
    "jtg:tau:pastorin", ("Elster", "Rinami",
                         "Pastorin"), Person("w", Rasse.Munin),
    startinventar={
        "Mantel": 1,
        "BH": 1,
        "Ehering": 1,
    },
    vorstellen_fn="Elster Rinami ist die Pastorin dieser Kirche. Sie trägt einen vollmondförmigen "
    "Kopfschmuck.")

pastorin.dialog("hallo", "Hallo!", ("Hallo!",
                "Schön, dich hier zu sehen. Warum bist du hier?"))
pastorin.dialog("tür", "Weißt du etwas über Türen, die einen an weit entfernte Orte bringen?", (
    "Du meinst Portale?...", "Hier in Gibon ist keins, das ist sicher.",
    "Die Macht der großen Göttin Ridna manifestiert sich in seltsamen Weisen.",
), "hallo").wenn_var("jtg:t2")
pastorin.dialog("mond", "Warum tragen die Statuen und du so einen mondförmigen Schmuck?", (
    "Das symbolisiert unsere Göttin Ridna, auch Göttin des Mondes genannt."
), "hallo")
