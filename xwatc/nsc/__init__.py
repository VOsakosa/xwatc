"""Ein NSC-System, das das Template (bei Kompilierzeit erstellt, im Code) und den
gespeicherten Teil trennt. Bei Erstellung soll alles einen eindeutigen Namen haben.
"""
from xwatc import dorf
from xwatc import system
from xwatc import weg
from xwatc.serialize import converter
from xwatc.system import Fortsetzung, Inventar, MenuOption, malp, mint, schiebe_inventar, MissingIDError
from xwatc.untersystem.person import Rasse

from attrs import define, field, Factory
import attrs
import cattrs

from collections import defaultdict
from collections.abc import Mapping, Iterator, Sequence, Callable
from enum import Enum
from logging import getLogger
from typing import Any, Literal
from xwatc.nsc._dialog import (Dialog, DialogFn, DialogErzeugerFn, DialogGeschichte, Rückkehr,
                               RunType, VorList, Zeitpunkt, Malp, Sprich)


class Geschlecht(Enum):
    Weiblich = 0
    Männlich = 1


def to_geschlecht(attr: Literal["m"] | Literal["w"] | Geschlecht) -> Geschlecht:
    """Wandelt eine Eingabe zu Geschlecht um."""
    match attr:
        case "m":
            return Geschlecht.Männlich
        case Geschlecht():
            return attr
        case "w":
            return Geschlecht.Weiblich
        case str(other):
            raise ValueError(f"Unbekanntes Geschlecht: {other}")
    raise TypeError(f"Falscher Typ für Geschlecht: {type(attr)} ({attr})")


@define
class Person:
    """Definiert Eigenschaften, die jedes intelligente Wesen in Xvatc hat."""
    geschlecht: Geschlecht = attrs.field(converter=to_geschlecht)
    rasse: Rasse = Rasse.Mensch


@define(frozen=True)
class Bezeichnung:
    """Die Ingame-Bezeichnung für den NSC. Sie kann zwischen dem vollen Namen und einer Abkürzung
    für sprich unterscheiden."""
    name: str
    art: str
    kurz_name: str


def bezeichnung(val: str | tuple[str, str] | tuple[str, str, str] | Bezeichnung) -> Bezeichnung:
    """Converter zu Bezeichnung."""
    match val:
        case Bezeichnung():
            return val
        case str():
            return Bezeichnung(val, "", val)
        case [name, art]:
            return Bezeichnung(name, art, name)
        case [vorname, nachname, art]:
            return Bezeichnung(vorname + " " + nachname, art, vorname)
    raise TypeError(f"{val} ist keine Bezeichnung", val)


@define
class StoryChar:
    """Ein weltweit einzigartiger Charakter, mit eigenen Geschichten.

    Diese Klasse ist dazu gedacht, direkt auf Modul-Ebene erzeugt zu werden. Sie registriert
    sich dann von alleine und kann wie durch den Objekt-Cache aufgerufen werden und den spezifischen
    NSC erstellen.
    """
    id_: str | None
    """Eine eindeutige Identifikation, wie jtg:torobiac"""
    bezeichnung: Bezeichnung = attrs.field(converter=bezeichnung)
    """Das ist der Ingame-Name, wie "Torobias Berndoc, Magier". """
    person: Person | None = None
    startinventar: Mapping[str, int] = Factory(lambda: defaultdict(int))
    """Das Inventar, mit dem der Charakter erzeugt wird."""
    # ort: str = ""
    # """Der Ort, an dem ein NSC startet. Wenn er leer ist, muss er manuell per Events in
    # Orte geholt werden."""
    direkt_reden: bool = True
    """Ob bei dem NSC-Menu die Rede-Optionen direkt angezeigt werden."""
    vorstellen_fn: DialogGeschichte | None = None
    dialoge: list[Dialog] = Factory(list)
    randomize_fn: Callable[['NSC'], Any] | None = field(default=None)

    def __attrs_post_init__(self):
        """Registriere das NSC-Template mit ID und Ort, wenn verfügbar."""
        if self.id_:
            CHAR_REGISTER[self.id_] = self
        # if self.ort:
        #    ORTS_CHARE[self.ort].append(self)

    def zu_nsc(self, nr: int = 0) -> 'NSC':
        """Erzeuge den zugehörigen NSC aus dem Template. Dieser wird
        zunächst nirgendwo gespeichert!
        Um den NSC direkt einem Ort zuzuweisen,
        nutze direkt `welt.obj(story_char.id_)`.
        """
        # Der Ort ist zunächst immer None. Der Ort wird erst zugeordnet
        ans = NSC(self, self.bezeichnung, self.startinventar, nr=nr)
        if self.randomize_fn:
            self.randomize_fn(ans)
        return ans

    def erzeuge_mehrere(self, welt: system.Welt, anzahl: int) -> list['NSC']:
        """Erzeuge gleich mehrere, zufällige NSCs."""
        ans = [self.zu_nsc(nr=i) for i in range(anzahl)]
        assert self.id_
        welt.setze_objekt(self.id_, ans)
        return ans

    def dialog(self,
               name: str,
               text: str,
               geschichte: DialogGeschichte,
               vorherige: str | VorList = (),
               wiederhole: int = 0,
               min_freundlich: int | None = None,
               zeitpunkt: Zeitpunkt = Zeitpunkt.Reden,
               effekt: DialogFn | None = None,
               gruppe: str | None = None) -> Dialog:
        "Erstelle einen Dialog"
        dia = Dialog(
            name=name, text=text, geschichte=geschichte,
            vorherige=vorherige, wiederhole=wiederhole, min_freundlich=min_freundlich,
            zeitpunkt=zeitpunkt, effekt=effekt, gruppe=gruppe)
        self.dialoge.append(dia)
        return dia

    def dialog_deco(self,
                    name: str,
                    text: str,
                    vorherige: str | VorList = (),
                    wiederhole: int = 0,
                    min_freundlich: int | None = None,
                    zeitpunkt: Zeitpunkt = Zeitpunkt.Reden,
                    effekt: DialogFn | None = None,
                    gruppe: str | None = None) -> Callable[[DialogFn], Dialog]:
        """Erstelle einen Dialog als Wrapper. Alle Parameter außer der Funktion sind gleich zu
        Dialog"""
        def wrapper(geschichte: DialogFn) -> Dialog:
            dia = Dialog(
                name=name, text=text, geschichte=geschichte,
                vorherige=vorherige, wiederhole=wiederhole, min_freundlich=min_freundlich,
                zeitpunkt=zeitpunkt, effekt=effekt, gruppe=gruppe)
            self.dialoge.append(dia)
            return dia
        return wrapper

    def vorstellen(self, fn: DialogGeschichte) -> DialogGeschichte:
        """Dekorator, um die Vorstellen-Funktion zu setzen
        >>>hans = StoryChar("test:hans", "Hans", Person("m","Spinner"), {})
        ...@vorstellen
        ...def hans_vorstellen(nsc, mänx):
        ...   malp("Ein junger Mann schaut dich neugierig an.") 
        """
        self.vorstellen_fn = fn
        return fn

    def kampf(self, fn: DialogGeschichte) -> Dialog:
        """Dekorator, um die Kampf-Funktion zu setzen"""
        dia = Dialog("k", "Angreifen", fn,
                          zeitpunkt=Zeitpunkt.Option)
        self.dialoge.append(dia)
        return dia

    @classmethod
    def structure(cls, data, typ) -> 'StoryChar':
        """Create the story char """
        if isinstance(data, str):
            id_ = data
            if id_ not in CHAR_REGISTER:
                raise MissingIDError(id_)
            return CHAR_REGISTER[id_]
        raise TypeError(f"Can't structure {data['bezeichnung']['name']}")
        # return story_char_base_structure(data, typ)

    def _unstructure(self) -> dict | str:
        if self.id_:
            return self.id_
        return story_char_base_unstructure(self)


converter.register_structure_hook(StoryChar, StoryChar.structure)
story_char_base_structure = cattrs.gen.make_dict_structure_fn(
    StoryChar, converter)
story_char_base_unstructure = cattrs.gen.make_dict_unstructure_fn(
    StoryChar, converter)
converter.register_unstructure_hook(StoryChar, StoryChar._unstructure)


def structure_geschichte(base, typ) -> DialogGeschichte | None:
    if base is None:
        return None
    return converter.structure(base, Sequence[str | Malp | Sprich])  # type: ignore


converter.register_structure_hook(DialogGeschichte | None, structure_geschichte)


def _copy_inventar(old: Mapping[str, int]) -> defaultdict[str, int]:
    return defaultdict(int, old)


@define
class NSC(system.InventarBasis):
    """Ein NSC, mit dem der Spieler interagieren kann. Alles konkretes ist in template und
    der Rest der Datenstruktur beschäftigt sich mit dem momentanen Status dieses NSCs in der
    Welt."""
    template: StoryChar
    bezeichnung: Bezeichnung
    inventar: Inventar = attrs.field(
        converter=_copy_inventar, factory=lambda: defaultdict(int))
    variablen: set[str] = Factory(set)
    dialog_anzahl: dict[str, int] = Factory(dict)
    kennt_spieler: bool = False
    freundlich: int = 0
    tot: bool = False
    _ort: weg.Wegkreuzung | None = None
    nr: int = 0

    def __attrs_post_init__(self):
        if self._ort:
            self._ort.add_nsc(self)

    @property
    def name(self) -> str:
        return self.bezeichnung.name

    @property
    def art(self) -> str:
        return self.bezeichnung.art

    @property
    def ort(self) -> weg.Wegkreuzung | None:
        """Der Ort/Wegpunkt eines NSCs."""
        return self._ort

    @ort.setter
    def ort(self, ort: weg.Wegkreuzung | None) -> None:
        """Den Ort an einem NSC zu setzen, speichert ihn in die Liste der
        NSCs an einem Ort."""
        if ort is self._ort:
            return
        ort_alt, self._ort = self._ort, ort
        if ort_alt is not None:
            try:
                ort_alt.remove_nsc(self)
            except ValueError:
                pass
        if ort is not None:
            ort.add_nsc(self)

    def vorstellen(self, mänx: system.Mänx) -> None | Fortsetzung | Rückkehr:
        """So wird der NSC vorgestellt"""
        if self.template.vorstellen_fn:
            ans = self._call_geschichte(
                mänx, self.template.vorstellen_fn, erzähler=True)
            if ans != Rückkehr.WEITER_REDEN:
                return ans
        for dialog in self.template.dialoge:
            if dialog.zeitpunkt == Zeitpunkt.Vorstellen and dialog.verfügbar(self, mänx):
                ans = self._run(dialog, mänx)
                if ans != Rückkehr.WEITER_REDEN:
                    return ans
        return None

    def optionen(self, mänx: system.Mänx) -> Iterator[MenuOption[RunType]]:
        """Gibt die zusätzlichen Optionen außer Reden zurück."""
        fliehen_da = False
        for dialog in self.template.dialoge:
            if dialog.zeitpunkt == Zeitpunkt.Option and dialog.verfügbar(self, mänx):
                yield dialog.zu_option()
                if dialog.name in ("fliehen", "zurück"):
                    fliehen_da = True
        if not fliehen_da:
            yield ("fliehen" if self.freundlich < 0 else "zurück", "f", self.fliehen)

    def fliehen(self, __) -> None:
        """Vor NSCs kann man immer bedenkenlos fliehen"""
        return None

    def kampf(self, mänx: system.Mänx) -> Rückkehr | Fortsetzung:
        """Startet den Standard-Kampf, falls verfügbar."""
        for dia in self.template.dialoge:
            if dia.name == "k" and dia.verfügbar(self, mänx):
                return self._run(dia, mänx)
        malp(f"Dir ist nicht danach, {self.name} anzugreifen.")
        return Rückkehr.VERLASSEN

    def dialog_optionen(self, mänx: system.Mänx) -> Iterator[MenuOption[Dialog]]:
        """Hole die Dialoge, die der Mänx einleitet."""
        for d in self.template.dialoge:
            if d.zeitpunkt == Zeitpunkt.Reden and d.verfügbar(self, mänx):
                yield d.zu_option()

    def direkte_dialoge(self, mänx: system.Mänx) -> Iterator[Dialog]:
        """Hole die Dialoge, die direkt beim Ansprechen abgespielt werden."""
        for d in self.template.dialoge:
            if d.zeitpunkt == Zeitpunkt.Ansprechen and d.verfügbar(self, mänx):
                yield d

    def main(self, mänx: system.Mänx) -> Fortsetzung | None:
        """Starte die Interaktion mit dem NSC."""
        if self.tot:
            mint(f"{self.name}s Leiche liegt still auf dem Boden.")
            return None
        vorstellung = self.vorstellen(mänx)
        # intermediäre variable wegen
        # https://github.com/python/mypy/issues/12998
        match vorstellung:
            case None:  # @UnusedVariable
                pass
            case Rückkehr():
                return None
            case fortsetzung:
                return fortsetzung
        return self._main(mänx)

    def _main(self, mänx: system.Mänx) -> Fortsetzung | None:
        """Das Hauptmenu, möglicherweise ist Reden direkt an."""
        for dia in self.direkte_dialoge(mänx):
            ans = self._run(dia, mänx)
            if ans != Rückkehr.WEITER_REDEN:
                if isinstance(ans, Rückkehr):
                    return None
                else:
                    return ans
        while True:
            opts = list[MenuOption[RunType]]()
            if self.template.direkt_reden:
                opts.extend(self.dialog_optionen(mänx))
            else:
                opts.append(("reden", "r", self.reden))
            opts.extend(self.optionen(mänx))
            ans = self._run(mänx.menu(opts, save=self), mänx)
            if isinstance(ans, Rückkehr):
                if ans == Rückkehr.VERLASSEN:
                    return None
            else:
                return ans

    def reden(self, mänx: system.Mänx) -> Rückkehr | Fortsetzung:
        """Das Menu, wo nur reden möglich ist."""
        if not self.kennt_spieler:
            self.kennt_spieler = True
        ans: Rückkehr | Fortsetzung = Rückkehr.WEITER_REDEN
        start = True
        for dia in self.direkte_dialoge(mänx):
            ans = self._run(dia, mänx)
            if ans != Rückkehr.WEITER_REDEN:
                return ans
        while ans == Rückkehr.WEITER_REDEN:
            optionen: list[MenuOption[Dialog | Rückkehr]]
            optionen = list(self.dialog_optionen(mänx))
            if not optionen:
                if start:
                    malp("Du weißt nicht, was du sagen könntest.")
                else:
                    malp("Du hast nichts mehr zu sagen.")
                return Rückkehr.ZURÜCK
            optionen.append(("Zurück", "f", Rückkehr.ZURÜCK))
            ans = self._run(mänx.menu(optionen), mänx)
            start = False
        return ans

    def _run(self, option: RunType,
             mänx: system.Mänx) -> Rückkehr | Fortsetzung:
        """Führe eine Option aus."""
        if isinstance(option, Dialog):
            getLogger("xwatc.nsc").info(
                f"Starte Dialog {option.name} von {self.name}")
            dlg = option
            dlg_anzahl = self.dialog_anzahl
            ans = self._call_geschichte(mänx, dlg.geschichte, dlg.effekt)
            dlg_anzahl[dlg.name] = dlg_anzahl.setdefault(dlg.name, 0) + 1
            if dlg.gruppe:
                dlg_anzahl[dlg.gruppe] = dlg_anzahl.setdefault(
                    dlg.gruppe, 0) + 1
            self.kennt_spieler = True
            return ans
        elif isinstance(option, Rückkehr):
            return option
        elif callable(option):
            ans = option(mänx)
            if isinstance(ans, Rückkehr):
                return ans
            elif ans:
                return ans
            return Rückkehr.VERLASSEN
        else:
            raise TypeError("Could not run {} of type {}".format(
                option, type(option)))

    def _call_geschichte(self, mänx: system.Mänx,
                         geschichte: DialogGeschichte,
                         effekt: DialogFn | None = None,
                         erzähler: bool = False) -> Rückkehr | Fortsetzung:
        """Führe den Geschichtsteil eines Dialoges aus."""
        ans: Rückkehr | Fortsetzung = Rückkehr.WEITER_REDEN
        if callable(geschichte):
            ans2 = geschichte(self, mänx)
            if ans2 is False:
                ans = Rückkehr.VERLASSEN
            elif ans2 is True or ans2 is None:
                pass
            else:
                ans = ans2
        else:
            self._call_inner(geschichte, erzähler, True)

        if effekt:
            ans3 = effekt(self, mänx)
            if ans3 and ans3 is not True:
                ans = ans3
        return ans

    def _call_inner(self, text: Sequence[str | Malp | Sprich], erzähler: bool,
                    warte: bool = True):
        """Führe einen Text des Dialoges aus."""
        if isinstance(text, str):
            if erzähler:
                malp(text)
            else:
                self.sprich(text)
        elif erzähler:
            for g in text:
                malp(g)
        else:
            for g in text:
                if isinstance(g, Malp):
                    g()
                elif isinstance(g, Sprich):
                    self.sprich(g.text, wie=g.wie)
                else:
                    self.sprich(g)
            if warte:
                mint()

    def sprich(self, text: str | Sequence[str | Malp], *args, **kwargs) -> None:
        """Minte mit vorgestelltem Namen"""
        if isinstance(text, str):
            system.sprich(self.bezeichnung.kurz_name, text, *args, **kwargs)
        else:
            for block in text:
                if isinstance(block, Malp):
                    block()
                else:
                    system.sprich(self.bezeichnung.kurz_name,
                                  block, *args, **kwargs)

    def add_freundlich(self, wert: int, grenze: int) -> None:
        """Füge Freundlichkeit hinzu, aber überschreite nicht die Grenze."""
        if (wert > 0) == (self.freundlich > grenze):
            return
        elif wert > 0:
            self.freundlich = min(grenze, wert + self.freundlich)
        else:
            self.freundlich = max(grenze, wert + self.freundlich)

    def dialog(self, *args, **kwargs) -> 'Dialog':
        "Erstelle einen Dialog"
        dia = self.template.dialog(*args, **kwargs)
        return dia

    def plündern(self, mänx: system.Mänx) -> Any:
        """Schiebe das ganze Inventar von NSC zum Mänxen."""
        schiebe_inventar(self.inventar, mänx.inventar)


def mache_monster(
        id_: str,
        name: str | tuple[str, str] | tuple[str, str, str] | Bezeichnung,
        beute: Mapping[str, int] | None = None
) -> Callable[[DialogFn], StoryChar]:
    """Decorator, um ein Monster zu machen, mit der Kampffunktion gegeben.
    ```

    ```
    """
    def wrapper(geschichte: DialogFn) -> StoryChar:
        ans = StoryChar(id_, name, startinventar=beute or {})
        ans.kampf(geschichte)
        return ans
    return wrapper


CHAR_REGISTER: dict[str, StoryChar] = {}
"""Ein zentrales Register für StoryChar nach id_"""
ORTS_CHARE: dict[str, list[StoryChar]] = defaultdict(list)
"""Eine Zuordnung Orts-ID -> List von Charakteren, die dort starten."""
