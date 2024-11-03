from collections.abc import Iterator
from functools import wraps
import threading
from time import sleep
from typing import Any, Awaitable, Callable
import unittest
from unittest.mock import Mock

from attrs import define
import pytest

import xwatc.anzeige
import xwatc.lg.mitte
from xwatc.anzeige import InventarAnzeige, InventarFenster, XwatcFenster
from xwatc_test.mock_system import MockSystem

from gi.repository import Gdk, GLib, Gtk  # type: ignore # isort: skip


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

    def test_double_e(self, lg_fenster: XwatcFenster, with_dialogs):
        """Regression test: If you click 'e' while in Inventar, your options were greyed out."""
        lg_fenster.key_pressed(None, Gdk.KEY_e, None, Gdk.ModifierType(0))

        @with_dialogs
        async def inner():
            assert InventarFenster in lg_fenster.sichtbare_anzeigen
            assert len(lg_fenster.auswahlwidget._mgn) == 1
            assert (child := lg_fenster.auswahlwidget.get_first_child())
            assert child.is_sensitive()
            lg_fenster.key_pressed(None, Gdk.KEY_e, None, Gdk.ModifierType(0))
            assert (child := lg_fenster.auswahlwidget.get_first_child())
            assert child.is_sensitive()
            assert InventarFenster in lg_fenster.sichtbare_anzeigen


@pytest.fixture
def xwatc_fenster() -> XwatcFenster:
    app = Gtk.Application()
    xwatc.anzeige._main_thread = threading.main_thread()
    return XwatcFenster(app)


@pytest.fixture
def lg_fenster(xwatc_fenster) -> XwatcFenster:
    xwatc_fenster.run(xwatc.lg.mitte.Eintritt, show=False)
    sleep(0.02)
    assert xwatc_fenster.mänx
    return xwatc_fenster


@define
class GIdle:
    """Waiting for the event loop"""


@pytest.fixture
def with_dialogs(xwatc_fenster) -> Callable[[Callable[..., Awaitable]], None]:
    awaitable = iter(())
    error = None

    def waiter():
        nonlocal error
        try:
            ret = next(awaitable, None)
        except Exception as exc:
            error = exc
            raise
        match ret:
            case None:
                xwatc_fenster.destroy()
                return False
            case GIdle():
                pass
        return True

    def inner(function: Callable[..., Awaitable]) -> None:
        nonlocal awaitable
        awaitable = function().__await__()
        app = xwatc_fenster.app
        app.connect("activate", lambda *__: GLib.idle_add(waiter))
        app.run([])
        if error:
            raise error

    return inner
