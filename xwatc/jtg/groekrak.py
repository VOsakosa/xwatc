"""
Die große Feste von Grökrakchöl mitsamt umliegender Landschaft und See.
Created on 15.10.2020
"""
from xwatc import nsc
from xwatc import jtg
from xwatc.dorf import ort, Malp, Dorf, Rückkehr
from xwatc.nsc import StoryChar, NSC, Person
from xwatc.system import mint, Mänx, malp, HatMain, Welt, malpw, Fortsetzung
from xwatc.weg import get_eintritt, gebiet, Gebiet, kreuzung, WegAdapter, Eintritt, Gebietsende
from xwatc.effect import Cooldown, NurWenn
__author__ = "jasper"

GENAUER = [
    "Hinter der Festung fangen Felder an.",
    "In vier Richtungen führen Wege weg, nach Norden, Nordosten, Südosten "
    "und nach Westen. Der Weg nach Norden ist aber nur ein Pfad.",
    "In den vier Ecken der Festung stehen Türme, dabei ist der im Südosten "
    "besonders groß.",
    "Um den Kern der Festung gibt es noch eine zweite Mauer. Zwischen den "
    "Mauern sind wohl die Häuser der normalen Bevölkerung."
]

zugang_ost = Eintritt(("jtg:grökrak", "ost"))
zugang_südost = Eintritt(("jtg:grökrak", "südost"))

def pflücken(mänx: Mänx) -> None:
    """Eine Option auf der Streuobstwiese."""
    mänx.erhalte("Aprikose", 14)
    mänx.erhalte("Apfel", 5)
    mänx.erhalte("Zwetschge", 31)
    malp("Niemand hat dich gesehen.")


@gebiet("jtg:grökrak")
def grökrak(mänx: Mänx, gebiet: Gebiet) -> None:
    wiese = kreuzung("Streuobstwiese", immer_fragen=True).add_beschreibung(
        "Du folgst dem Weg. Auf der linken Seite sind Felder.", nur="o").add_beschreibung((
            "Du kommst in eine Streuobstwiese.",
            "Du siehst Äpfel, Zwetschgen und Aprikosen.",
            "Willst du einige pflücken?"
        ))
    wiese.verbinde(WegAdapter(jtg.süd_dorf, "südost", gebiet), "o")
    wiese.add_option("Plücken", "pflücken", NurWenn(Cooldown("jtg:grk:pflücken", 1),
                                                    pflücken))  # type: ignore
    vor_stadt = kreuzung("Vor dem Stadttor").add_beschreibung([
        "Der Weg überquert mit einer Brücke einen Bach. Am Bach stehen Bäume,"
        " die dir die Aussicht auf Grökrakhöl verbargen.",
        "Grökrakhöl, eine große, quadratische Festung, ragt majestätisch vor dir auf."
    ], nur="so").add_beschreibung(
        "Du verlässt die Festung.", nur="Stadttor").add_beschreibung([
            "Vor dir bietet sich ein erfurchterregender Anblick:",
            "In der Mitte einer weiten Ebene ragt eine hohe quadratische "
            "Festung hervor: Grökrakchöl."
        ], nur="no", warten=True).add_beschreibung(
            "Du stehst vor den Toren von Grökrakchöl.")
    vor_stadt.verbinde_mit_weg(wiese, 1 / 24, "so")
    vor_stadt.add_option("Genauer", "genauer", GENAUER)
    vor_stadt - _grökrak(mänx.welt).get_ort("Stadttor")
    biegung = kreuzung("Waldeingang", immer_fragen=False).add_beschreibung(
        "Der Weg führt nach Südwesten aus dem Wald heraus.", nur="o"
    ).add_beschreibung(
        "Der Weg führt in einen Wald hinein.", nur="sw"
    )
    biegung.verbinde(Gebietsende(
        None, gebiet, "ost", "jtg:mitte", "west"), "o")
    vor_stadt.verbinde_mit_weg(biegung, 1 / 24, "no")


def _grökrak(welt: Welt) -> Dorf:
    """"""
    tor = ort("Stadttor", None,
              "Am Stadttor von Grökrakchöl herrscht reger Betrieb.")
    haupt = ort("Hauptplatz", None, "Vor dem Burgfried Grökrakchöls ist ein großer,"
                "geschäftiger Platz. In der Mitte ist ein großer Springbrunnen, "
                "davor eine Statue eines großen Denkers.")

    taverne = ort("Taverne Zum Katzenschweif", None,
                  "Eine lebhafte Taverne voller Katzen",
                  [
                      welt.obj("jtg:gr:özil"),
                      welt.obj("jtg:gr:kloos"),
                      welt.obj("jtg:gr:canna"),
                      welt.obj("jtg:gr:carlo"),
                      welt.obj("jtg:gr:klavier"),
                  ])
    tor - haupt - taverne
    return Dorf.mit_struktur("Grökrakchöl", [tor, haupt, taverne])


özil = StoryChar("jtg:gr:özil", ("Özil", "Çakır", "Kellner"), startinventar={
    "Tablett": 4,
    "Anzug": 1,
    "Tomate": 1,
    "Speisekarte": 1,
    "Gold": 13,
}, vorstellen_fn=["Ein unsicher wirkender junger Kellner."])


def bier(n: NSC, m: Mänx):
    n.sprich("Kommt sofort.")
    n.sprich("Das macht dann 2 Gold.")
    if m.gold > 2:
        m.erhalte("Gold", -2, n)
        m.erhalte("Bier", 1)
    else:
        if n.inventar["Bier"] < 10:
            n.inventar["Bier"] += 1
        m.ausgabe.malp("Du hast nicht genug Geld.")


özil.dialog("bier", "Ein Bier bitte.", bier)
özil.dialog("hallo", "Hallo", "Hallo")
özil.dialog("taverne", "Erzähl mir etwas über die Taverne", [
    "Das ist die Taverne Zum Katzenschweif.",
    "Der ursprüngliche Besitzer war ein großer Fan von Katzen.",
    "Nun sind Katzen das Erkennungsmerkmal unserer Taverne."
])
özil.dialog("ursprünglich", "Ursprünglich?", [
    "Ja, die ursprüngliche Besitzerin Catheryne hat vor 5 Jahren "
    "Grökrakchöl verlassen.",
    "Jetzt führt Frau Kloos den Laden."
], "taverne")

kloos = StoryChar("jtg:gr:kloos", ("Miřam", "Kloos", "Wirtin"), vorstellen_fn=[
    "Eine hochgewachsene Frau steht hinter dem Tresen"
], startinventar={
    "Gold": 124,
    "Schürze": 1,
    "Einfaches Kleid": 2,
    "Socke": 2,
    "Ring": 4,
    "Mugel des Geschmacks": 1,
})

kloos.dialog("hallo", "Hallo", "Bier gibt's beim Kellner")

canna = StoryChar("jtg:gr:canna", ("Canna", "Gill Darß", "Stammkundin"), Person("w"), startinventar={
    "Tarotkarte": 64,
    "Hose": 1,
    "T-Shirt": 1,
    "Gold": 34,
    "Tasche": 1
}, vorstellen_fn=[
    "Canna trinkt Bier.", "Es ist sicherlich nicht das erste."]
)


@canna.kampf
def canna_kampf(canna: NSC, mänx: Mänx) -> Rückkehr | Fortsetzung:
    canna.sprich("Häh?")
    malp("Obwohl sie betrunken ist, schafft sie es, dir auszuweichen.")
    if canna.hat_item("Tarotkarte"):
        canna.sprich("Du hast dich mit der falschen *Hick* angelegt.")
        malp("Sie zieht eine Tarotkarte aus ihrer Tasche.")
        canna.sprich("Ich ziehe: Den Narren!")
        malp("Die Welt vor dir verschwimmt.")
        canna.sprich("Ich ziehe den Zauberer!", warte=True)
        canna.sprich("und den Stern!")
        malp("Die Welt verschwimmt vor dir.")
        return get_eintritt(mänx, "lg:mitte")
    else:
        canna.sprich("Wo sind meine Karten?")
        canna.sprich("Wo sind meine Karten?", wie="wimmernd")
        malp("Canna flieht.")
        canna.tot = True
        return Rückkehr.VERLASSEN


canna.dialog("hallo", "Hallo", ["Hallöchen"], wiederhole=1)
canna.dialog("hallo2", "Hallo?", [
             "Hallöchen, Hallo, Hallöchen! *Hust*"], "hallo")
canna.dialog("zuschauen", "zuschauen", [
    Malp("Canna trinkt ein Bier."), Malp("Dann noch eins."),
    "Was starrst du mich so an?", Malp("Canna schaut wieder weg."),
    "Miřam, noch eins!"])
canna.dialog("betrinken", "Warum betrinkst du dich den ganzen Tag?", [
    "Geht dich das was an?",
    "Bier schmeckt, Bier ist gut, Bier ist toll.",
    "Brauche ich noch einen anderen Grund?",
], "zuschauen")
canna.dialog("gr", "Kannst du mir etwas über Grökrakchöl erzählen?", [
    "Grökrakchöl, ja, das ist eine große Festung hier an der Grenze.",
    "Es gibt gutes Bier, gute Katzen und gute Arbeit.",
    "Nur die Soldaten reden die ganze Zeit von Tauern."
], "hallo")


carlo = StoryChar("jtg:gr:carlo", ("Carlo", "Kater"),
                  vorstellen_fn=(
                      "Carlo ist der größte Kater in der Taverne.",),
                  startinventar={})


carlo.dialog("hallo", "Hallo", ("Miao",))
carlo.dialog("streicheln", "streicheln", [
    Malp("Carlo lässt sich bereitwillig streicheln.")])


@carlo.kampf
def carlo_kampf(n: NSC, m: Mänx):
    malp(f"{n.name} faucht")
    m.sleep(0.2)
    malp("Aber er scheint Gefallen an eurem Testkampf zu finden.")
    m.sleep(0.5)
    malp("Jetzt ist Carlo müde.")


def fisch(n: nsc.NSC, m: Mänx):
    fisch = m.hat_klasse("Fisch")
    assert fisch
    m.erhalte(fisch, -1, n)
    n.add_freundlich(10, 50)


carlo.dialog("fisch", "Fisch geben",
             [Malp("Carlo frisst glücklich den Fisch.")],
             effekt=fisch
             ).wenn(lambda _n, m: bool(m.hat_klasse("Fisch")))


klavier = StoryChar("jtg:gr:klavier", "Klavier",
                    vorstellen_fn=("Ein großes Klavier steht in der Taverne."),)


@klavier.kampf
def klavier_kampf(klavier: NSC, mänx: Mänx) -> None:
    if mänx.hat_item("Axt"):
        klavier.tot = True
        # mänx.context.melde(Ereignis.SACHBESCHÄDIGUNG, [klavier])
        malpw("Du schlägst das Klavier entzwei.")
    elif mänx.hat_item("Schwert"):
        malp("Dein Schwert weigert sich, das Klavier zu beschädigen.")
        malpw("Es ist plötzlich sehr schwer in deiner Hand.")
    else:
        malpw("Du brauchst wohl eine Axt, um das Klavier ernsthaft zu "
              "beschädigen.")


def kann_spielen(n, m):
    return m.hat_fähigkeit("Orgel")


klavier.dialog("ein fröhliches Lied spielen", "froh", [
    Malp("Die Stimmung in der Taverne hellt sich auf.")]).wenn(kann_spielen)
klavier.dialog("den gestiefelten Kater spielen", "kater", [
    Malp("Die Melodie klingt durch die Taverne")]).wenn(kann_spielen)


if __name__ == '__main__':
    import xwatc.anzeige
    xwatc.anzeige.main(zugang_ost)
