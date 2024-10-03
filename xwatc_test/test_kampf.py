""""""
import unittest
from typing import Any

import pytest
from xwatc.kampf import AIController, Kampf, Zieltyp, Kämpfer, MänxController
from xwatc.nsc import NSC, StoryChar
from xwatc.system import Mänx, get_item
from xwatc_test.mock_system import MockSystem


class TestKampf(unittest.TestCase):
    def test_wähle_attacke(self) -> None:
        system = MockSystem()
        mänx = system.install()
        gegner = StoryChar("test:gegner", "Strohpuppe").zu_nsc()
        kampf = Kampf.neu_gegen(mänx, [gegner])
        self.assertEqual(len(kampf.kämpfer), 2)
        controller = kampf.kämpfer[0].controller
        self.assertIsInstance(controller, MänxController)

        # system.ein("a")
        system.ein("faust")
        controller.wähle_attacke(kampf, 0)
        ausgaben = system.pop_ausgaben()

    def test_make_mänx_kämpfer(self) -> None:
        mänx = Mänx()
        kämpfer = Kämpfer.aus_mänx(mänx)
        self.assertEqual(kämpfer.seite, 1)
        self.assertEqual(kämpfer.lp, kämpfer.max_lp)
        self.assertEqual(kämpfer.lp, 100)
        self.assertIsInstance(kämpfer.controller, MänxController)
        self.assertIs(kämpfer.nsc, mänx)

    def test_make_nsc_kämpfer(self) -> None:
        gegner = StoryChar("test:gegner", "Strohpuppe").zu_nsc()
        kämpfer = Kämpfer.aus_nsc(gegner)
        self.assertEqual(kämpfer.seite, 2)
        self.assertEqual(kämpfer.lp, kämpfer.max_lp)
        self.assertEqual(kämpfer.lp, 100)
        self.assertIsInstance(kämpfer.controller, AIController)
        self.assertIs(kämpfer.nsc, gegner)

        kämpfer = Kämpfer.aus_gefährte(gegner)
        self.assertEqual(kämpfer.seite, 1)
        self.assertEqual(kämpfer.lp, kämpfer.max_lp)
        self.assertEqual(kämpfer.lp, 100)
        self.assertIsInstance(kämpfer.controller, MänxController)
        self.assertIs(kämpfer.nsc, gegner)

    def test_get_attacken_mänx(self) -> None:
        mänx = Mänx()
        kämpfer = Kämpfer.aus_mänx(mänx)
        attacken = kämpfer.get_attacken()
        self.assertEqual(len(attacken), 1)
        self.assertEqual(attacken[0].name, "Faustschlag")
        self.assertEqual(attacken[0].zieltyp, Zieltyp.Einzel)

        mänx.erhalte("Schwert")
        mänx.auto_ausrüsten()
        self.assertEqual(mänx.get_waffe(), get_item("Schwert"))
        kämpfer = Kämpfer.aus_mänx(mänx)
        attacken = kämpfer.get_attacken()
        self.assertEqual(len(attacken), 2)
        self.assertEqual(attacken[0].name, "Schlag")
        self.assertEqual(attacken[0].zieltyp, Zieltyp.Einzel)
        self.assertEqual(attacken[1].name, "schwerer Hieb")
        self.assertEqual(attacken[1].zieltyp, Zieltyp.Einzel)

    def test_get_attacken_nsc(self) -> None:
        gefährte = StoryChar("test:mensch", "Dein Freund").zu_nsc()
        kämpfer = Kämpfer.aus_gefährte(gefährte)
        attacken = kämpfer.get_attacken()
        self.assertEqual(len(attacken), 1)
        self.assertEqual(attacken[0].name, "Faustschlag")
        self.assertEqual(attacken[0].zieltyp, Zieltyp.Einzel)

        gefährte.erhalte("Schwert")
        gefährte.auto_ausrüsten()
        self.assertEqual(gefährte.get_waffe(), get_item("Schwert"))
        kämpfer = Kämpfer.aus_gefährte(gefährte)
        attacken = kämpfer.get_attacken()
        self.assertEqual(len(attacken), 2)
        self.assertEqual(attacken[0].name, "Schlag")
        self.assertEqual(attacken[0].zieltyp, Zieltyp.Einzel)
        self.assertEqual(attacken[1].name, "schwerer Hieb")
        self.assertEqual(attacken[1].zieltyp, Zieltyp.Einzel)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    pytest.main()
