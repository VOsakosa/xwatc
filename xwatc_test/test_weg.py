"""
Unittests für xwatc.weg

"""
import unittest
from xwatc.weg import Wegtyp, GEBIETE, Beschreibung, get_gebiet, Gebiet, Himmelsrichtung
from xwatc.system import Mänx, mint
from xwatc_test.mock_system import MockSystem


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
    
    def test_gitter(self):
        gebiet = Gebiet("Test-Gebiet")
        p1 = gebiet.neuer_punkt((1,1), "oase")
        self.assertIs(gebiet.get_punkt_at(1,1), p1)
        self.assertIs(p1.gebiet, gebiet)
        p2 = gebiet.neuer_punkt((3,1), "karawanenort")
        self.assertIs(p1.nachbarn[Himmelsrichtung.from_kurz("o")].ziel, p2)
        self.assertListEqual(p1.get_nachbarn(), [p2])
        p3 = gebiet.neuer_punkt((2,1), "zwischenpunkt")
        self.assertListEqual(p1.get_nachbarn(), [p3])
        self.assertListEqual(p2.get_nachbarn(), [p3])
        self.assertListEqual(p3.get_nachbarn(), [p1, p2])
        p4 = gebiet.neuer_punkt((3,2), "sandwurmplatz")
        self.assertListEqual(p2.get_nachbarn(), [p3, p4])
        


class TestIntegration(unittest.TestCase):

    def test_all(self):
        """Instantiiere alle Gebiete und prüfe damit, ob alle funktionieren."""
        import xwatc_Hauptgeschichte  # @UnusedImport
        mänx = Mänx()
        for name in GEBIETE:  # @UndefinedVariable
            with self.subTest(name=name):
                get_gebiet(mänx, name)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
