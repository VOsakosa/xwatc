"""
Anzeige für Xvatc mit GTK.
"""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import wraps
from itertools import islice
from logging import getLogger
from pathlib import Path
import queue
import sys
import threading
from typing import Any, Callable, ClassVar, Mapping, NamedTuple, TypeAlias, assert_never, cast
from typing import Protocol, Sequence, TypeVar

from attrs import define
import exceptiongroup
import gi

from xwatc.untersystem.itemverzeichnis import Item
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GObject, GLib, Gtk  # type: ignore # noqa
from typing_extensions import Self  # noqa

from xwatc import XWATC_PATH, _, system  # noqa
from xwatc.system import SPEICHER_VERZEICHNIS, Bekleidetheit, Fortsetzung, Inventar, Menu, Mänx, get_item_or_dummy  # noqa

if False:
    from xwatc.system import Speicherpunkt

__author__ = "jasper"


Text = str

#: Aus dieser Queue werden Antworten an den Xwatc-Thread gelegt.
_minput_return: queue.Queue[Any] = queue.Queue(1)
_main_thread: threading.Thread

# Abkürzungen für häufige Optionen
KURZ_CODES: dict[str, Sequence[str]] = {
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
    """Sorgt dafür, dass nur die GUI-Funktion diese Funktion aufrufen kann."""
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


@define
class AnzeigeSpielEnde(BaseException):
    """Signalisiert, dass der Xvatc-Thread beendet werden muss, da die GUI geschlossen wurde."""

    def __attrs_pre_init__(self):
        super().__init__()


@define
class Unterbrechung:
    """Signalisiert in minput_return, dass der Spieler eine ständig verfügbare Option ausgelöst
    hat, wie z.B. mit seinen Gefährten zu reden. Diese wird auf einem neuen Stack ausgeführt."""
    fkt: system.MänxFkt


@Gtk.Template(string="""
<interface>
  <template class="Auswahlswidget" parent="GtkBox">
    <property name="orientation">vertical</property>
  </template>
</interface>
""")
class Auswahlswidget(Gtk.Box):
    """Eine Box von Buttons"""
    __gtype_name__: ClassVar[str] = "Auswahlswidget"

    def __init__(self, action: Callable[[object], object]) -> None:
        super().__init__()
        # Optionen
        self._mgn: dict[str, object] = {}
        #: Die Anzahl der nicht versteckten Optionen
        self._mgn_hidden_count: int = 0
        self.action: Callable[[object], object] = action

    @_idle_wrapper
    def auswahl(self, mgn: Sequence[tuple[str, T] | tuple[str, T, str]],
                versteckt: Mapping[str, T] | None = None) -> None:
        """Zeige Auswahlmöglichkeiten unten an.

        :param action:
            Die Aktion, die ausgeführt wird, wenn die Auswahl getroffen wird.
            Standardmäßig wird die gewählte Option an den Xwatc-Thread weitergegeben.
        """
        self._remove_choices()
        self._mgn_hidden_count = len(mgn)

        for name, antwort, *short in mgn:
            button = Gtk.Button(label=name, visible=True, hexpand=True)
            child = button.get_child()
            assert isinstance(child, Gtk.Label)
            child.set_wrap(True)
            child.set_max_width_chars(70)
            button.connect("clicked", self._button_clicked, antwort)
            self.append(button)
            if short:
                name = short[0]
            self._mgn[name.casefold()] = antwort
        if versteckt:
            for name, antwort in versteckt.items():
                self._mgn[name[:1]] = antwort

    def eingabe(self, action: Callable[[Any], Any] | None) -> None:
        self._remove_choices()
        self.choice_action = action
        entry = Gtk.Entry(visible=True)
        entry.connect("activate", self.entry_activated)
        self.append(entry)
        entry.grab_focus()

    def _remove_choices(self):
        """Entferne die Auswahlen. Das wird immer vor dem Hinzufügen der neuen Auswahlen
        eingefügt."""
        self._mgn.clear()
        while child := self.get_first_child():
            self.remove(child)

    def deactivate_choices(self) -> None:
        """Graue die Auswahlen aus. Passiert nach jeder Auswahl."""
        for child in get_children(self):
            if isinstance(child, (Gtk.Button, Gtk.Entry)):
                child.set_sensitive(False)

    def activate_choices(self) -> None:
        """Mache die Auswahlen wieder möglich."""
        for child in get_children(self):
            if isinstance(child, (Gtk.Button, Gtk.Entry)):
                child.set_sensitive(True)

    def wähle(self, ans: object) -> None:
        """Wähle programmatisch eine Option."""
        self._button_clicked(None, ans)

    def _button_clicked(self, _button: object, text: object) -> None:
        """Beantwortet die gestellte Frage mit *text*."""
        self.deactivate_choices()
        self.action(text)

    def entry_activated(self, entry: Gtk.Entry) -> None:
        self._button_clicked(entry, entry.get_text())

    def key_pressed(self, taste: str) -> bool:
        """Finde die richtige Aktion mithilfe der Taste."""
        if not self._mgn:
            return False
        elif taste in self._mgn:
            self._button_clicked(None, self._mgn[taste])
            return True
        elif taste in KURZ_CODES:
            for t in KURZ_CODES[taste]:
                if t in self._mgn:
                    self._button_clicked(None, t)
                    return True

        if taste == 'Return' and len(self._mgn) == 1:
            self._button_clicked(None, next(iter(self._mgn.values())))
        elif len(taste) == 1 and ord('0') <= ord(taste) <= ord('9'):
            nr = int(taste)
            if nr == 0:
                nr = 10
            # Versteckte dürfen nicht durch Nummer aktiviert werden.
            if nr <= self._mgn_hidden_count:
                try:
                    self._button_clicked(None, next(
                        islice(self._mgn.values(), nr - 1, None)))
                    return True
                except StopIteration:
                    pass
        return False


class XwatcFenster:
    """Ein Fenster, um Xwatc zu spielen. Es funktioniert als eigene Ausgabe. Die Anzeige
    funktioniert auf Basis eines Stacks, sodass aus geöffneten Menus auf vorherige Stufen
    zurückgekehrt werden kann. Ausgaben werden auf ein Textfeld geschrieben. Eingaben werden
    von Buttons am Ende des Fensters eingeholt."""
    terminal: ClassVar[bool] = False

    def __init__(self, app: Gtk.Application):
        win = Gtk.ApplicationWindow()
        app.add_window(win)
        self.app = app

        # Eigenschaften des Stacks(?)
        self.text_view = Gtk.TextView(hexpand=True, vexpand=True, editable=False)
        self.text_view.add_css_class("main_text_view")
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.buffer = self.text_view.get_buffer()
        self.anzeigen: dict[type, Gtk.Widget] = {}
        self.sichtbare_anzeigen: set[type] = set()
        #: Das wird gemacht, statt an den Xwatc-Thread zurückzugeben.
        self.choice_action: None | Callable[[Any], Any] = None
        self.speicherpunkt: system.Speicherpunkt | None = None

        self.info_widget: InfoWidget = InfoWidget.create()
        self._stack: list[_StackItem] = []
        self.main_grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.show_grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_grid.append(self.info_widget.widget)
        self.main_grid.append(self.show_grid)
        self.show_grid.append(Gtk.ScrolledWindow(hexpand=True, vexpand=True, child=self.text_view))
        self.auswahlwidget = Auswahlswidget(action=self._auswahl_action)
        self.main_grid.append(self.auswahlwidget)
        win.connect("destroy", self.fenster_schließt)
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self.key_pressed)
        win.add_controller(controller)
        win.set_child(self.main_grid)
        win.set_default_size(400, 500)
        win.set_title("Xwatc")
        # Spiel beginnen
        self.mänx: system.Mänx | None = None
        self.unterbrochen = False

    def run(self, startpunkt: None | Fortsetzung = None, *, show: bool = True) -> None:
        system.ausgabe = self
        threading.Thread(target=self._xwatc_thread, args=(startpunkt,),
                         name="Xwatc-Geschichte", daemon=True).start()
        if show:
            cast(Gtk.Window, self.main_grid.get_parent()).present()

    def _xwatc_thread(self, startpunkt: Fortsetzung | None):
        # Das nächste, was passiert. None für Abbruch, die Buchstaben stehen für interne Menüs
        from xwatc.lg import start  # @UnusedImport
        next_: str | Path | None
        try:
            if startpunkt:
                self.mänx = system.Mänx(self)
                next_ = "m"
            else:
                next_ = "h"  # Hauptmenü
            # Next speichert den Zustand (Hauptmenü, Spiel, Lademenü, etc.)
            while next_ is not None:
                if next_ == "h":  # Hauptmenü
                    self.malp(_("Xwatc-Hauptmenü"))
                    if self.menu(None, Menu([(_("Lade Spielstand"), "lade", False),
                                             (_("Neuer Spielstand"), "neu", True)])):
                        self.mänx = system.Mänx(self)
                        next_ = "m"
                    else:
                        next_ = "l"
                elif next_ == "m":  # main (neue Geschichte)
                    assert self.mänx
                    try:
                        system.main_loop(self.mänx, startpunkt)
                    except AnzeigeSpielEnde:
                        raise
                    except Exception as exc:
                        self.mint(_("Xwatc ist abgestürzt:\n")
                                  + "\n".join(exceptiongroup.format_exception(exc))[-10000:])
                        next_ = "h"
                    else:
                        next_ = "h"
                elif next_ == "l":  # Lademenü
                    SPEICHER_VERZEICHNIS.mkdir(exist_ok=True, parents=True)  # @UndefinedVariable
                    options = [
                        (path.stem, path.name.lower(), path) for path in
                        SPEICHER_VERZEICHNIS.iterdir()  # @UndefinedVariable
                    ]
                    if not options:
                        self.malp(_("Keine Speicherstände verfügbar."))
                    else:
                        self.malp(_("Wähle einen Speicherstand zum Laden."))
                    mgn2: Menu[Path | None] = Menu(options + [("Zurück", "zurück", None)])
                    wahl: Path | None = self.menu(None, mgn2)
                    if wahl:
                        next_ = wahl
                    else:
                        next_ = "h"
                elif isinstance(next_, Path):  # laden
                    try:
                        self.mänx, startpunkt = Mänx.load_from_file(next_)
                        assert isinstance(self.mänx, Mänx)
                    except Exception as exc:
                        self.mint(_("Das Laden des Spielstands ist gescheitert:\n") +
                                  "\n".join(exceptiongroup.format_exception(exc))[-10000:])
                        next_ = "h"
                    else:
                        next_ = "m"
                else:
                    assert False, f"Falscher Zustand {next_}"
        except (AnzeigeSpielEnde, system.ZumHauptmenu):
            pass
        finally:
            GLib.idle_add(self.xwatc_ended)

    def _auswahl_action(self, ans: object) -> None:
        """Wird ausgeführt, wenn eine Wahl getroffen wurde."""
        # Der Text wird erst entfernt
        self.buffer.set_text("")
        self.sichtbare_anzeigen.clear()
        # Dann kommen die Aktionen
        if self.choice_action is None:
            _minput_return.put(ans)
        else:
            self.choice_action(ans)

    def get_minput_return(self) -> Any:
        """Hole ein Item aus der Rückgabequeue für Usereingaben.
        Hat der User aber eine Unterbrechung (wie z.B. das Betrachten des Inventars etc.)
        eingereiht, so wird das erst ausgeführt.
        """
        while True:
            ans = _minput_return.get()
            match ans:
                case AnzeigeSpielEnde() | system.ZumHauptmenu():
                    raise ans
                case Unterbrechung(fkt=fkt):
                    if self.mänx and not self.unterbrochen:
                        self.unterbrochen = True
                        GLib.idle_add(self.push_stack)
                        fkt(self.mänx)

                        def ready():
                            self.pop_stack()
                            self.unterbrochen = False
                        GLib.idle_add(ready)
                    else:
                        GLib.idle_add(self.auswahlwidget.activate_choices)
                        if not self.mänx:
                            getLogger("xwatc.anzeige").error(
                                "Unterbrechung eingereiht, ohne Mänxen.")

                case _:
                    return ans

    def _update_status(self) -> None:
        """Update den Status im Info-Widget und verstecke ungenutzte Extra-Anzeigen.
        Ausgeführt vor der Anzeige neuer Optionen.
        """
        for typ, anzeige in self.anzeigen.items():
            if typ not in self.sichtbare_anzeigen:
                anzeige.set_visible(False)
        if self.mänx:
            self.info_widget.update(self.mänx, can_save=self.speicherpunkt is not None)

    def malp(self, *text: object, sep: str = " ", end: str = '\n', warte: bool = False) -> None:
        """Zeigt *text* zusätzlich an."""
        self.add_text(sep.join(map(str, text)) + end)
        if warte:
            self.auswahl([(_("Weiter"), None)])
            self.get_minput_return()

    def mint(self, *text: object) -> None:
        """Printe und warte auf ein Enter."""
        self.add_text(" ".join(str(t) for t in text) + "\n")
        self.auswahl([(_("Weiter"), None)])
        self.get_minput_return()

    def sprich(self, sprecher: str, text: str, warte: bool = False, wie: str = "") -> None:
        if wie:
            sprecher += f"({wie})"
        self.add_text(f'{sprecher}: »{text}«\n')
        if warte:
            self.auswahl([("Weiter", None)])
            self.get_minput_return()

    @_idle_wrapper
    def add_text(self, text: str) -> None:
        """Füge Text hinzu."""
        self.buffer.insert(self.buffer.get_end_iter(), text)

    def minput(self, _mänx, frage: str, lower=True,
               save: system.Speicherpunkt | None = None) -> str:
        self.malp(frage)
        self.speicherpunkt = save
        self.eingabe(prompt=None)
        ans = self.get_minput_return()
        if lower:
            ans = ans.lower()
        return ans

    @_idle_wrapper
    def auswahl(self, mgn: Sequence[tuple[str, T] | tuple[str, T, str]],
                versteckt: Mapping[str, T] | None = None,
                save: system.Speicherpunkt | None = None,
                action: Callable[[T], Any] | None = None) -> None:
        """Zeige Auswahlmöglichkeiten unten an.

        :param action:
            Die Aktion, die ausgeführt wird, wenn die Auswahl getroffen wird.
            Standardmäßig wird die gewählte Option an den Xwatc-Thread weitergegeben.
        """
        self.speicherpunkt = save
        self.choice_action = action
        self._update_status()
        self.auswahlwidget.auswahl(mgn, versteckt)

    @_idle_wrapper
    def eingabe(self, prompt: str | None,
                action: Callable[[str], Any] | None = None,
                save: system.Speicherpunkt | None = None) -> None:
        """Zeigt ein Eingabefeld unten an."""
        if prompt:
            self.malp(prompt)
        self.choice_action = action
        self.save = save
        self._update_status()
        self.auswahlwidget.eingabe(action)

    def menu(self,
             _mänx,
             menu: Menu[T],
             save: system.Speicherpunkt | None = None) -> T:
        if menu.frage:
            self.malp(menu.frage)
        self.auswahl(
            [(name, value, shorthand) for name, shorthand, value in menu.optionen],
            menu.versteckt, save=save)
        ans = self.get_minput_return()
        return ans

    @_idle_wrapper
    def show(self, daten: AnzeigeDaten) -> None:
        """Zeige ein komplizierteres Widget. Siehe :py:`AnzeigeDaten`."""
        typ = type(daten)
        if typ in self.anzeigen:
            self.anzeigen[typ].set_visible(True)
            daten.update_widget(self.anzeigen[typ], self)
        else:
            widget = daten.erzeuge_widget(self)
            widget.set_visible(True)
            self.anzeigen[typ] = widget
            self.show_grid.prepend(widget)
        self.sichtbare_anzeigen.add(typ)

    def key_pressed(self, _controller: object,
                    keyval: int, _keycode: object, state: Gdk.ModifierType) -> bool:
        """Ausgeführt, wenn eine Taste gedrückt wird."""
        control = Gdk.ModifierType.CONTROL_MASK & state
        taste = Gdk.keyval_name(keyval)
        if not taste:
            return False
        if control:
            if taste == "q":
                # Legt ZumHauptmenü in die Minput-Schleife
                self.choice_action = None
                self.auswahlwidget.wähle(system.ZumHauptmenu())
            if self.mänx:
                if taste == 's' or taste == 'S':
                    if self.speicherpunkt:
                        if self.mänx.speicherdatei_name and taste == 's':
                            self.mänx.save(self.speicherpunkt)
                            self.malp_stack(_("Spielstand unter {} gespeichert.").format(
                                self.mänx.speicherdatei_name
                            ))
                        else:
                            self.speichern_als()
                    else:
                        self.malp_stack(_("Du kannst hier nicht speichern."))
                elif taste == "g":
                    _minput_return.put(Unterbrechung(system.Mänx.rede_mit_gefährten))
            return False
        # KEIN STRG: Auswahl der Option
        elif taste == "e" and self.mänx and self.choice_action is None:
            self.auswahlwidget.wähle(Unterbrechung(InventarFenster.run))
            return False
        return self.auswahlwidget.key_pressed(taste)

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

    def fenster_schließt(self, _window: Gtk.Window) -> bool:
        # xwatc-thread umbringen
        _minput_return.put(AnzeigeSpielEnde())
        return False

    def xwatc_ended(self):
        """"""
        root = self.main_grid.get_root()
        if isinstance(root, Gtk.Window):
            root.close()

    def kursiv(self, text: str) -> Text:
        return f"*{text}*"

    def push_stack(self) -> None:
        """Legt ein neues Fenster auf den Stack."""
        self._stack.append(_StackItem(
            self.auswahlwidget._mgn.copy(),
            self.auswahlwidget._mgn_hidden_count,
            self.anzeigen,
            self.sichtbare_anzeigen,
            self.choice_action,
            list(get_children(self.auswahlwidget)),
            self.buffer))
        self.sichtbare_anzeigen = set()
        self.buffer = Gtk.TextBuffer()
        self.text_view.set_buffer(self.buffer)
        self.auswahlwidget.deactivate_choices()

    def pop_stack(self) -> None:
        """Entfernt ein Fenster vom Stack."""
        # kein Update von gezeigten Anzeigen
        self.auswahlwidget._remove_choices()
        [self.auswahlwidget._mgn, self.auswahlwidget._mgn_hidden_count, self.anzeigen,
         self.sichtbare_anzeigen, self.choice_action,
         controls, self.buffer] = self._stack.pop()
        for anzeige_typ, anzeige in self.anzeigen.items():
            anzeige.set_visible(anzeige_typ in self.sichtbare_anzeigen)
        for control in controls:
            self.auswahlwidget.append(control)
            if isinstance(control, (Gtk.Button, Gtk.Entry)):
                control.set_sensitive(True)
        self.text_view.set_buffer(self.buffer)

    @contextmanager
    def stack(self) -> Iterator[None]:
        """Contextmanager für "Mache auf einem Stack"."""
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
    choice_action: None | Callable[[Any], Any]
    controls: list[Gtk.Widget]
    buffer: Gtk.TextBuffer


class AnzeigeDaten(Protocol):
    """Anzeigedaten werden durch die XwatcFenster.show()-Methode gezeigt. Ihnen
    ist ein Widget zugeordnet, dass sie selbst erzeugen und updaten.

    Beispielimplementation: xwatc.scenario.anzeige.PixelArtDrawingArea"""

    def erzeuge_widget(self, _fenster: XwatcFenster) -> Gtk.Widget:
        """Erzeugt das Anzeige-Widget für die Daten.

        Bemerke, dass nach dem erzeugen nicht `update_widget` aufgerufen wird.
        """

    def update_widget(self, widget: Gtk.Widget, _fenster: XwatcFenster) -> object:
        """Aktualisiert das Anzeige-Widget mit den Daten."""


@define
class InfoWidget:
    """Zeigt ständig irgendwelche Infos über den Mänxen, z.B. Zeit und ob gespeichert werden kann.
    """
    widget: Gtk.Box
    tag_label: Gtk.Label
    zeit_label: Gtk.Label
    can_save_label: Gtk.Label

    @classmethod
    def create(cls) -> Self:
        """Erzeuge ein neues InfoWidget."""
        grid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, halign=Gtk.Align.END,
                       spacing=6)
        can_save_label = Gtk.Label()
        tag_label = Gtk.Label()
        zeit_label = Gtk.Label()
        grid.append(can_save_label)
        grid.append(tag_label)
        grid.append(zeit_label)
        return cls(grid, tag_label, zeit_label, can_save_label)

    def update(self, mänx: Mänx, can_save: bool) -> None:
        """Update die angezeigten Informationen."""
        self.tag_label.set_text(_("Tag {}").format(mänx.welt.get_tag()))
        self.zeit_label.set_text(_("{:02}:{:02}").format(*mänx.welt.uhrzeit()))
        if can_save:
            self.can_save_label.set_label("S")
        else:
            self.can_save_label.set_markup('<span color="#AAAAAA">S</span>')


@define
class InventarFenster(AnzeigeDaten):
    """Eine Anzeige des Inventars des Menschen, auf der er seine Ausrüstung ändern kann.
    """
    _mänx: Mänx
    _response_fn: Callable[[tuple[Item, str]], object] | None = None

    @staticmethod
    def run(mänx: Mänx) -> None:
        """Lasse das Inventar-Fenster laufen"""
        daten = InventarFenster(mänx)
        cast(XwatcFenster, mänx.ausgabe).show(daten)
        mänx.menu([("Weiter", "weiter", None)])

    def erzeuge_widget(self, fenster: XwatcFenster) -> Gtk.Widget:
        """Erzeugt das Anzeige-Widget für die Daten."""
        widget = InventarAnzeige()
        widget.set_actions([
            ItemAction("abrüsten", icon="remove-equipment",
                       visible=lambda item: self._mänx.ist_ausgerüstet(item.name),
                       action=lambda item: self._mänx.ablegen(item.name)),
            ItemAction("anlegen", icon="add-equipment",
                       visible=lambda item: item.ausrüstungsklasse and
                       not self._mänx.ist_ausgerüstet(item.name),
                       action=lambda item: self._mänx.ausrüsten(item.name)),
        ])
        self.update_widget(widget, fenster)
        return widget

    def update_widget(self, widget: Gtk.Widget, _fenster: XwatcFenster) -> None:
        """Aktualisiert das Anzeige-Widget mit den Daten."""
        assert isinstance(widget, InventarAnzeige)
        match self._mänx.bekleidetheit:
            case Bekleidetheit.NACKT:
                nackt = _(" [NACKT!]")
            case Bekleidetheit.IN_UNTERWÄSCHE:
                nackt = _(" [in Unterwäsche]")
            case Bekleidetheit.OBERKÖRPERFREI:
                nackt = _(" [oberkörperfrei]")
            case Bekleidetheit.BEKLEIDET:
                nackt = ""
            case other:
                assert_never(other)
        widget.set_top_line("{} Gold{}".format(self._mänx.inventar["Gold"], nackt))
        widget.set_inventar(self._mänx.inventar)


@define
class ItemAction:
    name: str
    visible: Callable[[Item], object]
    action: Callable[[Item], object]
    icon: str


@Gtk.Template(string="""
<interface>
  <template class="InventarAnzeige" parent="GtkBox">
    <property name="orientation">vertical</property>
    <property name="vexpand">1</property>
    <child>
      <object class="GtkLabel" id="top_line">
      </object>
    </child>
    <!--<child>
      <object class="GtkScrolledWindow">-->
        <child>
          <object class="GtkListBox" id="inventar_box">
            <style><class name="sidebar"/><class name="eingerückt"/></style>
            <property name="selection_mode">0</property>
          </object>
        </child>
      <!--</object>
    </child>-->
  </template>
</interface>
""")
class InventarAnzeige(Gtk.Box):
    """Allgemeine Anzeige eines Inventars, die nach Items Optionen in Form von Knöpfen einblendet.
    """
    __gtype_name__ = "InventarAnzeige"
    top_line: Gtk.Label = Gtk.Template.Child()  # type: ignore
    inventar_box: Gtk.ListBox = Gtk.Template.Child()  # type: ignore
    _action_list: list[ItemAction]
    _item_str_template: str
    _buttons: dict[tuple[str, str], Gtk.Button]

    def __init__(self) -> None:
        super().__init__()
        self._item_str_template = '{anzahl:>4}x {item} (<span color="#504000">{item.gold:>3}G</span>)'
        self._action_list = []
        self._buttons = {}
        self.init_template()

    def set_actions(self, actions: Sequence[ItemAction]) -> None:
        """Setze die Liste von Aktionen, die an einem Item sein sollen."""
        self._action_list[:] = actions

    def set_item_str_template(self, text: str) -> None:
        """Set a new item string template."""
        self._item_str_template = text

    def set_inventar(self, inventar: Inventar) -> None:
        """Setze das zugehörige Inventar und baue das Widget auf."""
        self.inventar_box.remove_all()
        self._buttons = {}
        for item, anzahl in inventar.items():
            if item == "Gold":
                continue
            item_obj = get_item_or_dummy(item)
            item_zeile = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            item_zeile.append(
                Gtk.Label(label=self._item_str_template.format(item=item_obj, anzahl=anzahl),
                          use_markup=True))
            for action in self._action_list:
                button = Gtk.Button(icon_name=action.icon, has_frame=False)
                self._buttons[item, action.name] = button
                button.connect("clicked", lambda button, args: self.run_action(*args),
                               (action.name, item))
                button.set_visible(bool(action.visible(item_obj)))
                item_zeile.append(button)
            self.inventar_box.append(item_zeile)

    def set_top_line(self, text: str) -> None:
        self.top_line.set_text(text)

    def run_action(self, name: str, item: str) -> None:
        """Führe eine Aktion auf einem Item aus."""
        actions_dict = {action.name: action for action in self._action_list}
        actions_dict[name].action(get_item_or_dummy(item))
        for (item_name, action_name), button in self._buttons.items():
            button.set_visible(
                bool(actions_dict[action_name].visible(get_item_or_dummy(item_name))))


def _setup_gtk() -> None:
    display = Gdk.Display.get_default()
    assert display
    icon_theme = Gtk.IconTheme.get_for_display(display)
    icon_theme.add_search_path(str(XWATC_PATH / ".." / "share" / "icons"))
    assert "add-equipment" in icon_theme.get_icon_names()
    style_provider = Gtk.CssProvider()
    style_provider.load_from_path(str(XWATC_PATH / 'style.css'))
    Gtk.StyleContext.add_provider_for_display(
        display, style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def main(startpunkt: Fortsetzung | None = None) -> None:
    """Lasse xwatc.anzeige laufen."""
    global _main_thread
    import logging
    getLogger("xwatc").setLevel(logging.INFO)

    _setup_gtk()
    app = Gtk.Application(application_id="com.github.vosakosa.xwatc")
    app.connect("activate", lambda app: XwatcFenster(app).run(startpunkt))
    _main_thread = threading.main_thread()
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
