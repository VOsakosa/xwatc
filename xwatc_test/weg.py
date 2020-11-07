"""
Unittests für xwatc.weg

"""
import unittest
from xwatc.weg import Wegtyp


class TestWeg(unittest.TestCase):

    def testTypFormat(self):
        self.assertEqual(format(Wegtyp.WEG,"111"), "Der Weg")
        self.assertEqual(format(Wegtyp.WEG,"g11"), "Der")
        self.assertEqual(format(Wegtyp.ALTE_STRASSE,"011"), "Eine alte Straße")
        self.assertEqual(format(Wegtyp.VERFALLENER_WEG,"13"), "dem verfallenen Weg")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()