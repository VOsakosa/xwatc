"""
Anzeige für Xvatc mit GTK.
"""
from __future__ import annotations

from attrs import define
from itertools import islice

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk


from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from logging import getLogger
import queue
import threading
from typing import (Tuple, Optional as Opt, Mapping,
                    Protocol, Sequence, Any, TypeVar, Callable,
                    ClassVar, NamedTuple)
from typing_extensions import Self
from xwatc import _
from xwatc import system
from xwatc.system import (Fortsetzung, Speicherpunkt, SPEICHER_VERZEICHNIS,
                          MenuOption, Mänx)
__author__ = "jasper"


Text = str

_minput_return: queue.Queue[Any] = queue.Queue(1)
_main_thread: threading.Thread

# Abkürzungen für häufige Optionen
KURZ_CODES = {
    "f": ("fliehen", "zurück"),
    "r": ("reden",),
    "k": ("kämpfen",),
    "j": ("ja",),
    "n": ("nein", "norden"),
    "Return": ("weiter",),
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


class AnzeigeSpielEnde(BaseException):
    """Signalisiert, dass der Xvatc-Thread beendet werden muss, da die GUI geschlossen wurde."""

    def __init__(self, weiter: Opt[Path]):
        self.weiter = weiter


@define
class Unterbrechung:
    """Signalisiert in minput_return, dass der Spieler eine ständig verfügbare Option ausgelöst
    hat, wie z.B. mit seinen Gefährten zu reden. Diese wird auf einem neuen Stack ausgeführt."""
    fkt: system.MänxFkt


class XwatcFenster:
    """Ein Fenster, um Xwatc zu spielen. Es funktioniert als eigene Ausgabe. Die Anzeige
    funktioniert auf Basis eines Stacks, sodass aus geöffneten Menus auf vorherige Stufen
    zurückgekehrt werden kann. Ausgaben werden auf ein Textfeld geschrieben. Eingaben werden
    von Buttons am Ende des Fensters eingeholt."""
    terminal: ClassVar[bool] = False

    def __init__(self, app: Gtk.Application, startpunkt: Opt[Fortsetzung] = None):
        style_provider = Gtk.CssProvider()
        style_provider.load_from_path(str(Path(__file__).parent / 'style.css'))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        win = Gtk.ApplicationWindow()
        app.add_window(win)
        textview = Gtk.TextView(hexpand=True, vexpand=True, editable=False)
        textview.get_style_context().add_class("main_text_view")
        textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.buffer = textview.get_buffer()

        # Optionen
        self.mgn: dict[str, Any] = {}
        # Die Anzahl der nicht versteckten Optionen
        self.mgn_hidden_count: int = 0
        self.anzeigen: dict[type, Gtk.Widget] = {}
        self.sichtbare_anzeigen: set[type] = set()
        self.choice_action: Opt[Callable[[Any], Any]] = None

        self.info_widget: InfoWidget = InfoWidget.create()
        self._stack: list[_StackItem] = []
        self.main_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.show_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.main_grid.add(self.info_widget.widget)
        self.main_grid.add(self.show_grid)
        self.show_grid.add(textview)
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.main_grid.add(self.grid)
        win.connect("destroy", self.fenster_schließt)
        win.connect("key-press-event", self.key_pressed)
        win.add(self.main_grid)
        win.set_default_size(400, 500)
        win.set_title("Xwatc")
        # Spiel beginnen
        self.speicherpunkt: Speicherpunkt | None = None
        self.mänx: Opt[system.Mänx] = None
        self.unterbrochen = False
        system.ausgabe = self
        threading.Thread(target=self._xwatc_thread, args=(startpunkt,),
                         name="Xwatc-Geschichte", daemon=True).start()
        win.show_all()

    def _xwatc_thread(self, startpunkt: Speicherpunkt | None):
        from xwatc_Hauptgeschichte import main as xw_main
        # Das nächste, was passiert. None für Abbruch, die Buchstaben stehen für interne Menüs
        next_: str | Path | None
        try:
            if startpunkt:
                self.mänx = system.Mänx(self)
                next_ = "m"
            else:
                next_ = "h"  # hauptmenu
            # Next speichert den Zustand (Hauptmenü, Spiel, Lademenü, etc.)
            while next_ is not None:
                if next_ == "h":  # hauptmenu
                    self.malp("Xwatc-Hauptmenü")
                    mgn1 = [(_("Lade Spielstand"), "lade", False),
                            (_("Neuer Spielstand"), "neu", True)]
                    if system.ausgabe.menu(None, mgn1):
                        self.mänx = system.Mänx(self)
                        next_ = "m"
                    else:
                        next_ = "l"
                elif next_ == "m":  # main (neue Geschichte)
                    assert self.mänx
                    try:
                        xw_main(self.mänx)
                    except AnzeigeSpielEnde as ende:
                        next_ = ende.weiter
                        continue
                    except Exception:
                        import traceback
                        self.mint(_("Xwatc ist abgestürzt:\n")
                                  + traceback.format_exc())
                        next_ = "h"
                    else:
                        next_ = "h"
                elif next_ == "l":  # Lademenü
                    SPEICHER_VERZEICHNIS.mkdir(exist_ok=True, parents=True)
                    mgn2: list[MenuOption[Opt[Path]]] = [
                        (path.stem, path.name.lower(), path) for path in
                        SPEICHER_VERZEICHNIS.iterdir()  # @UndefinedVariable
                    ]
                    mgn2.append(("Zurück", "zurück", None))
                    wahl = system.ausgabe.menu(None, mgn2)
                    if wahl:
                        next_ = wahl
                    else:
                        next_ = "h"
                elif isinstance(next_, Path):  # laden
                    self.mänx, startpunkt = Mänx.load_from_file(next_)
                    assert isinstance(self.mänx, Mänx)
                    next_ = "m"
                else:
                    assert False, f"Falscher Zustand {next_}"
        except AnzeigeSpielEnde:
            pass
        finally:
            GLib.idle_add(self.xwatc_ended)

    def get_minput_return(self) -> Any:
        while True:
            ans = _minput_return.get()
            match ans:
                case AnzeigeSpielEnde():
                    raise ans
                case Unterbrechung(fkt=fkt):
                    if self.mänx:
                        if not self.unterbrochen:
                            self.unterbrochen = True
                            GLib.idle_add(self.push_stack)
                            fkt(self.mänx)

                            def ready():
                                self.pop_stack()
                                self.unterbrochen = False
                            GLib.idle_add(ready)
                    else:
                        getLogger("xwatc.anzeige").error(
                            "Unterbrechung eingereiht, ohne Mänxen.")

                case _:
                    return ans

    def malp(self, *text, sep=" ", end='\n', warte=False) -> None:
        """Zeigt *text* zusätzlich an."""
        self.add_text(sep.join(map(str, text)) + end)
        if warte:
            self.auswahl([(_("Weiter"), None)])
            self.get_minput_return()

    def mint(self, *text):
        """Printe und warte auf ein Enter."""
        self.add_text(" ".join(str(t) for t in text) + "\n")
        self.auswahl([(_("Weiter"), None)])
        self.get_minput_return()

    def sprich(self, sprecher: str, text: str, warte: bool = False, wie: str = ""):
        if wie:
            sprecher += f"({wie})"
        self.add_text(f'{sprecher}: »{text}«\n')
        if warte:
            self.auswahl([("weiter", None)])
            self.get_minput_return()

    @_idle_wrapper
    def add_text(self, text: str) -> None:
        """Füge Text hinzu."""
        self.buffer.insert(self.buffer.get_end_iter(), text)

    def minput(self, _mänx, frage: str, möglichkeiten=None,
               lower=True,
               save: Opt[Speicherpunkt] = None) -> str:
        self.malp(frage)
        if möglichkeiten is None:
            self.speicherpunkt = save
            self.eingabe(prompt=None)
        else:
            self.auswahl([(mg, mg) for mg in möglichkeiten], save=save)
        ans = self.get_minput_return()
        if lower:
            ans = ans.lower()
        return ans

    @_idle_wrapper
    def eingabe(self, prompt: Opt[str],
                action: Opt[Callable[[str], Any]] = None) -> None:
        if prompt:
            self.malp(prompt)
        self._remove_choices()
        self.choice_action = action
        entry = Gtk.Entry(visible=True)
        entry.connect("activate", self.entry_activated)
        self.grid.add(entry)
        entry.grab_focus()

    def menu(self,
             _mänx,
             optionen: list[system.MenuOption[T]],
             frage: str = "",
             versteckt: Opt[Mapping[str, T]] = None,
             save: Opt[system.Speicherpunkt] = None) -> T:
        if frage:
            self.malp(frage)
        self.auswahl([(name, value, shorthand)
                      for name, shorthand, value in optionen], versteckt, save=save)
        ans = self.get_minput_return()
        return ans

    def ja_nein(self, mänx: system.Mänx, frage: str,
                save: Opt[system.Speicherpunkt] = None) -> bool:
        self.malp(frage)
        self.auswahl([(_("Ja"), True), (_("Nein"), False)], save=save)
        ans = self.get_minput_return()
        return ans

    @_idle_wrapper
    def auswahl(self, mgn: Sequence[Tuple[str, Any] | Tuple[str, Any, str]],
                versteckt: Opt[Mapping[str, Any]] = None,
                save: Opt[Speicherpunkt] = None,
                action: Opt[Callable[[Any], Any]] = None) -> None:
        self.speicherpunkt = save
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
        taste = Gdk.keyval_name(event.keyval)
        if control:
            if self.mänx:
                if taste == 's' or taste == 'S':
                    if self.speicherpunkt:
                        if self.mänx.speicherdatei_name and taste == 's':
                            self.mänx.save(self.speicherpunkt)
                            self.malp_stack(_("Spielstand gespeichert."))
                        else:
                            self.speichern_als()
                    else:
                        self.malp_stack(_("Du kannst hier nicht speichern."))
                elif taste == "g":
                    _minput_return.put(Unterbrechung(
                        system.Mänx.rede_mit_gefährten))
        # KEIN STRG
        elif not self.mgn:
            return False
        elif taste in self.mgn:
            self.button_clicked(None, self.mgn[taste])
            return True
        elif taste in KURZ_CODES:
            for t in KURZ_CODES[taste]:
                if t in self.mgn:
                    self.button_clicked(None, t)
                    return True

        if taste == 'Return' and len(self.mgn) == 1:
            self.button_clicked(None, next(iter(self.mgn.values())))
        elif len(taste) == 1 and ord('0') <= ord(taste) <= ord('9'):
            nr = int(taste)
            if nr == 0:
                nr = 10
            # Versteckte dürfen nicht durch Nummer aktiviert werden.
            if nr <= self.mgn_hidden_count:
                try:
                    self.button_clicked(None, next(
                        islice(self.mgn.values(), nr - 1, None)))
                    return True
                except StopIteration:
                    pass
        elif taste == "e" and self.mänx:
            self.malp_stack(self.mänx.erweitertes_inventar())
        return False

    def malp_stack(self, nachricht: str) -> None:
        """Lege eine Nachricht auf den Stack -- Zeige diese und mache dann weiter."""
        self.push_stack()
        self.malp(nachricht)
        self.auswahl([(_("weiter"), None)],
                     action=lambda _arg: self.pop_stack())

    def speichern_als(self):
        """Zeigt das Speichern-Als-Fenster"""
        self.push_stack()
        self.malp("Unter welchem Namen willst du speichern?")
        vergeben = [
            path.stem for path in SPEICHER_VERZEICHNIS.iterdir()  # @UndefinedVariable
            if path.suffix == ".yaml"]
        if vergeben:
            self.malp("Bereits vergeben sind:", ", ".join(vergeben))
        self.eingabe("Als was möchstest du speichern?",
                     action=self._speichern_als_name)

    def _speichern_als_name(self, name: str):
        """Reagiert auf Speichern-Als."""
        if (SPEICHER_VERZEICHNIS / (name + ".yaml")).exists():
            self.malp(
                "Dieser Name ist bereits vergeben. Willst du überschreiben?")
            self.auswahl([(_("Ja"), name), (_("Nein"), "")],
                         action=self._speichern_als_name2, save=self.speicherpunkt)
        else:
            self._speichern_als_name2(name)

    def _speichern_als_name2(self, name: str):
        if name:
            assert self.speicherpunkt and self.mänx
            self.mänx.save(self.speicherpunkt, name)
        self.pop_stack()
        if name:
            self.malp_stack(_("Gespeichert."))

    def _remove_choices(self):
        # entferne buttons
        for _i in range(len(self.grid.get_children())):
            self.grid.remove_row(0)
        for typ, anzeige in self.anzeigen.items():
            if typ not in self.sichtbare_anzeigen:
                anzeige.set_visible(False)
        if self.mänx:
            self.info_widget.update(self.mänx)

    def _deactivate_choices(self):
        self.mgn.clear()
        self.buffer.set_text("")
        for child in self.grid.get_children():
            if isinstance(child, (Gtk.Button, Gtk.Entry)):
                child.set_sensitive(False)
        self.sichtbare_anzeigen.clear()

    def button_clicked(self, _button: Any, text: Any) -> None:
        """Beantwortet die gestellte Frage mit *text*."""
        self._deactivate_choices()
        if self.choice_action is None:
            _minput_return.put(text)
        else:
            self.choice_action(text)

    def entry_activated(self, entry: Gtk.Entry) -> None:
        self.button_clicked(entry, entry.get_text())

    def fenster_schließt(self, _window: Gtk.Window) -> bool:
        # xwatc-thread umbringen
        _minput_return.put(AnzeigeSpielEnde(None))
        return False

    def xwatc_ended(self):
        """"""
        self.main_grid.get_toplevel().destroy()

    def kursiv(self, text: str) -> Text:
        return f"*{text}*"

    def push_stack(self) -> None:
        """Legt ein neues Fenster auf den Stack."""
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

    def pop_stack(self) -> None:
        """Entfernt ein Fenster vom Stack."""
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
    """Represents a single page to be displayed in the window."""
    mgn: dict[str, Any]
    # Die Anzahl der nicht versteckten Optionen
    mgn_hidden_count: int
    anzeigen: dict[type, Gtk.Widget]
    sichtbare_anzeigen: set[type]
    choice_action: Opt[Callable[[Any], Any]]
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

@define
class InfoWidget:
    """Zeigt ständig irgendwelche Infos über den Mänxen."""
    widget: Gtk.Box
    tag_label: Gtk.Label
    zeit_label: Gtk.Label
    
    @classmethod
    def create(cls) -> Self:
        grid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, halign=Gtk.Align.END)
        tag_label = Gtk.Label(margin_end=12)
        zeit_label = Gtk.Label()
        grid.add(tag_label)
        grid.add(zeit_label)
        return cls(grid, tag_label, zeit_label)
    
    def update(self, mänx: Mänx) -> None:
        self.tag_label.set_text(_("Tag {}").format(mänx.welt.get_tag()))
        self.zeit_label.set_text(_("{:02}:{:02}").format(*mänx.welt.uhrzeit()))
        

def main(startpunkt: Fortsetzung | str | None = None):
    global _main_thread
    import logging
    getLogger("xwatc").setLevel(logging.INFO)
    app = Gtk.Application()
    if isinstance(startpunkt, str):
        startpunkt = system.Besuche(startpunkt)
    app.connect("activate", XwatcFenster, startpunkt)
    _main_thread = threading.main_thread()
    app.run()


if __name__ == '__main__':
    main()
