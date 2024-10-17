"""
Unittests für xwatc.weg

"""
import unittest
from unittest.mock import Mock, create_autospec, patch

from pytest import fixture

from xwatc.nsc import StoryChar
from xwatc.system import MissingIDError, Mänx, malp, mint
from xwatc.untersystem.attacken import (Fertigkeit, Kampfwerte, Resistenzen, Schadenstyp)
from xwatc.weg import (GEBIETE, _Strecke, Beschreibung, Eintritt, Gebiet,
                       Himmelsrichtung, Weg, WegAdapter, WegEnde, Wegpunkt, Wegtyp)
from xwatc.weg import finde_punkt as finde_kreuzung
from xwatc.weg import get_gebiet, kreuzung, wegsystem
from xwatc.weg._kreuzung import Wegkreuzung
from xwatc.weg.begegnung import (Begegnungsausgang, Begegnungsliste, Monstergebiet)
from xwatc_test.mock_system import MockSystem, ScriptEnde, UnpassendeEingabe


class TestWeg(unittest.TestCase):

    def testTypFormat(self):
        self.assertEqual(format(Wegtyp.WEG, "111"), "Der Weg")
        self.assertEqual(format(Wegtyp.WEG, "g11"), "Der")
        self.assertEqual(format(Wegtyp.ALTE_STRASSE, "011"),
                         "Eine alte Straße")
        self.assertEqual(format(Wegtyp.VERFALLENER_WEG, "13"),
                         "dem verfallenen Weg")

    def test_beschreibung(self):
        system = MockSystem()
        mänx = system.install()

        a = Beschreibung("Nur der Text")
        a.beschreibe(mänx, von=None)
        self.assertListEqual(system.pop_ausgaben(), ["Nur der Text"])

        b = Beschreibung(["Mehr", "Text"], nur=(None,))
        b.beschreibe(mänx, von=None)
        self.assertListEqual(system.pop_ausgaben(), ["Mehr", "Text"])
        b.beschreibe(mänx, von="hinten")
        self.assertListEqual(system.pop_ausgaben(), [])

        c = Beschreibung((lambda _m: mint("Hallo")), außer=("light", "heavy"))
        c.beschreibe(mänx, von=None)
        self.assertListEqual(system.pop_ausgaben(), ["Hallo"])
        c.beschreibe(mänx, von="middle")
        self.assertListEqual(system.pop_ausgaben(), ["Hallo"])
        c.beschreibe(mänx, "light")
        self.assertListEqual(system.pop_ausgaben(), [])

        with self.assertRaises(ValueError):
            Beschreibung("Nicht", nur="Ja", außer="Nein")

        d = Beschreibung("Nur der Text", außer="Nein")
        d.beschreibe(mänx, von=None)
        self.assertListEqual(system.pop_ausgaben(), ["Nur der Text"])
        d.beschreibe(mänx, von="Nein")
        self.assertListEqual(system.pop_ausgaben(), [])

    def test_beschreibe(self) -> None:
        system = MockSystem()
        mänx = system.install()

        kr = kreuzung("test")
        kr.add_beschreibung(["Da"], nur=(None,))
        kr.add_beschreibung(["An"], außer=(None,))
        kr.beschreibe(mänx, ri_name=None)
        self.assertListEqual(system.pop_ausgaben(), ["Da"])
        kr.beschreibe(mänx, ri_name="None")
        self.assertListEqual(system.pop_ausgaben(), ["An"])

    def test_gitter(self) -> None:
        gebiet = Gebiet("Test-Gebiet")
        self.assertEqual(gebiet.größe, (0, 0))
        p1 = gebiet.neuer_punkt((1, 1), "oase")
        self.assertEqual(gebiet.größe, (2, 2))
        self.assertIs(gebiet.get_punkt_at(1, 1), p1)
        self.assertIs(p1._gebiet, gebiet)
        with self.assertRaises(ValueError):
            gebiet.neuer_punkt((1, 1), "oase_kopie")
        p2 = gebiet.neuer_punkt((3, 1), "karawanenort")
        self.assertEqual(gebiet.größe, (4, 2))
        richtung = p1.nachbarn[Himmelsrichtung.from_kurz("o")]
        assert richtung
        self.assertIsInstance(richtung, Weg)
        self.assertIn(p2, richtung.get_nachbarn())

        def get_nachbarn2(pt: Wegpunkt) -> set:
            ans = set()
            for nb in pt.get_nachbarn():
                assert isinstance(nb, Weg)
                if nb.start == pt:
                    assert isinstance(nb.ende, Wegkreuzung)
                    ans.add(nb.ende.name)
                else:
                    assert isinstance(nb.start, Wegkreuzung)
                    ans.add(nb.start.name)
            return ans

        self.assertSetEqual(get_nachbarn2(p1), {p2.name})
        p3 = gebiet.neuer_punkt((2, 1), "zwischenpunkt")
        self.assertSetEqual(get_nachbarn2(p1), {p3.name})
        self.assertSetEqual(get_nachbarn2(p2), {p3.name})
        self.assertSetEqual(get_nachbarn2(p3), {p1.name, p2.name})
        p4 = gebiet.neuer_punkt((3, 2), "sandwurmplatz")
        self.assertSetEqual(get_nachbarn2(p2), {p3.name, p4.name})
        self.assertEqual(gebiet.größe, (4, 3))
        for row in gebiet._punkte:
            self.assertEqual(len(row), 3)

    def test_option(self) -> None:
        kr = kreuzung("startpunkt", immer_fragen=True).add_beschreibung(
            "Startpunkt")
        ende = Mock(spec=[])

        def effekt(_mx: Mänx) -> WegEnde:
            malp("Effekt eingetreten")
            return WegEnde(ende)

        kr.add_option("Test-Option[test]", "test_opt", effekt)
        sys = MockSystem()
        sys.ein("test")
        ans = wegsystem(sys.install(), kr, return_fn=True)
        ende.assert_not_called()
        self.assertIs(ans, ende)
        self.assertListEqual(["Startpunkt", "Welchen Weg nimmst du?", "Effekt eingetreten", ""],
                             sys.pop_ausgaben())

        kr.add_option("Sprach-Option[sprach]", "test_sprach", "Hallo")
        sys.ein("sprach")
        with self.assertRaises(ScriptEnde):
            wegsystem(sys.install(), kr, return_fn=True)
        self.assertListEqual(["Startpunkt", "Welchen Weg nimmst du?", "Hallo", "",
                              "Startpunkt", "Welchen Weg nimmst du?"
                              ], sys.pop_ausgaben())

    def test_kreuzung_ausgang(self) -> None:
        kr1 = kreuzung("1", immer_fragen=True)
        kr1.bschr("In Kreuzung 1")
        kr2 = kreuzung("2", immer_fragen=True)
        kr2.bschr("In Kreuzung 2")
        # Normale -- Verbindung
        kr1.ausgang("B", "KR2") - kr2.ausgang("A", "KR1")
        self.assertListEqual(kr1.get_nachbarn(), [kr2])
        self.assertDictEqual(kr2.nachbarn, {"A": kr1})
        self.assertIs(kr2, MockSystem().test_mänx_fn(self, kr1.main, ["kr2"], [
            "In Kreuzung 1", "Welchen Weg nimmst du?"]))

        # Einseitige Verbindung
        kr3 = kreuzung("3", immer_fragen=True).bschr("In Kreuzung 3")
        kr1.ausgang("C", "KR3") < kr3.ausgang("A", "KR1")  # @NoEffect
        with self.assertRaises(UnpassendeEingabe):
            MockSystem().test_mänx_fn(self, kr1.main, ["kr3"], [])
        self.assertIs(kr1, MockSystem().test_mänx_fn(self, kr3.main, ["kr1"], [
            "In Kreuzung 3", "Welchen Weg nimmst du?"]))

    @patch("xwatc.weg.get_gebiet")
    def test_finde_kreuzung(self, get_gebiet) -> None:
        m = MockSystem().install()
        g = Gebiet("test")
        get_gebiet.return_value = g
        h = g.neuer_punkt((0, 0), "hallo")
        h.verbinde(g.ende(Eintritt("test", "hallo"), lambda _m: h), "w")
        self.assertIs(finde_kreuzung(m, "test", "hallo"), h)
        get_gebiet.assert_called_with(m, "test")
        with self.assertRaises(MissingIDError):
            print(finde_kreuzung(m, "test", "nein"))

    def test_begegnungsliste(self) -> None:
        liste = Begegnungsliste("test:wiese")

        @liste.add_begegnung
        def blumen(mänx: Mänx):
            malp("Du findest Sonnenblumen")
            mänx.erhalte("Sonnenblume")

        liste.add_monster(StoryChar("test:büffel", "Büffel", kampfwerte=Kampfwerte(
            max_lp=150, resistenzen=Resistenzen.aus_str("0,0,20,0,-10,10,20,0"),
            fertigkeiten=[Fertigkeit("Ansturm", "ansturm", 20, Schadenstyp.aus_str("klinge"))],
            nutze_std_fertigkeiten=False,
        ), vorstellen_fn=["Ein großer, wütender Büffel hat dich entdeckt."]))


def test_kachel_verlassen(system: MockSystem, mänx: Mänx, monstergebiet: Monstergebiet) -> None:

    end_mock = Mock()
    start_mock = Mock()
    end = WegAdapter(end_mock)
    start = WegAdapter(start_mock)
    kachel = kreuzung("test:mitte", monster=monstergebiet, süden=end, norden=start, tiefe=2,
                      immer_fragen=True)
    kachel.add_beschreibung("Du bist in der Mitte des Tests", nur=(None,))
    kachel.add_beschreibung("Du erreichst die Mitte des Tests", außer=(None,))

    system.ein("süden")
    system.ein("w")
    system.ein("w")
    weiter = kachel.main(mänx, von=start)
    system.aus("Du erreichst die Mitte des Tests")
    system.aus("Welchen Weg nimmst du?")
    system.aus("Durchgang 1")
    system.aus("Du bist in der Mitte des Tests")
    system.aus("Durchgang 2")
    assert monstergebiet.nächste_begegnung.call_count == 2  # type: ignore
    assert weiter is end
    start_mock.assert_not_called()
    end_mock.assert_not_called()
    monstergebiet.betrete.assert_called_once()  # type: ignore


@fixture
def monstergebiet() -> Monstergebiet:
    gebiet_instance = Monstergebiet(begegnungen=Begegnungsliste("leer"), monsterspiegel=10)
    gebiet = create_autospec(gebiet_instance)
    i = 0

    def do(m: Mänx):
        nonlocal i
        i += 1
        malp(f"Durchgang {i}")
        return Begegnungsausgang(None)

    gebiet.nächste_begegnung.side_effect = do
    return gebiet


@fixture
def start_kreuzung():
    return kreuzung("start", immer_fragen=True)


@fixture
def end_kreuzung():
    return kreuzung("ende", immer_fragen=True)


@fixture
def testweg(start_kreuzung: Wegkreuzung, end_kreuzung: Wegkreuzung, monstergebiet: Monstergebiet):
    weg = Weg(4, monster=monstergebiet)
    start_kreuzung.ausgang("weiter", "Weiter") - weg - end_kreuzung.ausgang("zurück", "Zurück")
    return weg


def test_weg_geradeaus(mänx: Mänx, system: MockSystem, monstergebiet: Monstergebiet,
                       start_kreuzung: Wegkreuzung, end_kreuzung: Wegkreuzung, testweg: Weg) -> None:
    system.ein("w")
    system.ein("w")
    system.ein("w")
    system.ein("w")
    assert end_kreuzung == testweg.main(mänx, von=start_kreuzung)
    system.aus("Durchgang 1")
    system.aus(Weg.DEFAULT_FRAGE)
    system.aus("Durchgang 2")
    system.aus(Weg.DEFAULT_FRAGE)
    system.aus("Durchgang 3")
    system.aus(Weg.DEFAULT_FRAGE)
    system.aus("Durchgang 4")
    assert mänx.welt.uhrzeit() == (10, 0)


def test_weg_fliehen(system: MockSystem, start_kreuzung: Wegkreuzung, testweg: Weg) -> None:
    system.ein("w")
    system.ein("f")
    assert start_kreuzung == testweg.main(system.install(), von=start_kreuzung)
    system.aus("Durchgang 1")
    system.aus(Weg.DEFAULT_FRAGE)
    system.aus("Durchgang 2")


class TestIntegration(unittest.TestCase):

    def test_all(self):
        """Instantiiere alle Gebiete und prüfe damit, ob alle funktionieren."""
        import xwatc.lg.start  # @UnusedImport
        mänx = Mänx()
        for name in GEBIETE:  # @UndefinedVariable
            with self.subTest(name=name):
                get_gebiet(mänx, name)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
