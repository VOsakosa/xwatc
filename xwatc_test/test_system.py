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
        with self.assertRaisesRegex(ValueError, "Schwert.*ist nicht im Inventar"):
            mänx.ausrüsten("Schwert")
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

    def test_ausrüsten2(self) -> None:
        mänx = Mänx()
        mänx.erhalte("Speisekarte")
        with self.assertRaisesRegex(ValueError, "Speisekarte.*kann nicht ausgerüstet werden"):
            mänx.ausrüsten("Speisekarte")

    def test_obenunten(self) -> None:
        oben = "T-Shirt"
        ou = "Lumpen"
        unten = "Leggings"
        assert get_item(oben).ausrüstungsklasse.ort.name == "OBEN"  # type: ignore
        assert get_item(ou).ausrüstungsklasse.ort.name == "OBENUNTEN"  # type: ignore
        assert get_item(unten).ausrüstungsklasse.ort.name == "UNTEN"  # type: ignore
        for item in (oben, ou, unten):
            assert get_item(item).ausrüstungsklasse.dicke.name == "INNEN"  # type: ignore

        # Auto-Ausrüsten
        mänx = Mänx(inventar={oben: 1, ou: 1})
        self.assertNotEqual(mänx.ist_ausgerüstet(oben), mänx.ist_ausgerüstet(ou))

        mänx = Mänx(inventar={unten: 1, ou: 1})
        self.assertNotEqual(mänx.ist_ausgerüstet(unten), mänx.ist_ausgerüstet(ou))

        mänx = Mänx(inventar={unten: 1, oben: 1})
        self.assertTrue(mänx.ist_ausgerüstet(unten))
        self.assertTrue(mänx.ist_ausgerüstet(oben))

        def strips(start, then, do_strip=True):
            if isinstance(start, str):
                start = start,
            mänx = Mänx(inventar={key: 1 for key in start})
            for item in start:
                self.assertTrue(mänx.ist_ausgerüstet(item),
                                msg=f"{item} wurde nicht auto-ausgerüstet")
            mänx.erhalte(then)
            mänx.ausrüsten(then)
            self.assertTrue(mänx.ist_ausgerüstet(then), "Neues Item nicht ausgerüstet")
            if do_strip:
                for item in start:
                    self.assertFalse(mänx.ist_ausgerüstet(item), msg=f"{item} wurde nicht abgelegt")
            else:
                for item in start:
                    self.assertTrue(mänx.ist_ausgerüstet(item), msg=f"{item} wurde abgelegt")

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
        strips(unten, oben, do_strip=False)
        # unten entfernt oben nicht
        strips(oben, unten, do_strip=False)

    def test_bekleidet(self) -> None:
        mänx = Mänx()
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.BEKLEIDET)
        mänx = Mänx(inventar={"Schwert": 1})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.NACKT)
        mänx = Mänx(inventar={"BH": 1, "Unterhose": 1})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.IN_UNTERWÄSCHE)
        mänx = Mänx(inventar={"Unterhose": 1})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.OBERKÖRPERFREI)
        mänx = Mänx(inventar={"Gürtel": 1})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.NACKT)
        mänx = Mänx(inventar={"Unterhose": 1, "Jeans": 4})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.OBERKÖRPERFREI)
        mänx = Mänx(inventar={"Schwert": 1, "Hemd": 1, "BH": 1})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.NACKT)
        mänx = Mänx(inventar={"Schwert": 1, "Lumpen": 1})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.BEKLEIDET)
        mänx = Mänx(inventar={"Schwert": 1, "Mantel": 1})
        self.assertEqual(mänx.bekleidetheit, Bekleidetheit.NACKT)
