"""Ein NSC-System, das das Template (bei Kompilierzeit erstellt, im Code) und den
gespeicherten Teil trennt. Bei Erstellung soll alles einen eindeutigen Namen haben.
"""
from collections import defaultdict
from collections.abc import Mapping, Iterator, Sequence, Callable
from enum import Enum
import pickle
from typing import Any, Literal

from attrs import define, Factory
import attrs
import cattrs

from xwatc import dorf
from xwatc import system
from xwatc import weg
from xwatc.dorf import Fortsetzung, Rückkehr
from xwatc.system import Inventar, MenuOption, malp, mint, schiebe_inventar, MissingIDError
from xwatc.serialize import converter


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


class Rasse(Enum):
    """Die Rasse des intelligenten/humanoiden Wesens."""
    Mensch = 0
    Munin = 1


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
    ort: str = ""
    """Der Ort, an dem ein NSC startet. Wenn er leer ist, muss er manuell per Events in
    Orte geholt werden."""
    direkt_reden: bool = True
    """Ob bei dem NSC-Menu die Rede-Optionen direkt angezeigt werden."""
    vorstellen_fn: dorf.DialogGeschichte | None = None
    dialoge: list[dorf.Dialog] = Factory(list)

    def __attrs_post_init__(self):
        """Registriere das NSC-Template mit ID und Ort, wenn verfügbar."""
        if self.id_:
            CHAR_REGISTER[self.id_] = self
        if self.ort:
            ORTS_CHARE[self.ort].append(self)

    def zu_nsc(self) -> 'NSC':
        """Erzeuge den zugehörigen NSC aus dem Template."""
        # Der Ort ist zunächst immer None. Der Ort wird erst zugeordnet
        return NSC(self, self.bezeichnung, self.startinventar)

    def dialog(self,
               name: str,
               text: str,
               geschichte: dorf.DialogGeschichte,
               vorherige: str | dorf.VorList = (),
               wiederhole: int = 0,
               min_freundlich: int | None = None,
               zeitpunkt: dorf.Zeitpunkt = dorf.Zeitpunkt.Reden,
               effekt: dorf.DialogFn | None = None,
               gruppe: str | None = None) -> dorf.Dialog:
        "Erstelle einen Dialog"
        dia = dorf.Dialog(
            name=name, text=text, geschichte=geschichte,
            vorherige=vorherige, wiederhole=wiederhole, min_freundlich=min_freundlich,
            zeitpunkt=zeitpunkt, effekt=effekt, gruppe=gruppe)
        self.dialoge.append(dia)
        return dia

    def dialog_deco(self,
                    name: str,
                    text: str,
                    vorherige: str | dorf.VorList = (),
                    wiederhole: int = 0,
                    min_freundlich: int | None = None,
                    zeitpunkt: dorf.Zeitpunkt = dorf.Zeitpunkt.Reden,
                    effekt: dorf.DialogFn | None = None,
                    gruppe: str | None = None) -> Callable[[dorf.DialogFn], dorf.Dialog]:
        """Erstelle einen Dialog als Wrapper. Alle Parameter außer der Funktion sind gleich zu
        Dialog"""
        def wrapper(geschichte: dorf.DialogFn) -> dorf.Dialog:
            dia = dorf.Dialog(
                name=name, text=text, geschichte=geschichte,
                vorherige=vorherige, wiederhole=wiederhole, min_freundlich=min_freundlich,
                zeitpunkt=zeitpunkt, effekt=effekt, gruppe=gruppe)
            self.dialoge.append(dia)
            return dia
        return wrapper

    def vorstellen(self, fn: dorf.DialogGeschichte) -> dorf.DialogGeschichte:
        """Dekorator, um die Vorstellen-Funktion zu setzen
        >>>hans = StoryChar("test:hans", "Hans", Person("m","Spinner"), {})
        ...@vorstellen
        ...def hans_vorstellen(nsc, mänx):
        ...   malp("Ein junger Mann schaut dich neugierig an.") 
        """
        self.vorstellen_fn = fn
        return fn

    def kampf(self, fn: dorf.DialogGeschichte) -> dorf.Dialog:
        """Dekorator, um die Kampf-Funktion zu setzen"""
        dia = dorf.Dialog("k", "Angreifen", fn, zeitpunkt=dorf.Zeitpunkt.Option)
        self.dialoge.append(dia)
        return dia

    @classmethod
    def structure(cls, data, typ) -> 'StoryChar':
        """Create the story char """
        if id_ := data.get("id_"):
            if id_ not in CHAR_REGISTER:
                raise MissingIDError(id_)
            return CHAR_REGISTER[id_]
        return story_char_base_structure(data, typ)


converter.register_structure_hook(StoryChar, StoryChar.structure)
story_char_base_structure = cattrs.gen.make_dict_structure_fn(
    StoryChar, converter)


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

    def __attrs_post_init__(self):
        if self._ort:
            self._ort.menschen.append(self)

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
        if self._ort is not None:
            try:
                self._ort.menschen.remove(self)
            except ValueError:
                pass
        self._ort = ort
        if ort is not None:
            if self not in ort.menschen:
                ort.menschen.append(self)

    def vorstellen(self, mänx: system.Mänx) -> None:
        """So wird der NSC vorgestellt"""
        if self.template.vorstellen_fn:
            self._call_geschichte(
                mänx, self.template.vorstellen_fn, erzähler=True)
        for dialog in self.template.dialoge:
            if dialog.zeitpunkt == dorf.Zeitpunkt.Vorstellen and dialog.verfügbar(self, mänx):
                self._run(dialog, mänx)

    def optionen(self, mänx: system.Mänx) -> Iterator[MenuOption[dorf.RunType]]:
        # yield ("kämpfen", "k", self.kampf)
        for dialog in self.template.dialoge:
            if dialog.zeitpunkt == dorf.Zeitpunkt.Option and dialog.verfügbar(self, mänx):
                yield dialog.zu_option()
        yield ("fliehen" if self.freundlich < 0 else "zurück", "f", self.fliehen)

    def fliehen(self, __) -> None:
        """Vor NSCs kann man immer bedenkenlos fliehen"""
        return None
    
    def kampf(self, mänx: system.Mänx) -> None:
        for dia in self.template.dialoge:
            if dia.name == "k" and dia.verfügbar(self, mänx):
                self._run(dia, mänx)
                return
        malp(f"Dir ist nicht danach, {self.name} anzugreifen.")
            

    def dialog_optionen(self, mänx: system.Mänx) -> Iterator[MenuOption[dorf.Dialog]]:
        for d in self.template.dialoge:
            if d.zeitpunkt == dorf.Zeitpunkt.Reden and d.verfügbar(self, mänx):
                yield d.zu_option()

    def direkte_dialoge(self, mänx: system.Mänx) -> Iterator[dorf.Dialog]:
        """Hole die Dialoge, die direkt abgespielt werden."""
        for d in self.template.dialoge:
            if d.zeitpunkt == dorf.Zeitpunkt.Ansprechen and d.verfügbar(self, mänx):
                yield d

    def main(self, mänx: system.Mänx) -> Fortsetzung | None:
        """Starte die Interaktion mit dem NSC."""
        if self.tot:
            mint(f"{self.name}s Leiche liegt still auf dem Boden.")
            return None
        self.vorstellen(mänx)
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
            opts: dorf._MainOpts
            opts = list()
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
            optionen: list[MenuOption[dorf.Dialog | Rückkehr]]
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

    def _run(self, option: dorf.RunType,
             mänx: system.Mänx) -> Rückkehr | Fortsetzung:
        """Führe eine Option aus."""
        if isinstance(option, dorf.Dialog):
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
                         geschichte: dorf.DialogGeschichte,
                         effekt: dorf.DialogFn | None = None,
                         erzähler: bool = False) -> Rückkehr | Fortsetzung:
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

    def _call_inner(self, text: Sequence[str | dorf.Malp], erzähler: bool,
                    warte: bool = True):
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
                if isinstance(g, dorf.Malp):
                    g()
                else:
                    self.sprich(g)
            if warte:
                mint()

    def sprich(self, text: str | Sequence[str | dorf.Malp], *args, **kwargs) -> None:
        """Minte mit vorgestelltem Namen"""
        if isinstance(text, str):
            system.sprich(self.bezeichnung.kurz_name, text, *args, **kwargs)
        else:
            for block in text:
                if isinstance(block, dorf.Malp):
                    block()
                else:
                    system.sprich(self.bezeichnung.kurz_name, block, *args, **kwargs)

    def add_freundlich(self, wert: int, grenze: int) -> None:
        """Füge Freundlichkeit hinzu, aber überschreite nicht die Grenze."""
        if (wert > 0) == (self.freundlich > grenze):
            return
        elif wert > 0:
            self.freundlich = min(grenze, wert + self.freundlich)
        else:
            self.freundlich = max(grenze, wert + self.freundlich)

    def dialog(self, *args, **kwargs) -> 'dorf.Dialog':
        "Erstelle einen Dialog"
        dia = self.template.dialog(*args, **kwargs)
        assert pickle.dumps(dia)
        return dia

    def plündern(self, mänx: system.Mänx) -> Any:
        """Schiebe das ganze Inventar von NSC zum Mänxen."""
        schiebe_inventar(self.inventar, mänx.inventar)


class OldNSC(NSC):
    """Unterklasse von NSC, die dazu dient, das alte System mit dem neuen zu vereinen.
    Beim alten System war das Template nicht benamt und nicht gespeichert.

    Stattdessen gab
    es die (pickelbare) DLG-Funktion, die dafür zuständig war, die (nicht-pickelbaren)
    Dialoge zu erzeugen. Die pickelbaren Dialoge waren dann außerdem in static_dialogs gespeichert.

    """
    _ort: weg.Wegkreuzung | None

    def __init__(self,
                 name: str,
                 art: str,
                 kampfdialog: dorf.DialogFn | None = None,
                 fliehen: Callable[[system.Mänx], None] | None = None,
                 direkt_reden: bool = False,
                 freundlich: int = 0,
                 startinventar: dict[str, int] | None = None,
                 vorstellen: dorf.DialogGeschichte | None = None,
                 ort: weg.Wegkreuzung | None = None,
                 max_lp: int | None = None,
                 dlg: dorf.DialogErzeugerFn | None = None):
        inventar = startinventar or {}
        template = StoryChar(
            id_=None,
            bezeichnung=(name, art),
            person=None,
            direkt_reden=direkt_reden,
            dialoge=list(dlg()) if dlg else [],
            startinventar=inventar,
            vorstellen_fn=vorstellen
        )
        super().__init__(template, template.bezeichnung,
                         inventar=inventar, ort=ort, freundlich=freundlich)
        self.kampf_fn = kampfdialog
        self.fliehen_fn = fliehen
        self._dlg = dlg
        self._static_dialoge: list[dorf.Dialog] = []

        self.max_lp = max_lp or 100
        # Extra-Daten, die du einem NSC noch geben willst, wie z.B. seine
        # Geschwindigkeit, Alter, ... (vorläufig)
        self.extra_daten: dict[str, Any] = {}

    def kampf(self, mänx: system.Mänx) -> Fortsetzung | None:
        """Starte den Kampf gegen mänx."""
        self.kennt_spieler = True
        if self.kampf_fn:
            ret = self.kampf_fn(self, mänx)
            if isinstance(ret, (bool, Rückkehr)):
                return None
            else:
                return ret
            # if isinstance(ret, Wegpunkt)
        else:
            malp("Dieser Kampfdialog wurde noch nicht hinzugefügt.")
            return None

    def fliehen(self, mänx: system.Mänx):
        if self.fliehen_fn:
            self.fliehen_fn(mänx)
        elif self.freundlich < 0:
            mint("Du entkommst mühelos.")

    def change_dlg(self, new_dlg: dorf.DialogErzeugerFn):
        """Ändere die Dialoge auf eine neue Dlg-Funktion"""
        self._dlg = new_dlg
        self.template.dialoge[:] = new_dlg()


CHAR_REGISTER: dict[str, StoryChar] = {}
"""Ein zentrales Register für StoryChar nach id_"""
ORTS_CHARE: dict[str, list[StoryChar]] = defaultdict(list)
"""Eine Zuordnung Orts-ID -> List von Charakteren, die dort starten."""
