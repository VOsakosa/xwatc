"""
Unittests für xwatc.weg

"""
import unittest
from xwatc.weg import Wegtyp, GEBIETE, Beschreibung, get_gebiet, Gebiet, Himmelsrichtung, Weg
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
        self.assertEqual(gebiet.größe, (0,0))
        p1 = gebiet.neuer_punkt((1,1), "oase")
        self.assertEqual(gebiet.größe, (2,2))
        self.assertIs(gebiet.get_punkt_at(1,1), p1)
        self.assertIs(p1._gebiet, gebiet)
        with self.assertRaises(ValueError):
            gebiet.neuer_punkt((1,1), "oase_kopie")
        p2 = gebiet.neuer_punkt((3,1), "karawanenort")
        self.assertEqual(gebiet.größe, (4,2))
        richtung = p1.nachbarn[Himmelsrichtung.from_kurz("o")]
        assert richtung
        self.assertIsInstance(richtung.ziel, Weg)
        self.assertIn(p2, richtung.ziel.get_nachbarn())
        def get_nachbarn2(pt) -> set:
            ans = set()
            for nb in pt.get_nachbarn():
                self.assertIsInstance(nb, Weg)
                if nb.p1 == pt:
                    ans.add(nb.p2.name)
                else:
                    ans.add(nb.p1.name)
            return ans
        self.assertSetEqual(get_nachbarn2(p1), {p2.name})
        p3 = gebiet.neuer_punkt((2,1), "zwischenpunkt")
        self.assertSetEqual(get_nachbarn2(p1), {p3.name})
        self.assertSetEqual(get_nachbarn2(p2), {p3.name})
        self.assertSetEqual(get_nachbarn2(p3), {p1.name, p2.name})
        p4 = gebiet.neuer_punkt((3,2), "sandwurmplatz")
        self.assertSetEqual(get_nachbarn2(p2), {p3.name, p4.name})
        self.assertEqual(gebiet.größe, (4,3))
        for row in gebiet._punkte:
            self.assertEqual(len(row), 3)


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
