"""Karvapedo: Ein Geschichts-Spiel"""
import os
from typing import Tuple, List, Optional as Opt, TextIO

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

SPEICHER_VERZEICHNIS = os.path.join(os.path.dirname(__file__), "saves")

TextId = str
TextInhalt = str
Möglichkeiten = List[Tuple[str, TextId]]
Text = Tuple[TextInhalt, Möglichkeiten]


class Geschichte(Protocol):
    """Eine Geschichte in Karvapedo ist die Einheit eines Spiels und hält
    alle Information spezifisch für die Geschichte.(Welttags)"""
    def save(self, _file: TextIO):
        """Speichert die Geschichte"""

    def load(self, _file: TextIO):
        """Lädt die Geschichte aus der Datei. Der Geschichtenname ist
        bereits eingelesen."""

    def finde_text(self) -> Text:
        """Führe einen Text aus."""


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
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.grid.add(textview)
        win.connect("delete-event", self.fenster_schließt)
        win.add(self.grid)
        win.set_default_size(300, 300)
        win.set_title("Karvapedo")
        self.text("0")
        win.show_all()

    def text(self, name: TextId):
        """Lade und zeige den Text *name*."""
        inhalt, möglichkeiten = self.finde_text(name)
        self.momentan = name
        self.buffer.set_text(inhalt)
        # entferne buttons
        for child in self.grid.get_children():
            if isinstance(child, Gtk.Button):
                self.grid.remove(child)
        for name, text in möglichkeiten:
            button = Gtk.Button(label=name, visible=True)
            button.connect("clicked", self.button_clicked, text)
            self.grid.add(button)

    def button_clicked(self, _button: Gtk.Button, text: TextId):
        if text.startswith("!lade"):
            text = text[5:]
            datei = os.path.join(SPEICHER_VERZEICHNIS, text)
            with open(datei, "r") as file:
                stand = file.readline().strip()
            self.stand = text
            self.text(stand)
        elif text == "!neu":
            nr = 1
            bestehend = os.listdir(SPEICHER_VERZEICHNIS)
            while str(nr) in bestehend:
                nr += 1
            self.stand = str(nr)
            self.text("1")
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


def hauptmenu() -> Text:
    return "", [
        ("Neue Geschichte", "!neu"),
        ("Lade Geschichte", "lade")
    ]


def lade() -> Text:
    os.makedirs(SPEICHER_VERZEICHNIS, exist_ok=True)
    stände = os.listdir(SPEICHER_VERZEICHNIS)
    inhalt = "" if stände else "Du hast keine Speicherstände"
    mgn = [(stand, "!lade" + stand)
           for stand in stände] + [("Zurück", "hauptmenu")]
    return inhalt, mgn


def main():
    app = Gtk.Application()
    app.connect("activate", Karvapedo)
    app.run()


if __name__ == '__main__':
    print("hallo, hallo, ko")
    main()
