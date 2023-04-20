"""
Created on 25.03.2023
"""
from pathlib import Path
import tempfile
import unittest
from xwatc_test.mock_system import MockSystem
from xwatc.lg.start import waffe_wählen
__author__ = "Jasper Ischebeck"


class TestLG(unittest.TestCase):
    def setUp(self):
        self.system = MockSystem()
        self.mänx = self.system.install()

class TestSpeichernLaden(unittest.TestCase):
    def test_speichern(self) -> None:
        with tempfile.NamedTemporaryFile() as obj:
            MockSystem().install().save(waffe_wählen, Path(obj.name))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
