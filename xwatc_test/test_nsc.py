""""""
import unittest
from xwatc.nsc import StoryChar, Person, Rasse
from xwatc.system import Welt


class TestNSC(unittest.TestCase):

    def test_template_init(self):
        # Without registration
        jonas = StoryChar(None, "Jonas Berncod", Person("m"), {"Unterhose": 3})
        self.assertEqual(jonas.id_, None)
        self.assertEqual(jonas.name, "Jonas Berncod")
        self.assertEqual(jonas.person.rasse, Rasse.Mensch)
        self.assertDictEqual(jonas.startinventar, {"Unterhose": 3})
        # With registration
        toro = StoryChar("jtg:toro", "Toro Berncod", Person("m"), {"Klavier": 1})
        self.assertEqual(toro.id_, "jtg:toro")
        
        # Mit Ort
        welt = Welt("Winkel")
        toro_nsc = welt.obj("jtg:toro")
        self.assertIs(toro_nsc.template, toro)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
