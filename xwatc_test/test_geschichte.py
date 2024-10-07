"""
Created on 25.03.2023
"""
import json
from pathlib import Path
import tempfile
import unittest
from xwatc.lg.süden.süden import rückweg
from xwatc.serialize import structure_punkt, unstructure_punkt
from xwatc.system import Mänx
from xwatc_test.mock_system import MockSystem
from xwatc.lg.start import waffe_wählen
__author__ = "Jasper Ischebeck"


class TestLG(unittest.TestCase):
    def setUp(self):
        self.system = MockSystem()
        self.mänx = self.system.install()


class TestSpeichernLaden(unittest.TestCase):
    def test_speichern(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            MockSystem().install().save(waffe_wählen, Path(temp_dir) / "test")

    def test_serialize_fn(self) -> None:
        data = unstructure_punkt(rückweg)
        print(data)
        self.assertIn("rückweg", json.dumps(data, ensure_ascii=False))
        self.assertIs(structure_punkt(data, Mänx()), rückweg)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
