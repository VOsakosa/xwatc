from time import sleep
from xwatc import haendler
from xwatc import scenario
from xwatc.system import Mänx, minput, ja_nein, Spielende, mint, sprich, kursiv, Karawanenfracht
from xwatc.lg.osten.karawane import Karawane, Angestellte
from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner, Dialog
import random
from xwatc.jtg.tauern import land_der_kühe
from xwatc.jtg import groekrak, see, nord
from xwatc.haendler import Preis
from xwatc.jtg.groekrak import zugang_südost
from xwatc.jtg import eo_nw
import xwatc_Hauptgeschichte


class MinkajaOrekano(Angestellte):
    def __init__(self) -> None:
        super().__init__("Minkaja Orekano", "Magd")
        cls = type(self)
        self.dialog("geige",
                    '"Stimmt es, dass du Geige spielst?"',
                    cls.reden_geige)
        self.dialog("geht", '"Wie geht es dir?"',
                    cls.reden_geht)
        self.dialog("wetter",
                    '"Wie findest du das Wetter heute?"', cls.reden_wetter)

    def kampf(self, mänx: Mänx) -> None:
        cls = type(self)
        self.dialog("bewusstlos",
                    '"bewusstlos schlagen"',
                    cls.kampf_bewusstlos)
        self.dialog("töten", '"töten"',
                    cls.kampf_töten)
        self.dialog("fliehen",
                    '"zurück"',
                    cls.kampf_fliehen)

    def kampf_bewusstlos(self, mänx: Mänx) -> None:
        print("Sie weicht aus.")
        print("Wer hätte gedacht, dass sie so schnell sein konnte?")
        mint("Dann schnellt ihr Messer vor und du verendest elendig röchelnd.")
        raise Spielende

    def kampf_töten(self, mänx: Mänx) -> None:
        if mänx.hat_klasse("Waffe"):
            mint("Du tötest sie.")
            self.tot = True

    def kampf_fliehen(self, mänx: Mänx) -> None:
        mint('"Was ist?"')

    def vorstellen(self, mänx: Mänx) -> None:
        mint('"Tag. Was ist?"')

    def reden_geige(self, mänx: Mänx) -> None:
        mint('"Ja. Warum fragst du?"')

    def reden_geht(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')

    def reden_wetter(self, mänx: Mänx) -> None:  # pylint: disable=unused-argument
        mint('"Schön", sagte sie ohne aufzublicken.')

    def main(self, mänx: Mänx) -> None:
        print('"Tag. Was ist?"')
        super().main(mänx)


class ThonaTantavan(Angestellte):
    def __init__(self) -> None:
        super().__init__("Thona Tantavan", "Magd")
        cls = type(self)
        self.dialog("hallo",
                    '"Hallo, wie heißt du?"',
                    cls.reden_hallo)
        self.dialog("geht", '"Wie geht es dir?"',
                    cls.reden_geht)
        self.dialog("wetter",
                    '"Wie findest du das Wetter heute?"', cls.reden_wetter)

    def kampf(self, mänx: Mänx) -> None:
        cls = type(self)
        self.dialog("bewusstlos",
                    '"bewusstlos schlagen"',
                    cls.kampf_bewusstlos)
        self.dialog("töten", '"töten"',
                    cls.kampf_töten)
        self.dialog("fliehen",
                    '"zurück"', cls.kampf_fliehen)

    def vorstellen(self, mänx: Mänx) -> None:
        mint('"Was ist?"')

    def reden_geige(self, mänx: Mänx) -> None:
        mint('"Ja. Warum fragst du?"')

    def reden_geht(self, mänx: Mänx) -> None:
        print('"Was kümnmert dich das?"')
        if ja_nein(mänx, "Beharrst du auf deine Frage"):
            mint('"Gut und hau jetzt ab!"')

    def reden_wetter(self, mänx: Mänx) -> None:  # pylint: disable=unused-argument
        mint('"Schön", sagte sie ohne aufzublicken.')

    def main(self, mänx: Mänx) -> None:
        print('"Tag. Was ist?"')
        super().main(mänx)
