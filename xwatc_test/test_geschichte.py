"""
Created on 25.03.2023
"""
import unittest
from xwatc_test.mock_system import MockSystem, ScriptEnde
from xwatc_Hauptgeschichte import himmelsrichtungen
from xwatc.system import Mänx, _OBJEKT_REGISTER
__author__ = "Jasper Ischebeck"


class TestLG(unittest.TestCase):
    def setUp(self):
        self.system = MockSystem()
        self.mänx = self.system.install()

    def test_reach_jtg(self):
        self.system.ein("osten")
        self.system.ein("oase")
        self.system.ein("t2")
        with self.assertRaises(ScriptEnde):
            himmelsrichtungen(self.mänx)
        self.assertIn("Es erwartet dich Vogelgezwitscher.",
                      self.system.ausgaben)

    def test_all_registered(self):
        for name in _OBJEKT_REGISTER:  # @UndefinedVariable
            with self.subTest(id_=name):
                obj = self.mänx.welt.obj(name)
                try:
                    obj.main(self.mänx)
                except ScriptEnde:
                    pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
