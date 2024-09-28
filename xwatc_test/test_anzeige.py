from collections.abc import Iterator
import unittest
from unittest.mock import Mock

from xwatc.anzeige import InventarFenster
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
        close_mock = Mock()
        fenster = InventarFenster(mänx).erzeuge_widget(None)
        self.assertIsInstance(fenster, InventarFenster)
        widget = fenster.widget
        self.assertIsInstance(widget, Gtk.Widget)
        for subwidget in iter_widgets(widget):
            print(subwidget)
            if isinstance(subwidget, Gtk.Button):
                label = subwidget.get_label()
                print(label)
                if label and label.lower() in ("weiter", "zurück"):
                    subwidget.emit("clicked")
                    break
        else:
            self.fail('Kein Knopf mit "weiter" oder "zurück" gefunden')
        close_mock.assert_called_once_with()
