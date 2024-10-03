from collections.abc import Iterator
from typing import Any
import unittest
from unittest.mock import Mock

from xwatc.anzeige import InventarAnzeige, InventarFenster
from xwatc_test.mock_system import MockSystem

from gi.repository import Gtk  # type: ignore # isort: skip


def iter_widgets(widget: Gtk.Widget) -> Iterator[Gtk.Widget]:
    while True:
        if child := widget.get_first_child():
            widget = child
        elif sibling := widget.get_next_sibling():
            widget = sibling
        else:
            break
        yield widget


class TestStacks(unittest.TestCase):
    def test_init_and_close_inventar(self) -> None:
        mänx = MockSystem().install()
        fenster = InventarFenster(mänx)
        self.assertIsInstance(fenster, InventarFenster)
        xwatc_fenster: Any = None
        widget = fenster.erzeuge_widget(xwatc_fenster)
        self.assertIsInstance(widget, Gtk.Widget)
        for subwidget in iter_widgets(widget):
            print(subwidget)
            if isinstance(subwidget, Gtk.Label):
                label = subwidget.get_label()
                print(label)
                if label and "mantel" in label.lower():
                    break
        else:
            self.fail('Kein "Mantel" gefunden.')

    def test_ausrüsten(self) -> None:
        mänx = MockSystem().install()
        fenster = InventarFenster(mänx)
        xwatc_fenster: Any = None
        widget = fenster.erzeuge_widget(xwatc_fenster)
        assert isinstance(widget, InventarAnzeige)
        with self.assertRaisesRegex(KeyError, "blubb"):
            widget.run_action("blubb", "Unterhose")
        widget.run_action("abrüsten", "Unterhose")
        self.assertFalse(mänx.ist_ausgerüstet("Unterhose"))
