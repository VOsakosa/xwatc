""""""
from collections.abc import Iterator
from xwatc.serialize import converter
import unittest
from unittest.mock import patch

from xwatc.dorf import Ort, Dialog, Zeitpunkt
from xwatc import nsc
from xwatc.nsc import StoryChar, Person, Rasse, Geschlecht, NSC, OldNSC, bezeichnung,  Bezeichnung
from xwatc.system import Welt
from xwatc.haendler import mache_händler
from xwatc_test.mock_system import MockSystem
from xwatc import system


def slots_var(obj: object) -> dict:
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return {s: getattr(obj, s, None) for s in getattr(obj, '__slots__')}


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

    def test_zu_bezeichnung(self):
        self.assertEqual(bezeichnung(Bezeichnung("a", "b", "c")),
                         Bezeichnung("a", "b", "c"))
        self.assertEqual(bezeichnung("A"), Bezeichnung("A", "", "A"))
        self.assertEqual(bezeichnung(("A", "B")), Bezeichnung("A", "B", "A"))
        self.assertEqual(bezeichnung(("Lina", "Vollmayr", "Wirtin")),
                         Bezeichnung("Lina Vollmayr", "Wirtin", "Lina"))


def dlg_fn_für_test() -> Iterator[Dialog]:
    """Ein DLG-Funktion zu Testzwecken. Sie ist hier, damit sie gepickelt werden kann."""
    yield Dialog("hallo", "Hallo", ["Du bist, wer du bist.", "Hallo"])


class TestNSC(unittest.TestCase):

    def test_template_init(self):
        # Without registration
        jonas = StoryChar(None, "Jonas Berncod", Person("m"), {"Unterhose": 3})
        self.assertEqual(jonas.id_, None)
        self.assertEqual(jonas.bezeichnung.name, "Jonas Berncod")
        assert jonas.person
        self.assertEqual(jonas.person.rasse, Rasse.Mensch)
        self.assertDictEqual(jonas.startinventar, {"Unterhose": 3})
        # With registration
        toro = StoryChar("jtg:toro", ("Toro Berncod", "Pianist"),
                         Person("m"), {"Klavier": 1})
        self.assertEqual(toro.id_, "jtg:toro")

        welt = Welt("Winkel")
        toro_nsc = welt.obj("jtg:toro")
        self.assertIs(toro_nsc.template, toro)
        toro_nsc2 = welt.obj("jtg:toro")
        self.assertIs(toro_nsc, toro_nsc2)
        self.assertEqual(toro_nsc.name, "Toro Berncod")
        self.assertEqual(toro_nsc.art, "Pianist")

    def test_dialog_fns(self):
        jon = StoryChar(None, "Jon", Person("m"))
        jon.dialog("hallo", "Hallo", "Hallo dir auch")

        def und_dlg(nsc, mänx):
            nsc.sprich(mänx.minput("Was sagst du Jon?"))
        jon.dialog_deco("und", "Und was ist?", "hallo")(und_dlg)

        self.assertEqual(slots_var(jon.dialoge[0]), slots_var(Dialog(
            "hallo", "Hallo", "Hallo dir auch")))
        self.assertEqual(slots_var(jon.dialoge[1]), slots_var(Dialog(
            "und", "Und was ist?", und_dlg, "hallo")))
        
        jon.vorstellen("Jon ist dumm")
        self.assertEqual(jon.vorstellen_fn, "Jon ist dumm")
        
        jon.kampf(und_dlg)
        self.assertEqual(slots_var(jon.dialoge[2]), slots_var(Dialog(
            "k", "Angreifen", und_dlg, zeitpunkt=Zeitpunkt.Option)))

    @patch("xwatc.nsc.CHAR_REGISTER", {})
    def test_template_pickle(self):
        """Test if the template can be pickled from its ID alone and then updated."""
        jonas = StoryChar("test:jonas", ("Jonas Berndoc", "Subokianer"), Person("m"),
                          {"Unterhose": 3})
        jonas1 = jonas.zu_nsc()
        jonas1.inventar["Unterhose"] += 1
        pickled = converter.unstructure(jonas1)
        nsc.CHAR_REGISTER.clear()
        char2 = StoryChar("test:jonas", ("Jonas Berndoc", "Subokianer"),
                          Person("m"), {"Unterhose": 3, "Messer": 1})
        jonas2 = converter.structure(pickled, NSC)
        self.assertIs(jonas2.template, char2)
        self.assertEqual(jonas2.inventar["Unterhose"], 4)

    @unittest.skip("Old geht eh nicht")
    def test_old_nsc_pickle(self):
        """Test if OldNSC can be pickled."""
        jonas = OldNSC("Jonas Berncdo", "Subokianer",
                       None, dlg=dlg_fn_für_test)
        jonas.inventar["Unterhose"] += 2
        pickled = converter.unstructure(jonas)
        jonas2 = converter.structure(pickled, OldNSC)
        self.assertEqual(jonas2.name, "Jonas Berncdo")
        self.assertIs(jonas2._dlg, dlg_fn_für_test)

    def test_ort(self):
        """Test if the Ort attribute adds the NSC to the Ort's menschen attribute"""
        ort = Ort("Geheim", dorf=None)
        # On init
        juicy = NSC(StoryChar(None, "Juicy", Person("w"), {}),
                    bezeichnung("Juicy"), ort=ort)
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
    
    def test_vorstellen(self):
        """Test the vorstellen function."""


class TestHändler(unittest.TestCase):
    def test_kaufen(self):
        hdl = StoryChar(None, ("Bob", "Händler"))
        mache_händler(hdl, verkauft={}, kauft=[
                      "Kleidung"], gold=100, aufpreis=2)
        hdl_min = hdl.zu_nsc()
        self.assertEqual(hdl_min.gold, 100)
        sys = MockSystem()
        mx = sys.install()
        gold_start = mx.gold
        sys.ein("h")
        sys.ein("v Mantel")
        sys.ein("z")
        sys.ein("f")
        try:
            hdl_min.main(mx)
        except:
            print(*sys.ausgaben, sep="\n")
            raise
        self.assertTrue(hdl_min.inventar["Mantel"])
        self.assertFalse(mx.inventar["Mantel"])
        gold_mantel = system.ALLGEMEINE_PREISE["Mantel"] * 2
        self.assertEqual(hdl_min.gold, 100 - gold_mantel)
        self.assertEqual(mx.gold - gold_start, gold_mantel)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
