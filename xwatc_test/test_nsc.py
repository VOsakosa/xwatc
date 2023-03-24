""""""
from collections.abc import Iterator
from xwatc.serialize import converter
import unittest

from xwatc.dorf import Ort, Dialog
from xwatc.nsc import StoryChar, Person, Rasse, Geschlecht, NSC, CHAR_REGISTER, OldNSC
from xwatc.system import Welt


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


def dlg_fn_für_test() -> Iterator[Dialog]:
    """Ein DLG-Funktion zu Testzwecken. Sie ist hier, damit sie gepickelt werden kann."""
    yield Dialog("hallo", "Hallo", ["Du bist, wer du bist.", "Hallo"])


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
        jonas = StoryChar("test:jonas", "Jonas Berncdo", Person("m", art="Subokianer"),
                          {"Unterhose": 3})
        jonas1 = jonas.zu_nsc()
        jonas1.inventar["Unterhose"] += 1
        pickled = converter.unstructure(jonas1)
        CHAR_REGISTER.clear()
        char2 = StoryChar("test:jonas", "Jonas Berndoc",
                          Person("m", art="Subokianer"), {"Unterhose": 3, "Messer": 1})
        jonas2 = converter.structure(pickled, NSC)
        self.assertIs(jonas2.template, char2)
        self.assertEqual(jonas2.inventar["Unterhose"], 4)

    def test_old_nsc_pickle(self):
        """Test if OldNSC can be pickled."""
        jonas = OldNSC("Jonas Berncdo", "Subokianer",
                       None, None, dlg=dlg_fn_für_test)
        jonas.inventar["Unterhose"] += 2
        pickled = converter.unstructure(jonas)
        jonas2 = converter.structure(pickled, OldNSC)
        self.assertEqual(jonas2.name, "Jonas Berncdo")
        self.assertIs(jonas2._dlg, dlg_fn_für_test)
        

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
