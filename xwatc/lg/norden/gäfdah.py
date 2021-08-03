from xwatc.system import Mänx, minput, ja_nein, Spielende, mint, sprich, register
from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner, Dialog, Malp
from random import randint
from . Maria_Fischfrisch import Fischerfrau  # pylint: disable=relative-beyond-top-level
from xwatc.jtg import Waschweib
from xwatc.nsc.Wachen_von_Gäfdah import (MarioWittenpfäld,
                                         SakcaBrauc, OrfGrouundt, ThomarcAizenfjäld)
from xwatc.nsc.Bürger_von_Gäfdah import MartinPortulakk
from xwatc.nsc.Freiwild import RuboicHätxrik


GÄFDA_NAME = "Gäfda"
STANDARDKLEIDUNG = {
    "Schuh": 2,
    "Socke": 2,
    "Hose": 1,
    "Gürtel": 1,
    "Unterhose": 1,
    "Leinenhemd": 1,
}


def erzeuge_Gäfdah(mänx:  Mänx) -> Dorf:
    d = Dorf(GÄFDA_NAME)
    kirche = Ort("Kirche", d, [
        "Du bist in einer Kirche.",

    ])
    schenke = Ort("Schenke", d, [
        "Du bist in einer Schenke.",
        "Sie ist voll von grölenden und betrunkenden Leuten."
        
    
    ])
    schmiede = Ort("Schmiede", d, [
        "Du kommst in einen warmen, kleinen Raum, der irgendwie gemütlich wirkt und nach Schweiß riecht.",
        
        "Hinter der Theke steht ein bulliger Mann und verkauft wohl Waffen, Rüstungen und Anderes.",

    ])
    mänx.welt.obj("lg:norden:robert").ort = schmiede

    rathaus = Ort("Rathaus", d, [
        "Du kommst in ein großes Haus mit Marmorfußboden.",

        "Drei Wachen kommen auf dich zu."


    ])

    haus1 = Ort("Haus Nummer1", d, [
        "Du kommst in ein kleines Haus."
    ])
    mänx.welt.get_or_else(
        "lg:norden:Maria_Fischfrisch:maria_fischfrisch", Fischerfrau).ort = kirche
    # schmiede.menschen.append(mänx.welt.get_or_else)
    # d.orte.append(schmiede)
    rathaus.add_nsc(mänx.welt,
                    "nsc:Wachen_von_Gäfdah:MarioWittenpfäld", MarioWittenpfäld)
    rathaus.add_nsc(mänx.welt, "nsc:Wachen_von_Gäfdah:SakcaBrauc", SakcaBrauc)
    schenke.add_nsc(mänx.welt, "nsc:Freiwild:RuboicHätxrik", RuboicHätxrik)
    rathaus.add_nsc(mänx.welt,
                    "nsc:Wachen_von_Gäfdah:ThomarcAizenfjäld", ThomarcAizenfjäld)
    haus1.add_nsc(mänx.welt,
                  "nsc:Bürger_von_Gäfdah:MartinPortulakk", MartinPortulakk)
    d.orte[0].add_nsc(
        mänx.welt, "nsc:Wachen_von_Gäfdah:OrfGrouundt", OrfGrouundt)
    for _i in range(randint(2, 5)):
        w = Waschweib()
        d.orte[0].menschen.append(w)
    # TODO weitere Objekte
    return d


@register("lg:norden:robert")
def robert() -> NSC:
    rob = Dorfbewohner(
        "Robert Nikc", True,
        art="Schmiedegehilfe",
        direkt_reden=True,
        startinventar={
            "Schal": 1,
            "Messer": 1,
        },
        vorstellen=["Ein sommersprössiger Junge von ca. 18 Jahren mit "
                    "kurzen, braunen Haaren steht an der Theke der Schmiede."])
    rob.inventar.update(STANDARDKLEIDUNG)
    return rob

def rob_dlg():
    yield Dialog("helfen", '"Du siehst bedrückt aus. Kann ich dir helfen?"',
               ["Mein Bruder ist verschwunden.",
                Malp(
                    'Du: "Wie heißt er? Ich melde mich, falls der Lümmel mir über den Weg läuft."'),
                "Äh, Lümmel?",
                Malp('Du: "Ich dachte, er sei entlaufen."'),
                "So etwas würde er nie tun! Er war auf dem Weg nach Aizenfjäld,",
                "aber er wurde danach nicht mehr gefunden!",
                "Er heißt Gaa. Alle sagen immer, er sieht mir sehr ähnlich."],
               "hallo")
    yield Dialog("schmied", '"Wo ist der Schmied?"',
               ["Der ist weiter hinten.", "...müsste er sein."])


if __name__ == '__main__':
    mänx = Mänx()
    mänx.welt.get_or_else("Gäfdah", erzeuge_Gäfdah, mänx).main(mänx)
