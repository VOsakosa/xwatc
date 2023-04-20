"""
Tauern, das Land der aufrechten Kühe.
Created on 15.10.2020
"""
from xwatc import weg
from xwatc.jtg import osten, gibon
from xwatc.system import Mänx, malp, Spielende, _, sprich
from xwatc.untersystem.person import Fähigkeit, Geschlecht
from xwatc.weg import gebiet, kreuzung, Wegtyp, Eintritt
from xwatc.nsc import StoryChar, Person, Rasse, NSC, Rückkehr, Sprich, Malp


__author__ = "jasper"
ZOLL_PREIS = 10

KRIEGER_INVENTAR = {
    "Axt": 1,
    "Lederrüstung": 1,
    "Lederhose": 1,
    "Lendenschurz": 1,
    "Leibchen": 1,
    "Armband": 1,
    "Sandalen": 1,
    "Gold": 10,
    "Jubmumin-Premium-Karte": 1,
    "Personalausweis": 1,
}


land_der_kühe = Eintritt("jtg:tauern", "start")


@gebiet("jtg:tauern")
def erzeuge_tauern(mänx: Mänx, gebiet: weg.Gebiet) -> None:
    import xwatc.jtg.gibon as __  # @UnusedImport
    ein_adap = gebiet.ende(land_der_kühe, osten.no_tauern)
    eintritt = kreuzung("eintritt", sw=ein_adap)
    eintritt.add_beschreibung([
        "Der Weg führt weiter am Fluss entlang, das Land wird hügeliger.",
        "Die Vegetation wird spärlicher.",
    ], nur="sw")
    eintritt.add_beschreibung([
        "Der Weg folgt dem Fluss in einen Wald."], nur="no")

    vorbrück = kreuzung("vorbrück")
    vorbrück.verbinde_mit_weg(eintritt, 0.3, "sw", None, Wegtyp.WEG, "Jotungard",
                              "Tauern")
    vorbrück.add_beschreibung([
        "Der Weg überquert den Fluss in einer hölzernen Brücke, "
        "sie ist aber durch ein Zollhaus gesichert.",
        "Ein Trampelpfad führt aber weiter den Fluss entlang."], nur="sw")
    vorbrück.add_beschreibung([
        "Der Weg nach Jotungard folgt dem Fluss auf der rechten Seite.",
        "Die Brücke führt nach Tauern."], außer="sw")
    vorbrück.add_beschreibung(
        "Ein Trampelpfad führt den Fluss entlang nach rechts.", nur="brücke")

    steilwand = kreuzung("steilwand", immer_fragen=True)
    vorbrück.verbinde_mit_weg(
        steilwand, 0.05, "no", None, Wegtyp.TRAMPELPFAD, beschriftung_zurück="Zurück zur Brücke"
    )
    steilwand.add_beschreibung(
        "Du kommst an einen steilen Berg, der in den Fluss "
        "ragt. Ohne Kletterkünste ist hier kein Vorbeikommen.")

    zoll = weg.WegSperre(None, None, zoll_fn, zoll_fn)
    vorbrück.verbinde(zoll, "o", ziel="Über die Brücke")

    hinterbrück = kreuzung("hinterbrück", immer_fragen=True, w=zoll)
    hinterbrück.add_beschreibung("Vor dir liegt nun Tauern.", "w")
    hinterbrück.add_beschreibung("Du kommst an eine Zollbrücke.", "o")

    # Der Wächter ist da, wo der Mänx ist.
    def bewege(ort):
        def inner(m: Mänx):
            m.welt.obj("jtg:tau:wächter").ort = ort
        return inner
    vorbrück.add_effekt(bewege(vorbrück))
    hinterbrück.add_effekt(bewege(hinterbrück))
    osttor = gibon.erzeuge_gibon(mänx, gebiet).get_ort("Westtor")
    hinterbrück.verbinde_mit_weg(
        osttor, 1.5, richtung="o", beschriftung_zurück="Jotungard")
    osttor.bschr("Du erreichst nach Gibon, ein große Stadt direkt an der Grenze zu Jotungard.",
                 nur="w")


def zoll_fn(mänx: Mänx) -> bool:
    """Die Schranke, die prüft, ob der Mensch durch kann."""
    wächter = mänx.welt.obj("jtg:tau:wächter")
    if wächter.tot:
        malp("Das Zollhaus ist leer.")
        return True
    if mänx.welt.ist("jtg:tauern:freier_eintritt"):
        malp("Der Wächter winkt dich durch.")
        return True
    else:
        kosten = (1 + len(mänx.gefährten)) * ZOLL_PREIS
        wächter.sprich(_("Das macht dann {kosten} Gold.").format(kosten=kosten))
        if mänx.ja_nein("Zahlst du das Geld?"):
            mänx.erhalte("Gold", -kosten)
            return True
        else:
            return False


wärter = StoryChar("jtg:tau:wächter", ("Federico", "Pestalozzi", "Zollbeamter"),
                   Person("m", Rasse.Munin), startinventar=KRIEGER_INVENTAR | {"Uniform": 1})


wärter.dialog("hallo", "Hallo", "Muin.")
wärter.dialog("wer", "Wer sind Sie?",
              ["Ich bin Pestalozzi, Zollbeamter, und bewache diese Brücke.",
               "Wenn Sie zahlen, lasse ich Sie gerne 'rüber."])
wärter.dialog("kosten", "Wie viel kostet der Übergang",
              f"Es kostet {ZOLL_PREIS} pro Person.")
wärter.dialog("teuer", "Das ist aber teuer!", [
    "Tut mir leid, das sind die Regeln.",
    "Sie mögen das teuer finden, aber es ist schön einfach.",
    f"Sie wollen nach Tauern, dann zahlen Sie {ZOLL_PREIS} Gold.",
    "Es gibt keine Tageskarte, Jahreskarte, Kinderkarte oder Jubmumin-Premium-Karte.",
    "Dafür brauchen Sie keinen Ausweis, Reisepass, Impfpass, "
    "Magierlizenz, Asylverfahren "
    "oder Flohlosigkeitsnachweis.",
    "Wir machen keine Fieberkontrolle und durchsuchen nicht Ihr Gepäck.",
    "Und das alles sparen Sie sich und wir fordern nur etwas Gold."
], "kosten", wiederhole=1)

wärter.dialog("jubmumin", "Eine Jubmumin-Premium-Karte?", [
    "Nie davon gehört?", "Eine Sonderkarte für junge Mumin.",
    "Sie sind allerdings wohl weder jung noch ein Mumin.",
    "Außerdem sind diese Karten nicht übertragbar."
], "teuer").wenn_mänx(lambda m: m.rasse != Rasse.Munin)

wärter.dialog("ausreise", "Und die Ausreise?", [
    f"Auch {ZOLL_PREIS} Gold.",
    "Dafür gibt es aber keinen guten Grund.",
], "kosten")

wärter.dialog("heim", _("Ich bin ein Munin, ich will heim."), [
    "Warum du auch zahlen musst?",
    "Mal unter uns. Ich finde diese Regeln auch ziemlich dumm.",
    Sprich("Aber ich kann dich nicht einfach so hineinlassen.", wie="nervös")
], "kosten", wiederhole=1).wenn_mänx(lambda m: m.rasse == Rasse.Munin)

wärter.dialog("verführen", "Versuchen, zu verführen", [
    Malp("Du zeigst ihm etwas von deinen Kurven."),
    Sprich("Oh, la, la"),
    Sprich("Äh, das habe ich nie gesagt.", wie="nervös")
], "heim", effekt=lambda n, _m: n.add_freundlich(3, 20), wiederhole=2,
).wenn_mänx(lambda m: m.person.geschlecht == Geschlecht.Weiblich)


def wärter_überzeugen(_nsc: NSC, mänx: Mänx) -> None:
    sprich(_("Du"), _("Geht doch."))
    malp("Du zwinkerst ihm zu und lächelst verführerisch.")
    mänx.welt.setze("jtg:tauern:freier_eintritt")


wärter.dialog("überzeugen", _("Mein Süßer, du wirst doch für mich eine Ausnahme machen."), [
    Malp("Du zwinkerst ihm zu."),
    Sprich("Ja, werte Dame."),
    Sprich("Wenn ich es besorgen kann, wirst du bei mir fortan keinen Zoll mehr zahlen."),
], min_freundlich=6, effekt=wärter_überzeugen)


@wärter.kampf
def zoll_kampf(self: NSC, mänx: Mänx) -> Rückkehr:
    if "gewarnt" in self.variablen:
        kampf_gewarnt(self, mänx)
    malp("Du stürmst auf das Zollhäuschen zu, ", end="")
    waffe = mänx.hat_klasse("Waffe")
    if waffe:
        malp(f"mit dem {waffe} in der Hand.")
    else:
        malp(f"die Fäuste geballt.")
    self.sprich("Halt!")
    malp(f"{self.name} geht aus dem Zollhäuschen, die Axt erhoben.")
    if mänx.ja_nein("Machst du weiter?"):
        if mänx.hat_fähigkeit(Fähigkeit.Ausweichen):
            malp("Du weichst seinem ersten Hieb aus.", warte=True)
            if waffe:
                malp("Dann streckst du ihn nieder.")
                self.tot = True
            else:
                malp("Aber ewig kannst du ihm nicht ausweichen.")
                raise Spielende
        else:
            malp(f"Mit seiner enormen Größe hat {self.name} kein Problem "
                 "deinen Schädel zu spalten, bevor du ihn erreichst.")
            raise Spielende
    else:
        malp("Du erklärst, dass es alles nur ein Scherz war.")
        self.sprich("Ein weiteres Mal wird es nicht geben!")
        self.variablen.add("gewarnt")
    return Rückkehr.VERLASSEN


def kampf_gewarnt(self, _mänx: Mänx) -> None:
    """Der Zöllner ist bereits gewarnt und kennt keine Gnade."""
    malp("Du schickst dich gerade an, die Waffe herauszuholen...")
    self.sprich("He!")
    malp("da steckte dir schon eine Axt im Schädel...")
    malp("Muminen sind nicht zu unterschätzen...")
    raise Spielende


if __name__ == '__main__':
    import xwatc.anzeige
    xwatc.anzeige.main(land_der_kühe)
