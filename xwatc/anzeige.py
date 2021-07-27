"""
Anzeige für Xvatc
"""
from __future__ import annotations
__author__ = "jasper"
import os
import queue
import threading
from typing import Tuple, List, Optional as Opt, TextIO, Protocol, Sequence, Any, get_type_hints

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from xwatc import system

SPEICHER_VERZEICHNIS = os.path.join(os.path.dirname(__file__), "..", "saves")

Text = str

minput_return: queue.Queue[str] = queue.Queue(1)


class XwatcFenster:
    """Ein Fenster, um Xwatc zu spielen."""
    def __init__(self, app: Gtk.Application):
        from xwatc_Hauptgeschichte import himmelsrichtungen
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
        connect_minput(self)
        self.mänx = system.Mänx()
        threading.Thread(target=himmelsrichtungen, args=(self.mänx,),
                         name="Xwatc-Geschichte").start()
        win.show_all()

    def malp(self, text: Text) -> None:
        """Zeigt *text* zusätzlich an."""
        self.buffer.insert, text,  self.buffer.get_end_iter()
    
    def minput(self, mgn: Sequence[Tuple[str, Any]]):
        # entferne buttons
        for child in self.grid.get_children()[1:]:
            self.grid.remove(child)
        for name, text in mgn:
            button = Gtk.Button(label=name, visible=True)
            button.connect("clicked", self.button_clicked, text)
            self.grid.add(button)

    def button_clicked(self, _button: Gtk.Button, text: Any):
        for child in self.grid.get_children()[1:]:
            child.set_sensible(False)
        minput_return.put(text)

    def fenster_schließt(self, _window: Gtk.Window, _event) -> bool:
        # TODO warnen wegen nicht gespeichert?
        return False



def main():
    
    app = Gtk.Application()
    app.connect("activate", XwatcFenster)
    app.run()

def connect_minput(app: XwatcFenster):
    from xwatc.system import Mänx
    def replace_in_system(func):
        old_fn = getattr(system, func.__name__)
        setattr(system, func.__name__, func)
        # assert get_type_hints(old_fn) == get_type_hints(func)
        return func
    
    @replace_in_system
    def minput(mänx: Mänx, frage: str, möglichkeiten=None, lower=True) -> str:
        GLib.idle_add(app.malp, frage)
        if möglichkeiten is None:
            raise NotImplementedError("Noch keine Eingaben möglich.")
        else:
            if lower:
                GLib.idle_add(app.minput,[(mg, mg.lower()) for mg in möglichkeiten])
            else:
                GLib.idle_add(app.minput,[(mg, mg) for mg in möglichkeiten])
        return minput_return.get()
    
    @replace_in_system
    def malp(*text, sep=" ", end='\n', warte=False) -> None:
        GLib.idle_add(app.malp, sep.join(text)+end)
        
    


if __name__ == '__main__':
    main()

