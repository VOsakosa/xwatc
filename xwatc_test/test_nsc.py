""""""
import unittest
from xwatc.nsc import StoryChar, Person, Rasse, Geschlecht, NSC
from xwatc.system import Welt
from xwatc.dorf import Ort


class TestPerson(unittest.TestCase):
    def test_geschlecht(self):
        with self.assertRaises(TypeError):
            Person(True)  # type: ignore
        self.assertEqual(Person("m").geschlecht, Person(
            Geschlecht.Männlich).geschlecht)
        self.assertEqual(Person("w").geschlecht, Person(
            Geschlecht.Weiblich).geschlecht)
        self.assertNotEqual(Person("m").geschlecht, Geschlecht.Weiblich)
        with self.assertRaises(ValueError):
            Person("f")  # type: ignore


class TestNSC(unittest.TestCase):

    def test_template_init(self):
        # Without registration
        jonas = StoryChar(None, "Jonas Berncod", Person("m"), {"Unterhose": 3})
        self.assertEqual(jonas.id_, None)
        self.assertEqual(jonas.name, "Jonas Berncod")
        self.assertEqual(jonas.person.rasse, Rasse.Mensch)
        self.assertDictEqual(jonas.startinventar, {"Unterhose": 3})
        # With registration
        toro = StoryChar("jtg:toro", "Toro Berncod",
                         Person("m"), {"Klavier": 1})
        self.assertEqual(toro.id_, "jtg:toro")

        # Mit Ort
        welt = Welt("Winkel")
        toro_nsc = welt.obj("jtg:toro")
        self.assertIs(toro_nsc.template, toro)

    def test_template_pickle(self):
        """Test if the template can be pickled from its ID alone and then updated."""

    def test_old_nsc_pickle(self):
        """Test if OldNSC can be pickled."""

    def test_ort(self):
        """Test if the Ort attribute adds the NSC to the Ort's menschen attribute"""
        ort = Ort("Geheim", dorf=None)
        # On init
        juicy = NSC(StoryChar(None, "Juicy", Person("w"), {}), ort=ort)
        self.assertIs(ort, juicy.ort)
        self.assertIn(juicy, ort.menschen)
        # On set
        ort2 = Ort("Publik", dorf=None)
        juicy.ort = ort2
        self.assertIs(juicy.ort, ort2)
        self.assertIn(juicy, ort2.menschen)
        self.assertNotIn(juicy, ort.menschen)
        # On unset
        juicy.ort = None
        self.assertIsNone(juicy.ort)
        self.assertNotIn(juicy, ort2.menschen)
        # On set from None
        juicy.ort = ort
        # And done twice
        juicy.ort = ort
        self.assertIs(ort, juicy.ort)
        self.assertIn(juicy, ort.menschen)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
