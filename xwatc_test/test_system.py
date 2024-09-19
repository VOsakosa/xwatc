from typing import TypeVar, cast
import unittest

from xwatc.system import Bekleidetheit, Mänx

T = TypeVar("T")


class TestInventar(unittest.TestCase):
    """Testet die Inventar-Funktionen."""

    def assert_(self, item: None | T) -> T:
        self.assertIsNotNone(item)
        return cast(T, item)

    def test_auto_ausrüsten(self) -> None:
        mänx = Mänx(inventar={"Schwert": 1})
        self.assertTrue(mänx.hat_item("Schwert"))
        self.assertTrue(mänx.ist_ausgerüstet("Schwert"))
        self.assertEqual(self.assert_(mänx.get_waffe()).name, "Schwert")

    def test_get_waffe(self) -> None:
        self.assertEqual(self.assert_(Mänx(inventar={
            "Schwert": 1
        }).get_waffe()).name, "Schwert")
        self.assertEqual(self.assert_(Mänx(inventar={
            "Schwert": 1,
            "Schild": 1,
        }).get_waffe()).name, "Schwert")
        self.assertEqual(self.assert_(Mänx(inventar={
            "Axt": 1,
            "Schild": 1,
        }).get_waffe()).name, "Axt")
        self.assertIsNone(Mänx(inventar={
            "Turnschuh": 2,
        }).get_waffe())

    def test_waffen_ausrüsten(self) -> None:
        mänx = Mänx()
        mänx.erhalte("Schwert")
        self.assertFalse(mänx.ist_ausgerüstet("Schwert"))
        mänx.ausrüsten("Schwert")
        self.assertTrue(mänx.ist_ausgerüstet("Schwert"))
        mänx.erhalte("Schild")
        mänx.ausrüsten("Schild")
        self.assertTrue(mänx.ist_ausgerüstet("Schwert"))
        self.assertTrue(mänx.ist_ausgerüstet("Schild"))
        mänx.erhalte("Schwert", -1)
        self.assertFalse(mänx.ist_ausgerüstet("Schwert"))
        mänx.erhalte("mächtige Axt")
        mänx.ausrüsten("mächtige Axt")
        self.assertFalse(mänx.ist_ausgerüstet("Schild"))
        self.assertTrue(mänx.ist_ausgerüstet("mächtige Axt"))
        mänx.ablegen("mächtige Axt")
        self.assertFalse(mänx.ist_ausgerüstet("mächtige Axt"))

    def test_bekleidet(self) -> None:
        mänx = Mänx()
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.BEKLEIDET)
        mänx = Mänx(inventar={"Schwert": 1})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.NACKT)
