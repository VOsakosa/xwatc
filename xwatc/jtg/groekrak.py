"""
Die große Feste von Grökrakchöl mitsamt umliegender Landschaft und See.
Created on 15.10.2020
"""
from xwatc.dorf import Ort, NSC, Malp, Dorf, Dialog
from typing import Iterator
__author__ = "jasper"
from xwatc.system import mint, Mänx, malp, HatMain, register, Welt

GENAUER = [
    "Hinter der Festung fangen Felder an.",
    "In vier Richtungen führen Wege weg, nach Norden, Nordosten, Südosten "
    "und nach Westen. Der Weg nach Norden ist aber nur ein Pfad.",
    "In den vier Ecken der Festung stehen Türme, dabei ist der im Südosten "
    "besonders groß.",
    "Um den Kern der Festung gibt es noch eine zweite Mauer. Zwischen den "
    "Mauern sind wohl die Häuser der normalen Bevölkerung."
]


def zugang_ost(mänx: Mänx):
    """Zugang zu Grökrak aus dem Osten"""
    mint("Der Weg führt nach Südwesten aus dem Wald heraus.")
    if mänx.welt.ist("kennt:grökrakchöl"):
        mint("Vor dir siehst du Grökrakchöl.")
    else:
        malp("Vor dir bietet sich ein erfurchterregender Anblick:")
        mint("In der Mitte einer weiten Ebene ragt eine hohe quadratische "
             "Festung hervor.")
    mänx.genauer(GENAUER)
    grökrak(mänx)


def zugang_südost(mänx: Mänx):
    """Zugang aus Scherenfeld"""
    malp("Du folgst dem Weg. Auf der linken Seite sind Felder.")
    mint("Du kommst in eine Streuobstwiese.")
    malp("Du siehst Äpfel, Zwetschgen und Aprikosen.")
    if mänx.ja_nein("Willst du einige pflücken?"):
        mänx.erhalte("Aprikose", 14)
        mänx.erhalte("Apfel", 5)
        mänx.erhalte("Zwetschge", 31)
        malp("Niemand hat dich gesehen.")
    malp("Der Weg überquert mit einer Brücke einen Bach. Am Bach stehen Bäume,"
         " die "
         "dir die Aussicht auf ", end="")
    if mänx.welt.ist("kennt:grökrakchöl"):
        mint("Grökrakhöl verbargen.")
    else:
        mint("eine große quadratische Festung verbargen.")
    mänx.genauer(GENAUER)
    grökrak(mänx)


def grökrak(mänx: Mänx):
    if mänx.ja_nein("Willst du die Festung betreten?"):
        gkrak = mänx.welt.get_or_else(
            "jgt:dorf:grökrakchöl", erzeuge_grökrak, mänx.welt)
        gkrak.main(mänx)  # TODO Rückgabewert


def erzeuge_grökrak(welt: Welt) -> HatMain:
    """"""
    tor = Ort("Stadttor", None, "Am Stadttor von Grökrakchöl herrscht reger Betrieb.")
    haupt = Ort("Hauptplatz", None, "Vor dem Burgfried Grökrakchöls ist ein großer,"
                "geschäftiger Platz. In der Mitte ist ein großer Springbrunnen, "
                "davor eine Statue eines großen Denkers.")

    taverne = Ort("Taverne Zum Katzenschweif", None,
                  "Eine lebhafte Taverne voller Katzen",
                  [
                      welt.obj("jtg:gr:özil"),
                      welt.obj("jtg:gr:kloos"),
                      welt.obj("jtg:gr:canna"),
                      welt.obj("jtg:gr:carlo")
                  ])
    return Dorf("Grökrakchöl", [tor, haupt, taverne])


@register("jtg:gr:özil")
def özil() -> NSC:
    """Özil ist Kellner in der Taverne"""
    return NSC("Özil Çakır", "Kellner", startinventar={
        "Tablett": 4,
        "Anzug": 1,
        "Tomate": 1,
        "Speisekarte": 1,
        "Gold": 13,
    }, vorstellen=["Ein unsicher wirkender junger Kellner."], dlg=özil_dlg)


def özil_dlg() -> Iterator[Dialog]:

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
    yield Dialog("bier", "Ein Bier bitte.", bier)
    yield Dialog("hallo", "Hallo", "Hallo")
    yield Dialog("taverne", "Erzähl mir etwas über die Taverne", [
        "Das ist die Taverne Zum Katzenschweif.",
        "Der ursprüngliche Besitzer war ein großer Fan von Katzen.",
        "Nun sind Katzen das Erkennungsmerkmal unserer Taverne."
    ])
    yield Dialog("ursprünglich", "Ursprünglich?", [
        "Ja, die ursprüngliche Besitzerin Catheryne hat vor 5 Jahren "
        "Grökrakchöl verlassen.",
        "Jetzt führt Frau Kloos den Laden."
    ])


@register("jtg:gr:kloos")
def kloos() -> NSC:
    """Kloos ist die Besitzerin der Taverne. Sie ist kurz angebunden."""
    return NSC("Miřam Kloos", "Wirtin", vorstellen=[
        "Eine hochgewachsene Frau steht hinter dem Tresen"
    ], startinventar={
        "Gold": 124,
        "Schürze": 1,
        "Einfaches Kleid": 2,
        "Socke": 2,
        "Ring": 4,
        "Mugel des Geschmacks": 1,
    }, dlg=kloos_dlg)


def kloos_dlg() -> Iterator[Dialog]:
    yield Dialog("hallo", "Hallo", "Bier gibt's beim Kellner")


def canna_kampf(canna: NSC, mänx: Mänx):
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
        from xwatc_Hauptgeschichte import himmelsrichtungen
        return himmelsrichtungen
    else:
        canna.sprich("Wo sind meine Karten?")
        canna.sprich("Wo sind meine Karten?", wie="wimmernd")
        malp("Canna flieht.")
        canna.tot = True


@register("jtg:gr:canna")
def canna() -> NSC:
    """Canna sitzt nur in Taverne herum und trinkt."""

    return NSC("Canna Gill Darß", "Stammkundin", canna_kampf, vorstellen=[
        "Canna trinkt Bier.", "Es ist sicherlich nicht das erste."],
        startinventar={
        "Tarotkarte": 64,
        "Hose": 1,
        "T-Shirt": 1,
        "Gold": 34,
        "Tasche": 1
    }, dlg=canna_dlg)


def canna_dlg() -> Iterator[Dialog]:
    yield Dialog("hallo", "Hallo", ["Hallöchen"], wiederhole=1)
    yield Dialog("hallo2", "Hallo?", ["Hallöchen, Hallo, Hallöchen! *Hust*"], "hallo")
    yield Dialog("zuschauen", "zuschauen", [
        Malp("Canna trinkt ein Bier."), Malp("Dann noch eins."),
        "Was starrst du mich so an?", Malp("Canna schaut wieder weg."),
        "Miřam, noch eins!"])
    yield Dialog("betrinken", "Warum betrinkst du dich den ganzen Tag?", [
        "Geht dich das was an?",
        "Bier schmeckt, Bier ist gut, Bier ist toll.",
        "Brauche ich noch einen anderen Grund?",
    ], "zuschauen")
    yield Dialog("gr", "Kannst du mir etwas über Grökrakchöl erzählen?", [
        "Grökrakchöl, ja, das ist eine große Festung hier an der Grenze.",
        "Es gibt gutes Bier, gute Katzen und gute Arbeit.",
        "Nur die Soldaten reden die ganze Zeit von Tauern."
    ], "hallo")


def carlo_kampf(n: NSC, m: Mänx):
    malp(f"{n.name} faucht")
    m.sleep(0.2)
    malp("Aber er scheint Gefallen an eurem Testkampf zu finden.")
    m.sleep(0.5)
    malp("Jetzt ist Carlo müde.")


@register("jtg:gr:carlo")
def carlo() -> NSC:
    return NSC("Carlo", "Kater", carlo_kampf, vorstellen=(
        "Carlo ist der größte Kater in der Taverne.",), dlg=carlo_dlg)


def carlo_dlg():
    yield Dialog("hallo", "Hallo", ("Miao",))
    yield Dialog("streicheln", "streicheln", [
        Malp("Carlo lässt sich bereitwillig streicheln.")])

    def fisch(n: NSC, m: Mänx):
        fisch = m.hat_klasse("Fisch")
        assert fisch
        m.erhalte(fisch, -1, n)
        n.add_freundlich(10, 50)
    yield Dialog("fisch", "Fisch geben",
                 [Malp("Carlo frisst glücklich den Fisch.")],
                 effekt=fisch
                 ).wenn(lambda m, n: bool(m.hat_klasse("Fisch")))

if __name__ == '__main__':
    import xwatc.anzeige
    xwatc.anzeige.main(zugang_ost)
