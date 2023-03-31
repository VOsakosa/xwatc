"""
Tauern, das Land der aufrechten Kühe.
Created on 15.10.2020
"""
from xwatc import weg
from xwatc.dorf import NSC
__author__ = "jasper"
from xwatc.system import Mänx, register, malp, Spielende, Fortsetzung
from xwatc.weg import gebiet, WegAdapter, kreuzung, Wegtyp

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


def land_der_kühe(mänx: Mänx) -> Fortsetzung:
    return weg.wegsystem(mänx, "jtg:tauern", return_fn=True)


def rückweg(mänx: Mänx):
    """Gehe aus Tauern wieder zurück."""
    import xwatc.jtg
    xwatc.jtg.tauern_ww_no(mänx)


@gebiet("jtg:tauern")
def erzeuge_tauern(mänx: Mänx, gebiet: weg.Gebiet) -> None:
    import xwatc.jtg.gibon as __  # @UnusedImport
    ein_adap = WegAdapter(None, rückweg, "start", gebiet)
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
        steilwand, 0.05, "no", None, Wegtyp.TRAMPELPFAD, beschriftung_zurück="Brücke"
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
    hinterbrück.verbinde_mit_weg(
        mänx.welt.obj("jtg:tau:gibon").get_ort("Osttor"),
        1.5,
        richtung="o",
        beschriftung_zurück="Jotungard")


def zoll_fn(mänx: Mänx):
    wächter = mänx.welt.obj("jtg:tau:wächter")
    if wächter.tot:
        mänx.ausgabe.malp("Das Zollhaus ist leer.")
        return True
    kosten = (1 + len(mänx.gefährten)) * ZOLL_PREIS
    wächter.sprich(f"Das macht dann {kosten} Gold.")
    if mänx.ja_nein("Zahlst du das Geld?"):
        mänx.erhalte("Gold", -kosten)
        return True
    else:
        return False


@register("jtg:tau:wächter")
class Zollwärter(NSC):
    """Der Zollwärter bewacht die Brücke."""

    def __init__(self):
        super().__init__("Federico Pestalozzi", "Zollbeamter",
                         startinventar=KRIEGER_INVENTAR)
        self.gewarnt = False
        self.inventar["Uniform"] += 1
        self.rasse = "Mumin"
        self.dialog("hallo", "Hallo", "Muin.")
        self.dialog("wer", "Wer sind Sie?",
                    ["Ich bin Pestalozzi, Zollbeamter, und bewache diese Brücke.",
                     "Wenn Sie zahlen, lasse ich Sie gerne 'rüber."])
        self.dialog("kosten", "Wie viel kostet der Übergang",
                    f"Es kostet {ZOLL_PREIS} pro Person.")
        self.dialog("teuer", "Das ist aber teuer!", [
            "Tut mir leid, das sind die Regeln.",
            "Sie mögen das teuer finden, aber es ist schön einfach.",
            f"Sie wollen nach Tauern, dann zahlen Sie {ZOLL_PREIS} Gold.",
            "Es gibt keine Tageskarte, Jahreskarte, Kinderkarte oder Jubmumin-Premium-Karte.",
            "Dafür brauchen Sie keinen Ausweis, Reisepass, Impfpass, "
            "Magierlizenz, Asylverfahren "
            "oder Flohlosigkeitsnachweis.",
            "Wir machen keine Fieberkontrolle und durchsuchen nicht Ihr Gepäck.",
            "Und das alles sparen Sie sich und wir fordern nur etwas Gold."
        ], "kosten")

        self.dialog("jubmumin", "Eine Jubmumin-Premium-Karte?", [
            "Nie davon gehört?", "Eine Sonderkarte für junge Mumin.",
            "Sie sind allerdings wohl weder jung noch ein Mumin.",
            "Außerdem sind diese Karten nicht übertragbar."
        ], "teuer")

        self.dialog("ausreise", "Und die Ausreise?", [
            f"Auch {ZOLL_PREIS} Gold.",
            "Dafür gibt es aber keinen guten Grund.",
        ], "kosten")

    def kampf(self, mänx: Mänx) -> None:
        if self.gewarnt:
            return self.kampf_gewarnt(mänx)
        malp("Du stürmst auf das Zollhäuschen zu, ", end="")
        waffe = mänx.hat_klasse("Waffe")
        if waffe:
            malp(f"mit dem {waffe} in der Hand.")
        else:
            malp(f"die Fäuste geballt.")
        self.sprich("Halt!")
        malp(f"{self.name} geht aus dem Zollhäuschen, die Axt erhoben.")
        if mänx.ja_nein("Machst du weiter?"):
            if mänx.hat_fähigkeit("Ausweichen"):
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
            self.gewarnt = True
    
    def kampf_gewarnt(self, mänx: Mänx) -> None:
        """Der Zöllner ist bereits gewarnt und kennt keine Gnade."""
        malp("Du schickst dich gerade an, die Waffe herauszuholen...")
        self.sprich("He!")
        malp("da steckte dir schon eine Axt im Schädel...")
        malp("Muminen sind nicht zu unterschätzen...")
        raise Spielende

if __name__ == '__main__':
    import xwatc.anzeige
    xwatc.anzeige.main(land_der_kühe)
