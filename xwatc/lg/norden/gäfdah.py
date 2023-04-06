
from xwatc.system import Mänx, Inventar
from xwatc.dorf import Dorf, ort, Malp
from random import randint
from xwatc.jtg import frau
from xwatc.lg.nsc.Wachen_von_Gäfdah import (
    SakcaBrauc, OrfGrouundt, ThomarcAizenfjäld)
from xwatc.lg.nsc.Bürger_von_Gäfdah import MartinPortulakk
from xwatc.lg.nsc import Freiwild  #@UnusedImport
from xwatc.nsc import StoryChar, Person


GÄFDAH_NAME = "Gäfdah"
STANDARDKLEIDUNG: Inventar = {
    "Schuh": 2,
    "Socke": 2,
    "Hose": 1,
    "Gürtel": 1,
    "Unterhose": 1,
    "Leinenhemd": 1,
}


def erzeuge_Gäfdah(mänx: Mänx) -> Dorf:
    from xwatc.lg.norden import fischfrisch
    d = Dorf.mit_draußen(GÄFDAH_NAME)
    kirche = ort("Kirche", d, [
        "Du bist in einer Kirche.",

    ])
    schenke = ort("Schenke", d, [
        "Du bist in einer Schenke.",
        "Sie ist voll von grölenden und betrunkenden Leuten."
    ])
    schmiede = ort("Schmiede", d, [
        "Du kommst in einen warmen, kleinen Raum, der irgendwie gemütlich wirkt und nach Schweiß riecht.",
        "Hinter der Theke steht ein bulliger Mann und verkauft wohl Waffen, Rüstungen und Anderes.",

    ])
    mänx.welt.obj("lg:norden:robert").ort = schmiede

    rathaus = ort("Rathaus", d, [
        "Du kommst in ein großes Haus mit Marmorfußboden.",
        "Drei Wachen kommen auf dich zu."
    ])

    haus1 = ort("Haus Nummer1", d, [
        "Du kommst in ein kleines Haus."
    ])
    assert fischfrisch.frau.id_
    mänx.welt.obj(fischfrisch.frau.id_).ort = kirche
    # schmiede.menschen.append(mänx.welt.get_or_else)
    # d.orte.append(schmiede)
    mänx.welt.obj("nsc:Wachen_von_Gäfdah:MarioWittenpfäld").ort = rathaus
    rathaus.add_nsc(mänx.welt, "nsc:Wachen_von_Gäfdah:SakcaBrauc", SakcaBrauc)
    mänx.welt.obj("nsc:freiwild:ruboic").ort = schenke
    rathaus.add_nsc(mänx.welt,
                    "nsc:Wachen_von_Gäfdah:ThomarcAizenfjäld", ThomarcAizenfjäld)
    haus1.add_nsc(mänx.welt,
                  "nsc:Bürger_von_Gäfdah:MartinPortulakk", MartinPortulakk)
    d.draußen.add_nsc(
        mänx.welt, "nsc:Wachen_von_Gäfdah:OrfGrouundt", OrfGrouundt)
    for _i in range(randint(2, 5)):
        w = frau.zu_nsc()
        d.draußen.menschen.append(w)
    return d


rob = StoryChar(
    "lg:norden:robert", ("Robert", "Nikc", "Schmiedegehilfe"), Person("m"),
    direkt_reden=True,
    startinventar=STANDARDKLEIDUNG | {
        "Schal": 1,
        "Messer": 1,
    },
    vorstellen_fn=["Ein sommersprössiger Junge von ca. 18 Jahren mit "
                   "kurzen, braunen Haaren steht an der Theke der Schmiede."]
)

rob.dialog("helfen", '"Du siehst bedrückt aus. Kann ich dir helfen?"', [
    "Mein Bruder ist verschwunden.",
    Malp('Du: "Wie heißt er? Ich melde mich, falls der Lümmel mir über den Weg läuft."'),
    "Äh, Lümmel?",
    Malp('Du: "Ich dachte, er sei entlaufen."'),
    "So etwas würde er nie tun! Er war auf dem Weg nach Aizenfjäld,",
    "aber er wurde danach nicht mehr gefunden!",
    "Er heißt Gaa. Alle sagen immer, er sieht mir sehr ähnlich."
],
    "hallo")
rob.dialog("schmied", '"Wo ist der Schmied?"',
           ["Der ist weiter hinten.", "...müsste er sein."])


if __name__ == '__main__':
    mänx = Mänx()
    mänx.welt.get_or_else("Gäfdah", erzeuge_Gäfdah, mänx).main(mänx)
