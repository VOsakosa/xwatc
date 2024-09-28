"""Karvapedo: Ein Geschichts-Spiel"""
from __future__ import annotations
from collections.abc import Iterator
import os
from typing import Tuple, List, Optional as Opt, TextIO, Protocol, Sequence

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

SPEICHER_VERZEICHNIS = os.path.join(os.path.dirname(__file__), "..", "saves")

TextId = str
TextInhalt = str
Möglichkeiten = Sequence[Tuple[str, TextId]]
Text = Tuple[TextInhalt, Möglichkeiten]


class Geschichte(Protocol):
    """Eine Geschichte in Karvapedo ist die Einheit eines Spiels und hält
    alle Information spezifisch für die Geschichte.(Welttags)"""

    def save(self, _file: TextIO):
        """Speichert die Geschichte"""

    @staticmethod
    def load(_file: TextIO) -> Geschichte:
        """Lädt die Geschichte aus der Datei. Der Geschichtenname ist
        bereits eingelesen."""

    def finde_text(self, textid: TextId) -> Text:
        """Führe einen Text aus."""

    def starts(self) -> Möglichkeiten:
        """"""
        return []


class Karvapedo:
    momentan: str

    def __init__(self, app: Gtk.Application):
        """Eine Geschichte, aber du kannst Abzweigungen wählen, auch wenn das Endergebnis (wahrscheinlich) gleich
        bleibt."""
        self.stand: Opt[str] = None
        self.geschichte: Opt[Geschichte] = None
        win = Gtk.ApplicationWindow()
        app.add_window(win)
        textview = Gtk.TextView(hexpand=True, vexpand=True, editable=False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.buffer = textview.get_buffer()
        self.grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.grid.append(textview)
        win.connect("delete-event", self.fenster_schließt)
        win.set_child(self.grid)
        win.set_default_size(300, 300)
        win.set_title("Karvapedo")
        self.text("0")
        win.present()

    def text(self, name: TextId):
        """Lade und zeige den Text *name*."""
        inhalt, möglichkeiten = self.finde_text(name)
        self.momentan = name
        self.buffer.set_text(inhalt)
        # entferne buttons
        for child in get_children(self.grid):
            if isinstance(child, Gtk.Button):
                self.grid.remove(child)
        for name, text in möglichkeiten:
            button = Gtk.Button(label=name, visible=True)
            button.connect("clicked", self.button_clicked, text)
            self.grid.append(button)

    def button_clicked(self, _button: Gtk.Button, text: TextId):
        from karvapedo.parse import GeladeneGeschichte
        if text.startswith("!lade"):
            os.makedirs(SPEICHER_VERZEICHNIS, exist_ok=True)
            text = text[5:]
            datei = os.path.join(SPEICHER_VERZEICHNIS, text)
            with open(datei, "r") as file:
                stand = file.readline().strip()
            self.geschichte = GeladeneGeschichte()
            self.stand = text
            self.text(stand)
        elif text.startswith("!neu"):
            os.makedirs(SPEICHER_VERZEICHNIS, exist_ok=True)
            text = text[4:]
            self.geschichte = GeladeneGeschichte()
            nr = 1
            bestehend = os.listdir(SPEICHER_VERZEICHNIS)
            while str(nr) in bestehend:
                nr += 1
            self.stand = str(nr)
            self.text(text)
        else:
            self.text(text)

    def fenster_schließt(self, _window: Gtk.Window, _event) -> bool:
        if self.stand is None:
            return False
        datei = os.path.join(SPEICHER_VERZEICHNIS, self.stand)
        with open(datei, "w") as file:
            print(f"Speichere nach {datei}.")
            file.write(self.momentan)
        return False

    def finde_text(self, name: TextId) -> Text:
        if name == "hauptmenu":
            return hauptmenu()
        elif name == "lade":
            return lade()
        elif name == "neu":
            return self.neu()
        elif name == "0":
            return ("Karvapedo ist eine Sammlung von Geschichten, bei denen du meist geringen und teils "
                    "gewaltigen Einfluss auf das Geschehen hast."), [("weiter", "hauptmenu")]

        elif name == "1":
            return "Blub. Blub. Ich bin ein... Fisch? ", [("weiter", "2"), ("zurück zum Hauptmenu", "hauptmenu")]

        elif name == "2":
            return "Was tat der einarmige Herdazianer dem Mann an, der ihn an die Wand klebte? ", [("Auflösung", "3")]

        elif name == "3":
            return "Gar nichts. Er war 'armlos ", [("zurück", "1")]
        elif self.geschichte:
            return self.geschichte.finde_text(name)
        else:
            raise KeyError(f"Unbekannte Geschichte: {name}")

    def neu(self) -> Text:
        from karvapedo.parse import GeladeneGeschichte
        geschichten = [GeladeneGeschichte()]
        return "", [(a, "!neu" + b) for g in geschichten for a, b in g.starts()]


def hauptmenu() -> Text:
    return "", [
        ("Neue Geschichte", "neu"),
        ("Lade Geschichte", "lade")
    ]


def lade() -> Text:
    os.makedirs(SPEICHER_VERZEICHNIS, exist_ok=True)
    stände = sorted(os.listdir(SPEICHER_VERZEICHNIS))
    inhalt = "" if stände else "Du hast keine Speicherstände"
    mgn = [(stand, "!lade" + stand)
           for stand in stände] + [("Zurück", "hauptmenu")]
    return inhalt, mgn


def main():
    import sys
    app = Gtk.Application()
    app.connect("activate", Karvapedo)
    app.run(sys.argv)


def get_children(box: Gtk.Widget) -> Iterator[Gtk.Widget]:
    """Get all children of a widget. Tries to get the next sibling before yielding an item, to allow
    removing while iterating.
    """
    start = box.get_first_child()
    while start:
        new_start = start.get_next_sibling()
        yield start
        start = new_start


if __name__ == '__main__':
    print("hallo, hallo, ko")
    main()
