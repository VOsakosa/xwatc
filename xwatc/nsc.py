"""Ein NSC-System, das das Template (bei Kompilierzeit erstellt, im Code) und den
gespeicherten Teil trennt. Bei Erstellung soll alles einen eindeutigen Namen haben.
"""

from attrs import define, Factory
from enum import Enum
from collections.abc import Mapping, Iterator, Sequence
from typing import Any, Literal
from xwatc import system
from xwatc.system import Inventar, MenuOption
from xwatc import dorf
from xwatc import weg
from xwatc.dorf import Fortsetzung, Rückkehr
import attrs
from collections import defaultdict


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
        case "f":
            return Geschlecht.Weiblich
        case str(other):
            raise ValueError(f"Unbekanntes Geschlecht: {other}")
    raise TypeError(f"Falscher Typ für Geschlecht: {type(attr)} ({attr})")


class Rasse(Enum):
    Mensch = 0
    Munin = 1


@define
class Person:
    """Definiert Eigenschaften, die jedes intelligente Wesen in Xvatc hat."""
    geschlecht: Geschlecht = attrs.field(converter=to_geschlecht)
    rasse: Rasse = Rasse.Mensch
    art: str = ""


@define
class StoryChar:
    """Ein weltweit einzigartiger Charakter, mit eigenen Geschichten."""
    id_: str | None
    """Eine eindeutige Identifikation, wie jtg:torobiac"""
    name: str
    """Das ist der Ingame-Name, wie "Torobias Berndoc". """
    person: Person
    startinventar: Mapping[str, int]
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
        return NSC(self, dict(self.startinventar))

    def dialog(self,
               name: str,
               text: str,
               geschichte: dorf.DialogGeschichte,
               vorherige: str | None | dorf.VorList = None,
               wiederhole: int | None = None,
               min_freundlich: int | None = None,
               direkt: bool = False,
               effekt: dorf.DialogFn | None = None,
               gruppe: str | None = None) -> dorf.Dialog:
        "Erstelle einen Dialog"
        dia = dorf.Dialog(
            name=name, text=text, geschichte=geschichte,
            vorherige=vorherige, wiederhole=wiederhole, min_freundlich=min_freundlich,
            direkt=direkt, effekt=effekt, gruppe=gruppe)
        self.dialoge.append(dia)
        return dia
    # TODO unfertig.


@define
class NSC:
    """Ein NSC, mit dem der Spieler interagieren kann. Alles konkretes ist in template und
    der Rest der Datenstruktur beschäftigt sich mit dem momentanen Status dieses NSCs in der
    Welt."""
    template: StoryChar
    inventar: Inventar
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
        return self.template.name

    @property
    def art(self) -> str:
        return self.template.person.art

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
                mänx, self.template.vorstellen_fn, use_print=True)

    def optionen(self, mänx: system.Mänx) -> dorf.NSCOptionen:  # pylint: disable=unused-argument
        # yield ("kämpfen", "k", self.kampf)
        yield ("fliehen" if self.freundlich < 0 else "zurück", "f", self.fliehen)

    def fliehen(self, __) -> None:
        """Vor NSCs kann man immer bedenkenlos fliehen"""
        return None

    def dialog_optionen(self, mänx: system.Mänx) -> Iterator[MenuOption[dorf.Dialog]]:
        for d in self.template.dialoge:
            if not d.direkt and d.verfügbar(self, mänx):
                yield d.zu_option()

    def direkte_dialoge(self, mänx: system.Mänx) -> Iterator[dorf.Dialog]:
        """Hole die Dialoge, die direkt abgespielt werden."""
        for d in self.template.dialoge:
            if d.direkt and d.verfügbar(self, mänx):
                yield d

    def main(self, mänx: system.Mänx) -> Fortsetzung | None:
        """Starte die Interaktion mit dem NSC."""
        if self.tot:
            system.mint(
                f"{self.template.name}s Leiche liegt still auf dem Boden.")
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
                    system.malp("Du weißt nicht, was du sagen könntest.")
                else:
                    system.malp("Du hast nichts mehr zu sagen.")
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
            ans = self._call_geschichte(mänx, dlg.geschichte,
                                        dlg.geschichte_text)
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
                         text: Sequence[dorf.Malp | str] = (),
                         use_print: bool = False) -> Rückkehr | Fortsetzung:
        ans: Rückkehr | Fortsetzung = Rückkehr.WEITER_REDEN
        if text:
            self._call_inner(text, use_print)
        if callable(geschichte):
            ans2 = geschichte(self, mänx)
            if ans2 is False:
                ans = Rückkehr.VERLASSEN
            elif ans2 is True or ans2 is None:
                pass
            else:
                ans = ans2
        else:
            self._call_inner(geschichte, use_print, True)
        return ans

    def _call_inner(self, text: Sequence[str | dorf.Malp], use_print: bool,
                    warte: bool = True):
        if isinstance(text, str):
            if use_print:
                system.malp(text)
            else:
                self.sprich(text)
        elif use_print:
            for g in text:
                system.malp(g)
        else:
            for g in text:
                if isinstance(g, dorf.Malp):
                    g()
                else:
                    self.sprich(g)
            if warte:
                system.mint()

    def sprich(self, text: str | Sequence[str | dorf.Malp], *args, **kwargs) -> None:
        """Minte mit vorgestelltem Namen"""
        if isinstance(text, str):
            system.sprich(self.template.name, text, *args, **kwargs)
        else:
            for block in text:
                if isinstance(block, dorf.Malp):
                    block()
                else:
                    system.sprich(self.template.name, block, *args, **kwargs)

    def add_freundlich(self, wert: int, grenze: int) -> None:
        """Füge Freundlichkeit hinzu, aber überschreite nicht die Grenze."""
        if (wert > 0) == (self.freundlich > grenze):
            return
        elif wert > 0:
            self.freundlich = min(grenze, wert + self.freundlich)
        else:
            self.freundlich = max(grenze, wert + self.freundlich)

    def plündern(self, mänx: system.Mänx) -> Any:
        """Schiebe das ganze Inventar von NSC zum Mänxen."""
        system.schiebe_inventar(self.inventar, mänx.inventar)


CHAR_REGISTER: dict[str, StoryChar] = {}
"""Ein zentrales Register für StoryChar nach id_"""
ORTS_CHARE: dict[str, list[StoryChar]] = defaultdict(list)
"""Eine Zuordnung Orts-ID -> List von Charakteren, die dort starten."""
