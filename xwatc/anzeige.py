"""
Anzeige für Xvatc
"""
from __future__ import annotations
from functools import wraps
__author__ = "jasper"
import os
import queue
import threading
from typing import (Tuple, List, Optional as Opt, TextIO, Mapping,
                    Protocol, Sequence, Any, get_type_hints, TypeVar, Callable)
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from xwatc import system

SPEICHER_VERZEICHNIS = os.path.join(os.path.dirname(__file__), "..", "saves")

Text = str

minput_return: queue.Queue = queue.Queue(1)
_main_thread: threading.Thread
_XwatcThreadExit = object()

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

    def __init__(self, app: Gtk.Application):
        from xwatc_Hauptgeschichte import main as xw_main
        win = Gtk.ApplicationWindow()
        app.add_window(win)
        textview = Gtk.TextView(hexpand=True, vexpand=True, editable=False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.buffer = textview.get_buffer()
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.grid.add(textview)
        win.connect("delete-event", self.fenster_schließt)
        win.add(self.grid)
        win.set_default_size(300, 300)
        win.set_title("Xwatc")
        # Spiel beginnen
        self.mänx = system.Mänx(self)
        system.ausgabe = self  # type: ignore
        threading.Thread(target=xw_main, args=(self.mänx,),
                         name="Xwatc-Geschichte").start()
        win.show_all()

    @_idle_wrapper
    def malp(self, *text, sep=" ", end='\n', warte=False) -> None:
        """Zeigt *text* zusätzlich an."""
        self.add_text(sep.join(text)+end)
        
    @_idle_wrapper
    def mint(self, *text):
        """Printe und warte auf ein Enter."""
        self.add_text(" ".join(str(t) for t in text))

    @_idle_wrapper
    def sprich(self, sprecher: str, text: str, warte: bool = False, wie: str = ""):
        if wie:
            sprecher += f"({wie})"
        self.add_text(f'{sprecher}: »{text}«')
    
    def add_text(self, text: str) -> None:
        if self.buffer.get_end_iter().get_offset():
            text = "\n" + text
        self.buffer.insert(self.buffer.get_end_iter(), text)

    def minput(self, mänx: system.Mänx, frage: str, möglichkeiten=None, lower=True) -> str:
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
    
    
    def menu(self,
         mänx: system.Mänx,
         optionen: list[system.MenuOption[T]],
         frage: str = "",
         gucken: Opt[Sequence[str]] = None,
         versteckt: Opt[Mapping[str, T]] = None) -> T:
        self.auswahl([(name, value) for name, __, value in optionen])
        ans = minput_return.get()
        if ans is _XwatcThreadExit:
            raise SystemExit
        return ans
    
    def ja_nein(self, mänx: system.Mänx, frage: str) -> bool:
        self.malp(frage)
        self.auswahl([("Ja", True), ("Nein", False)])
        ans = minput_return.get()
        if ans is _XwatcThreadExit:
            raise SystemExit
        return ans
    
    @_idle_wrapper
    def auswahl(self, mgn: Sequence[Tuple[str, Any]]) -> None:
        self._remove_choices()
        for name, text in mgn:
            button = Gtk.Button(label=name, visible=True)
            button.get_child().set_line_wrap(Gtk.WrapMode.WORD_CHAR)
            button.get_child().set_max_width_chars(70)
            button.connect("clicked", self.button_clicked, text)
            self.grid.add(button)
    
    def _remove_choices(self):
        # entferne buttons
        for i in range(1, len(self.grid.get_children())):
            self.grid.remove_row(1)
        
    def _deactivate_choices(self):
        for child in self.grid.get_children():
            if isinstance(child, (Gtk.Button, Gtk.Entry)):
                child.set_sensitive(False)

    def button_clicked(self, _button: Gtk.Button, text: Any):
        self._deactivate_choices()
        self.buffer.set_text("")
        minput_return.put(text)
    
    def entry_activated(self, entry: Gtk.Entry):
        self._deactivate_choices()
        self.buffer.set_text("")
        minput_return.put(entry.get_text())

    def fenster_schließt(self, _window: Gtk.Window, _event) -> bool:
        # TODO warnen wegen nicht gespeichert?
        # TODO xwatc-thread umbringen
        return False


def main():
    global _main_thread
    app = Gtk.Application()
    app.connect("activate", XwatcFenster)
    _main_thread = threading.main_thread()
    app.run()


if __name__ == '__main__':
    main()
