"""
Unittests für xwatc.weg

"""
import unittest
from xwatc.weg import Wegtyp, GEBIETE
from xwatc.system import Mänx


class TestWeg(unittest.TestCase):

    def testTypFormat(self):
        self.assertEqual(format(Wegtyp.WEG, "111"), "Der Weg")
        self.assertEqual(format(Wegtyp.WEG, "g11"), "Der")
        self.assertEqual(format(Wegtyp.ALTE_STRASSE, "011"),
                         "Eine alte Straße")
        self.assertEqual(format(Wegtyp.VERFALLENER_WEG, "13"),
                         "dem verfallenen Weg")


class TestIntegration(unittest.TestCase):

    def test_all(self):
        """Instantiiere alle Gebiete und prüfe damit, ob alle funktionieren."""
        import xwatc_Hauptgeschichte  # @UnusedImport
        mänx = Mänx()
        for name, gebiet in GEBIETE.items():  # @UndefinedVariable
            with self.subTest(name=name):
                gebiet(mänx)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
