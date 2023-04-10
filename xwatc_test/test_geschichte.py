"""
Created on 25.03.2023
"""
from pathlib import Path
import tempfile
import unittest
from xwatc_test.mock_system import MockSystem, ScriptEnde
from xwatc.system import _OBJEKT_REGISTER
from xwatc_Hauptgeschichte import waffe_wählen
__author__ = "Jasper Ischebeck"


class TestLG(unittest.TestCase):
    def setUp(self):
        self.system = MockSystem()
        self.mänx = self.system.install()

    @unittest.skip("Takes too long")
    def test_all_registered(self):
        for name in _OBJEKT_REGISTER:  # @UndefinedVariable
            with self.subTest(id_=name):
                obj = self.mänx.welt.obj(name)
                try:
                    obj.main(self.mänx)
                except ScriptEnde:
                    pass

class TestSpeichernLaden(unittest.TestCase):
    def test_speichern(self) -> None:
        with tempfile.NamedTemporaryFile() as obj:
            MockSystem().install().save(waffe_wählen, Path(obj.name))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
