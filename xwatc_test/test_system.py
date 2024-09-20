from typing import TypeVar, cast
import unittest

from xwatc.system import Bekleidetheit, Mänx, get_item

T = TypeVar("T")


class TestItems(unittest.TestCase):
    """Testet Items und das Itemverzeichnis"""

    def test_load_items(self):
        # TODO
        pass


class TestInventar(unittest.TestCase):
    """Testet die Inventar-Funktionen."""

    def assert_(self, item: None | T) -> T:
        self.assertIsNotNone(item)
        return cast(T, item)

    def test_auto_ausrüsten(self) -> None:
        mänx = Mänx(inventar={"Schwert": 1})
        self.assertTrue(mänx.hat_item("Schwert"))
        self.assertTrue(mänx.ist_ausgerüstet("Schwert"))

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
        self.assertTrue(mänx.ist_ausgerüstet("Schwert"), msg="Schwert wurde nicht ausgerüstet")
        mänx.erhalte("Schild")
        mänx.ausrüsten("Schild")
        self.assertTrue(mänx.ist_ausgerüstet("Schwert"))
        self.assertTrue(mänx.ist_ausgerüstet("Schild"))
        mänx.erhalte("Schwert", -1)
        self.assertFalse(mänx.ist_ausgerüstet("Schwert"), msg="Verlieren lässt das Schwert nicht "
                         "verschwinden.")
        mänx.erhalte("mächtige Axt")
        mänx.ausrüsten("mächtige Axt")
        self.assertFalse(mänx.ist_ausgerüstet("Schild"),
                         msg="Schild wurde nicht wegen Axt abgelegt.")
        self.assertTrue(mänx.ist_ausgerüstet("mächtige Axt"))
        mänx.ablegen("mächtige Axt")
        self.assertFalse(mänx.ist_ausgerüstet("mächtige Axt"))

    def test_obenunten(self) -> None:
        oben = "T-Shirt"
        ou = "Lumpen"
        unten = "Leggings"
        assert get_item(oben).ausrüstungsklasse[0].name == "OBEN"  # type: ignore
        assert get_item(ou).ausrüstungsklasse[0].name == "OBENUNTEN"  # type: ignore
        assert get_item(unten).ausrüstungsklasse[0].name == "UNTEN"  # type: ignore
        for item in (oben, ou, unten):
            assert get_item(item).ausrüstungsklasse[1].name == "INNEN"  # type: ignore

        def strips(start, then, do=True):
            if isinstance(start, str):
                start = start,
            mänx = Mänx(inventar={key: 1 for key in start})
            for item in start:
                self.assertTrue(mänx.ist_ausgerüstet(item), msg=f"{
                                item} wurde nicht auto-ausgerüstet")
            mänx.ausrüsten(then)
            self.assertTrue(mänx.ist_ausgerüstet(then), "Neues Item nicht ausgerüstet")
            if do:
                for item in start:
                    self.assertTrue(mänx.ist_ausgerüstet(item), msg=f"{item} wurde nicht abgelegt")
            else:
                for item in start:
                    self.assertFalse(mänx.ist_ausgerüstet(item), msg=f"{item} wurde abgelegt")

        # obenunten entfernt oben
        strips(oben, ou)
        # obenunten entfernt unten
        strips(unten, ou)
        # obenunten entfernt oben + unten
        strips((oben, unten), ou)
        # unten entfernt obenunten
        strips(ou, unten)
        # oben entfernt obenunten
        strips(ou, oben)
        # oben entfernt unten nicht
        strips(unten, oben, do=False)
        # unten entfernt oben nicht
        strips(oben, unten, do=False)

    def test_bekleidet(self) -> None:
        mänx = Mänx()
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.BEKLEIDET)
        mänx = Mänx(inventar={"Schwert": 1})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.NACKT)
