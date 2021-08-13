"""
Anzeige für Xvatc
"""
from __future__ import annotations
from itertools import islice
from functools import wraps
from xwatc.system import Fortsetzung
from contextlib import contextmanager
__author__ = "jasper"
import os
import queue
import threading
from typing import (Tuple, List, Optional as Opt, TextIO, Mapping,
                    Protocol, Sequence, Any, get_type_hints, TypeVar, Callable,
                    ClassVar, NamedTuple)
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

from xwatc import system

Text = str

minput_return: queue.Queue = queue.Queue(1)
_main_thread: threading.Thread
_XwatcThreadExit = object()

KURZ_CODES = {
    "f": ("fliehen", "zurück"),
    "r": ("reden",),
    "k": ("kämpfen",),
    "j": ("ja",),
    "n": ("nein", "norden"),
    "\r": ("weiter",),
    "w": ("weiter",),
}

Tcall = TypeVar("Tcall", bound=Callable)
T = TypeVar("T")


def _idle_wrapper(fn: Tcall) -> Tcall:
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if threading.current_thread() is _main_thread:
            return fn(*args, **kwargs)
        else:
            def inner():
                fn(*args, **kwargs)
                return None
            GLib.idle_add(inner)

    return wrapped  # type: ignore


class XwatcFenster:
    """Ein Fenster, um Xwatc zu spielen."""
    terminal: ClassVar[bool] = False

    def __init__(self, app: Gtk.Application, startpunkt: Opt[Fortsetzung] = None):
        from xwatc_Hauptgeschichte import main as xw_main
        win = Gtk.ApplicationWindow()
        app.add_window(win)
        textview = Gtk.TextView(hexpand=True, vexpand=True, editable=False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.buffer = textview.get_buffer()

        # Optionen
        self.mgn: dict[str, Any] = {}
        # Die Anzahl der nicht versteckten Optionen
        self.mgn_hidden_count: int = 0
        self.anzeigen: dict[type, Gtk.Widget] = {}
        self.sichtbare_anzeigen: set[type] = set()
        self.choice_action: Opt[Callable[[Any], Any]] = None

        self._stack: list[_StackItem] = []
        self.main_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.show_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.main_grid.add(self.show_grid)
        self.show_grid.add(textview)
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.main_grid.add(self.grid)
        win.connect("delete-event", self.fenster_schließt)
        win.connect("key-press-event", self.key_pressed)
        win.add(self.main_grid)
        win.set_default_size(300, 300)
        win.set_title("Xwatc")
        # Spiel beginnen
        self.mänx = system.Mänx(self)
        if startpunkt:
            self.mänx.speicherpunkt = startpunkt
        system.ausgabe = self

        def xwatc_main(mänx=self.mänx):
            try:
                xw_main(mänx)
            except Exception as exp:
                import traceback
                self.buffer.set_text("Xwatc ist abgestürzt:\n"
                                     + traceback.format_exc())

        threading.Thread(target=xwatc_main,
                         name="Xwatc-Geschichte", daemon=True).start()
        win.show_all()

    def malp(self, *text, sep=" ", end='\n', warte=False) -> None:
        """Zeigt *text* zusätzlich an."""
        self.add_text(sep.join(map(str, text)) + end)
        if warte:
            self.auswahl([("weiter", None)])
            if minput_return.get() is _XwatcThreadExit:
                raise SystemExit

    def mint(self, *text):
        """Printe und warte auf ein Enter."""
        self.add_text(" ".join(str(t) for t in text) + "\n")
        self.auswahl([("weiter", None)])
        if minput_return.get() is _XwatcThreadExit:
            raise SystemExit

    def sprich(self, sprecher: str, text: str, warte: bool = False, wie: str = ""):
        if wie:
            sprecher += f"({wie})"
        self.add_text(f'{sprecher}: »{text}«\n')
        if warte:
            self.auswahl([("weiter", None)])
            if minput_return.get() is _XwatcThreadExit:
                raise SystemExit

    @_idle_wrapper
    def add_text(self, text: str) -> None:
        """Füge Text hinzu."""
        self.buffer.insert(self.buffer.get_end_iter(), text)

    def minput(self, _mänx, frage: str, möglichkeiten=None,
               lower=True,
               save: Opt[system.Speicherpunkt] = None) -> str:
        self.malp(frage)
        if möglichkeiten is None:
            self.eingabe(prompt=None)
        else:
            self.auswahl([(mg, mg) for mg in möglichkeiten])
        ans = minput_return.get()
        if ans is _XwatcThreadExit:
            raise SystemExit
        if lower:
            ans = ans.lower()
        return ans

    @_idle_wrapper
    def eingabe(self, prompt: Opt[str]) -> None:
        self._remove_choices()
        entry = Gtk.Entry(visible=True)
        entry.connect("activate", self.entry_activated)
        self.grid.add(entry)
        entry.grab_focus()

    def menu(self,
             _mänx,
             optionen: list[system.MenuOption[T]],
             frage: str = "",
             gucken: Opt[Sequence[str]] = None,
             versteckt: Opt[Mapping[str, T]] = None,
             save: Opt[system.Speicherpunkt] = None) -> T:
        self.auswahl([(name, value, shorthand)
                      for name, shorthand, value in optionen], versteckt)
        ans = minput_return.get()
        if ans is _XwatcThreadExit:
            raise SystemExit
        return ans

    def ja_nein(self, mänx: system.Mänx, frage: str,
                save: Opt[system.Speicherpunkt] = None) -> bool:
        self.malp(frage)
        self.auswahl([("Ja", True), ("Nein", False)])
        ans = minput_return.get()
        if ans is _XwatcThreadExit:
            raise SystemExit
        return ans

    @_idle_wrapper
    def auswahl(self, mgn: Sequence[Tuple[str, Any] | Tuple[str, Any, str]],
                versteckt: Opt[Mapping[str, Any]] = None,
                action: Opt[Callable[[Any], Any]] = None) -> None:
        self._remove_choices()
        self.mgn_hidden_count = len(mgn)
        self.choice_action = action
        for name, antwort, *short in mgn:
            button = Gtk.Button(label=name, visible=True, hexpand=True)
            button.get_child().set_line_wrap(Gtk.WrapMode.WORD_CHAR)
            button.get_child().set_max_width_chars(70)
            button.connect("clicked", self.button_clicked, antwort)
            self.grid.add(button)
            if short:
                name = short[0]
            self.mgn[name.casefold()] = antwort
        if versteckt:
            for name, antwort in versteckt.items():
                self.mgn[name[:1]] = antwort

    @_idle_wrapper
    def show(self, daten: AnzeigeDaten) -> None:
        typ = type(daten)
        if typ in self.anzeigen:
            self.anzeigen[typ].set_visible(True)
            daten.update_widget(self.anzeigen[typ], self)
        else:
            widget = daten.erzeuge_widget(self)
            widget.set_visible(True)
            self.anzeigen[typ] = widget
            self.show_grid.add(widget)
        self.sichtbare_anzeigen.add(typ)

    def key_pressed(self, _widget, event: Gdk.EventKey) -> bool:
        """Ausgeführt, wenn eine Taste gedrückt wird."""
        control = Gdk.ModifierType.CONTROL_MASK & event.state
        taste = event.string
        if not control:
            if not self.mgn:
                return False
            elif taste in self.mgn:
                self.button_clicked(None, self.mgn[taste])
                return True
            elif taste in KURZ_CODES:
                for t in KURZ_CODES[taste]:
                    if t in self.mgn:
                        self.button_clicked(None, t)
                        return True
            if taste == '\r' and len(self.mgn) == 1:
                self.button_clicked(None, next(iter(self.mgn.values())))
            elif len(taste) == 1 and ord('0') <= ord(taste) <= ord('9'):
                nr = int(taste)
                if nr == 0:
                    nr = 10
                if nr <= self.mgn_hidden_count:
                    try:
                        self.button_clicked(None, next(
                            islice(self.mgn.values(), nr - 1, None)))
                        return True
                    except StopIteration:
                        pass
            elif taste == "e":
                self.push_stack()
                self.malp(self.mänx.erweitertes_inventar())
                self.auswahl([("weiter", None)],
                             action=lambda _arg: self.pop_stack())
        else:
            if taste == "s":
                # TODO In Anzeige speichern
                pass
        return False

    def _remove_choices(self):
        # entferne buttons
        for i in range(len(self.grid.get_children())):
            self.grid.remove_row(0)
        for typ, anzeige in self.anzeigen.items():
            if typ not in self.sichtbare_anzeigen:
                anzeige.set_visible(False)

    def _deactivate_choices(self):
        self.mgn.clear()
        self.buffer.set_text("")
        for child in self.grid.get_children():
            if isinstance(child, (Gtk.Button, Gtk.Entry)):
                child.set_sensitive(False)
        self.sichtbare_anzeigen.clear()

    def button_clicked(self, _button: Any, text: Any) -> None:
        self._deactivate_choices()
        if self.choice_action is None:
            minput_return.put(text)
        else:
            self.choice_action(text)

    def entry_activated(self, entry: Gtk.Entry):
        self._deactivate_choices()
        self.buffer.set_text("")
        minput_return.put(entry.get_text())

    def fenster_schließt(self, _window: Gtk.Window, _event) -> bool:
        # TODO warnen wegen nicht gespeichert?
        # xwatc-thread umbringen
        minput_return.put(_XwatcThreadExit)
        return False

    def kursiv(self, text: str) -> Text:
        return text

    def push_stack(self):  # TODO text buffer
        self._stack.append(_StackItem(
            self.mgn.copy(),
            self.mgn_hidden_count,
            self.anzeigen.copy(),
            self.sichtbare_anzeigen,
            self.choice_action,
            self.grid.get_children(),
            self.buffer))
        for child in self.show_grid.get_children():
            if isinstance(child, Gtk.TextView):
                self.buffer = Gtk.TextBuffer()
                child.set_buffer(self.buffer)
                break
        self._deactivate_choices()

    def pop_stack(self):
        self._remove_choices()
        [self.mgn, self.mgn_hidden_count, self.anzeigen,
         self.sichtbare_anzeigen, self.choice_action,
         controls, self.buffer] = self._stack.pop()
        for control in controls:
            self.grid.add(control)
            if isinstance(control, (Gtk.Button, Gtk.Entry)):
                control.set_sensitive(True)
        for child in self.show_grid.get_children():
            if isinstance(child, Gtk.TextView):
                child.set_buffer(self.buffer)

    @contextmanager
    def stack(self):
        self.push_stack()
        try:
            yield None
        finally:
            self.pop_stack()


class _StackItem(NamedTuple):
    mgn: dict[str, Any]
    # Die Anzahl der nicht versteckten Optionen
    mgn_hidden_count: int
    anzeigen: dict[type, Gtk.Widget]
    sichtbare_anzeigen: set[type]
    choice_action: Callable[[Any], Any]
    controls: list[Gtk.Widget]
    buffer: Gtk.TextBuffer


class AnzeigeDaten(Protocol):
    """Anzeigedaten werden durch die XwatcFenster.show()-Methode gezeigt. Ihnen
    ist ein Widget zugeordnet, dass sie selbst erzeugen und updaten.

    Beispielimplementation: xwatc.scenario.anzeige.PixelArtDrawingArea"""

    def erzeuge_widget(self, _fenster: XwatcFenster) -> Gtk.Widget:
        """Erzeugt das Anzeige-Widget für die Daten."""

    def update_widget(self, widget: Gtk.Widget, _fenster: XwatcFenster) -> Any:
        """Aktualisiert das Anzeige-Widget mit den Daten."""


def main(startpunkt: Opt[Fortsetzung] = None):
    global _main_thread
    app = Gtk.Application()
    app.connect("activate", XwatcFenster, startpunkt)
    _main_thread = threading.main_thread()
    app.run()


if __name__ == '__main__':
    main()
