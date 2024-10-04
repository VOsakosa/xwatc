from collections.abc import Iterator
import threading
from typing import Any
import unittest
from unittest.mock import Mock

import pytest

import xwatc.anzeige
from xwatc.anzeige import InventarAnzeige, InventarFenster, XwatcFenster
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


@pytest.mark.usefixtures("xwatc_fenster")
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


class TestAnzeige:
    def test_malp_stack(self, xwatc_fenster: XwatcFenster):
        xwatc_fenster.add_text("Unterer Stack")
        xwatc_fenster.auswahl([("Weiter", None)])
        assert xwatc_fenster.buffer.props.text == "Unterer Stack"
        text = xwatc_fenster.show_grid.get_first_child().get_child()  # type: ignore
        assert isinstance(text, Gtk.TextView)
        assert text.get_buffer() is xwatc_fenster.buffer
        xwatc_fenster.malp_stack("Das ist die neue Nachricht.")
        assert xwatc_fenster.buffer.props.text.strip() == "Das ist die neue Nachricht."

        text = xwatc_fenster.show_grid.get_first_child().get_child()  # type: ignore
        assert isinstance(text, Gtk.TextView)
        assert text.get_buffer() is xwatc_fenster.buffer is xwatc_fenster.text_view.get_buffer()
        assert xwatc_fenster._stack[0].buffer.props.text == "Unterer Stack"

        assert list(xwatc_fenster.auswahlwidget._mgn) == ["weiter"]
        xwatc_fenster.auswahlwidget.wähle(None)  # Hier wird der Stack gepoppt

        assert text.get_buffer() is xwatc_fenster.buffer is xwatc_fenster.text_view.get_buffer()
        assert xwatc_fenster.buffer.props.text == "Unterer Stack"


@pytest.fixture
def xwatc_fenster():
    app = Gtk.Application()
    xwatc.anzeige._main_thread = threading.main_thread()
    return XwatcFenster(app)
