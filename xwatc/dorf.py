"""
Xwatc' Ort- und Menschensystem.

Seit 10.10.2020
"""
from __future__ import annotations
from enum import Enum
import random
from typing import List, Union, Callable, Dict, Tuple, Any, Iterator, Iterable
from typing import Optional as Opt, Sequence
from dataclasses import dataclass, field
from xwatc.system import (mint, schiebe_inventar, Spielende, MenuOption,
                          sprich, kursiv)
from xwatc import system
from xwatc.lg.norden.gefängnis_von_gäfdah import gefängnis_von_gäfdah
__author__ = "jasper"

MänxFkt = Callable[[system.Mänx], Any]
NSCOptionen = Iterable[MenuOption[MänxFkt]]
DialogFn = Callable[["NSC", system.Mänx], Opt[bool]]
RunType = Union['Dialog', MänxFkt, 'Rückkehr']
_MainOpts = List[MenuOption[RunType]]
DialogGeschichte = Union[Sequence[str], DialogFn]


class Rückkehr(Enum):
    WEITER_REDEN = 0
    ZURÜCK = 1
    VERLASSEN = 2


class NSC(system.InventarBasis):
    name: str
    art: str

    def __init__(self,
                 name: str,
                 art: str,
                 kampfdialog: Opt[DialogFn] = None,
                 fliehen: Opt[Callable[[system.Mänx], None]] = None,
                 direkt_reden: bool = False, freundlich: int = 0,
                 startinventar: Opt[Dict[str, int]] = None,
                 vorstellen: Opt[DialogGeschichte] = None):
        super().__init__()
        self.name = name
        self.art = art
        self.kennt_spieler = False
        self.tot = False
        self.direkt_reden = direkt_reden
        self.kampf_fn = kampfdialog
        self.vorstellen_fn = vorstellen
        self.freundlich = freundlich
        self.dialoge: List[Dialog] = []
        self.dialog_anzahl: Dict[str, int] = {}
        self.fliehen_fn = fliehen
        if startinventar:
            for a, i in startinventar.items():
                self.inventar[a] += i

    def kampf(self, mänx: system.Mänx) -> None:
        """Starte den Kampf gegen mänx."""
        self.kennt_spieler = True
        if self.kampf_fn:
            self.kampf_fn(self, mänx)
        else:
            raise ValueError(f"Xwatc weiß nicht, wie {self.name} kämpft")

    def fliehen(self, mänx: system.Mänx):
        if self.fliehen_fn:
            self.fliehen_fn(mänx)
        elif self.freundlich < 0:
            mint("Du entkommst mühelos.")

    def vorstellen(self, mänx: system.Mänx) -> None:
        """So wird der NSC vorgestellt"""
        if self.vorstellen_fn:
            self._call_geschichte(mänx, self.vorstellen_fn, use_print=True)

    def optionen(self, mänx: system.Mänx) -> NSCOptionen:  # pylint: disable=unused-argument
        yield ("kämpfen", "k", self.kampf)
        yield ("fliehen" if self.freundlich < 0 else "zurück", "f", self.fliehen)

    def dialog_optionen(self, mänx: system.Mänx) -> Iterator[MenuOption[Dialog]]:
        for d in self.dialoge:
            if d.verfügbar(self, mänx):
                yield d.zu_option()

    def main(self, mänx: system.Mänx) -> Any:
        """Starte die Interaktion mit dem Mänxen."""
        if self.tot:
            mint(f"{self.name}s Leiche liegt still auf dem Boden.")
            return
        self.vorstellen(mänx)
        self._main(mänx)

    def _run(self, option: RunType,
             mänx: system.Mänx) -> Rückkehr:
        """Führe eine Option aus."""
        if isinstance(option, Dialog):
            dlg = option
            dlg_anzahl = self.dialog_anzahl
            ans = self._call_geschichte(mänx, dlg.geschichte)
            dlg_anzahl[dlg.name] = dlg_anzahl.setdefault(dlg.name, 0) + 1
            self.kennt_spieler = True
            return ans
        elif isinstance(option, Rückkehr):
            return option
        elif callable(option):
            ans = option(mänx)
            if isinstance(ans, Rückkehr):
                return ans
            return Rückkehr.VERLASSEN
        else:
            raise TypeError("Could not run {} of type {}".format(
                option, type(option)))

    def _call_geschichte(self, mänx: system.Mänx,
                         geschichte: DialogGeschichte,
                         use_print: bool = False) -> Rückkehr:
        ans = Rückkehr.WEITER_REDEN
        if callable(geschichte):
            ans2 = geschichte(self, mänx)
            if ans2 is False:
                ans = Rückkehr.VERLASSEN
            elif isinstance(ans2, Rückkehr):
                ans = ans2
        elif use_print:
            for g in geschichte[:-1]:
                print(g)
            mint(geschichte[-1])
        else:
            for g in geschichte[:-1]:
                self.sprich(g)
            self.sprich(geschichte[-1], warte=True)
        return ans

    def _main(self, mänx: system.Mänx) -> Any:
        """Das Hauptmenu, möglicherweise ist Reden direkt an."""
        while True:
            opts: _MainOpts
            opts = list(self.optionen(mänx))
            if self.direkt_reden:
                opts.extend(self.dialog_optionen(mänx))
            else:
                opts.append(("reden", "r", self.reden))
            ans = self._run(mänx.menu(opts), mänx)
            if ans not in (Rückkehr.WEITER_REDEN, Rückkehr.ZURÜCK):
                return

    def reden(self, mänx: system.Mänx) -> Rückkehr:
        """Das Menu, wo nur reden möglich ist."""
        if not self.kennt_spieler:
            self.kennt_spieler = True
        ans = Rückkehr.WEITER_REDEN
        start = True
        while ans == Rückkehr.WEITER_REDEN:
            optionen: List[MenuOption[Union[Dialog, Rückkehr]]]
            optionen = list(self.dialog_optionen(mänx))
            if not optionen:
                if start:
                    print("Du weißt nicht, was du sagen könntest.")
                else:
                    print("Du hast nichts mehr zu sagen.")
                return Rückkehr.ZURÜCK
            optionen.append(("Zurück", "f", Rückkehr.ZURÜCK))
            ans = self._run(mänx.menu(optionen), mänx)
            start = False
        return ans

    def sprich(self, text: str, *args, **kwargs) -> None:
        """Minte mit vorgestelltem Namen"""
        system.sprich(self.name, text, *args, **kwargs)  # type: ignore

    def dialog(self, *args, **kwargs) -> 'Dialog':
        "Erstelle einen Dialog"
        dia = Dialog(*args, **kwargs)
        self.dialoge.append(dia)
        return dia

    def plündern(self, mänx: system.Mänx) -> Any:
        """Schiebe das ganze Inventar von NSC zum Mänxen."""
        schiebe_inventar(self.inventar, mänx.inventar)


VorList = List[Union[str, Tuple[str, int]]]


class Dialog:
    """Ein einzelner Gesprächsfaden beim Gespräch mit einem NSC"""
    wenn_fn: Opt[DialogFn]

    def __init__(self,
                 name: str,
                 text: str,
                 geschichte: Union[DialogFn, List[str]],
                 vorherige: Union[str, None, VorList] = None,
                 wiederhole: int = 0):
        # TODO mindestfreundlichkeit
        self.name = name
        self.text = text
        self.geschichte = geschichte
        self.vorherige: VorList
        if isinstance(vorherige, str):
            self.vorherige = [vorherige]
        elif vorherige is not None:
            self.vorherige = vorherige
        else:
            self.vorherige = []

        self.wenn_fn = None
        self.anzahl = wiederhole

    def wenn(self, fn: DialogFn) -> 'Dialog':
        self.wenn_fn = fn
        return self

    def wenn_var(self, *welt_variabeln: str) -> 'Dialog':
        if self.wenn_fn:
            def neue_wenn(nsc, mänx, wf=self.wenn_fn):
                return wf(nsc, mänx) and all(
                    mänx.welt.ist(v) for v in welt_variabeln)
            return self.wenn(neue_wenn)
        else:
            return self.wenn(lambda n, m: all(m.welt.ist(v) for v in welt_variabeln))

    def wiederhole(self, anzahl: int) -> 'Dialog':
        """Füge eine maximale Anzahl von Wiederholungen hinzu"""
        self.anzahl = anzahl
        return self

    def verfügbar(self, nsc: 'NSC', mänx: system.Mänx) -> bool:
        # Keine Wiederholungen mehr
        if self.anzahl and nsc.dialog_anzahl.get(self.name, 0) >= self.anzahl:
            return False
        # vorherige Dialoge
        for bed in self.vorherige:
            if isinstance(bed, str):
                if not nsc.dialog_anzahl.get(bed, 0):
                    return False
            else:
                bed_name, anzahl = bed
                if nsc.dialog_anzahl.get(bed_name, 0) < anzahl:
                    return False
        if self.wenn_fn:
            return bool(self.wenn_fn(nsc, mänx))
        return True

    def zu_option(self) -> MenuOption['Dialog']:
        return (self.text, self.name, self)


class Dorfbewohner(NSC):
    def __init__(self, name: str, geschlecht: bool, **kwargs):
        super().__init__(name, "Dorfbewohner" if geschlecht
                         else "Dorfbewohnerin", **kwargs)
        self.geschlecht = geschlecht
        self.dialog("hallo", "Hallo", lambda n, _:
                    sprich(n.name, f"Hallo, ich bin {n.name}. "
                           "Freut mich, dich kennenzulernen.") or True).wiederhole(1)
        self.dialog("hallo2", "Hallo", lambda n, _:
                    sprich(n.name, "Hallo nochmal!") or True, "hallo")

    def kampf(self, mänx: system.Mänx) -> None:
        if self.kampf_fn:
            return super().kampf(mänx)
        if mänx.hat_klasse("Waffe", "magische Waffe"):
            mint("Du streckst den armen Typen nieder.")
            self.tot = True
            self.plündern(mänx)
        elif self.hat_klasse("Waffe", "magische Waffe"):
            mint(
                f"Du rennst auf {self.name} zu und schlägst wie wild auf "
                + ("ihn" if self.geschlecht else "sie") + " ein."
            )
            if self.hat_item("Dolch"):
                if self.geschlecht:
                    mint("Er ist erschrocken, schafft es aber, seinen Dolch "
                         "hervorzuholen und dich zu erstechen.")
                else:
                    mint("Aber sie zieht seinen Dolch und sticht dich nieder")
                raise Spielende
            else:
                if self.geschlecht:
                    mint("Aber er wehrt sich tödlich.")
                else:
                    mint("Aber sie wehrt sich tödlich.")
                raise Spielende
        elif random.randint(1, 6) != 1:
            print("Irgendwann ist dein Gegner bewusstlos.")
            if mänx.ja_nein("Schlägst du weiter bis er tot ist oder gehst du weg?"):
                print("Irgendwann ist der Arme tot. Du bist ein Mörder. "
                      "Kaltblütig hast du dich dafür entschieden einen lebendigen Menschen zu töten."
                      "", kursiv(" zu ermorden. "), "Mörder.")
            else:
                print("Du gehst weg.")

        else:
            print("Diesmal bist du es, der unterliegt.")
            a = random.randint(1, 10)
            if a != 1:
                mint("Als du wieder aufwachst, bist du woanders.")
                gefängnis_von_gäfdah(mänx)


@dataclass
class Ort:
    """Ein Ort im Dorf, wo sich Menschen aufhalten können"""
    name: str
    text: Union[str, List[str]]
    menschen: List[NSC] = field(default_factory=list)

    def platzangabe(self):
        if isinstance(self.text, str):
            mint(self.text)
        else:
            for line in self.text[:-1]:
                print(line)
            mint(self.text[-1])


class Dorf:
    """Ein Dorf besteht aus mehreren Orten, an denen man Menschen treffen kann.
    Es gibt einen Standard-Ort, nämlich "draußen".
    """

    def __init__(self, name: str, orte: Opt[List[Ort]] = None) -> None:
        if orte:
            self.orte = orte
        else:
            self.orte = [Ort("Draußen", "Du bist draußen.")]
        self.name = name

    def main(self, mänx) -> None:
        print(f"Du bist in {self.name}. Möchtest du einen der Orte betreten oder "
              "draußen bleiben?")
        orte: List[MenuOption[Opt[Ort]]]
        orte = [(ort.name, ort.name.lower(), ort) for ort in self.orte]
        orte.append(("Bleiben", "", self.orte[0]))
        orte.append((f"{self.name} verlassen", "v", None))
        loc = mänx.menu(orte, frage="Wohin? ")
        while loc:
            loc = self.ort_main(mänx, loc)

    def ort_main(self, mänx, ort: Ort) -> Opt[Ort]:
        ort.menschen[:] = filter(lambda m: not m.tot, ort.menschen)
        if ort.menschen:
            print("Hier sind:")
            for mensch in ort.menschen:
                print(f"{mensch.name}, {mensch.art}")
        else:
            print("Hier ist niemand.")
        optionen: List[MenuOption[Union[NSC, Ort, None]]]
        optionen = [("Mit " + mensch.name + " reden", "r" + mensch.name.lower(),
                     mensch) for mensch in ort.menschen]
        optionen.extend((f"Nach {o.name} gehen", "o" + o.name.lower(), o)
                        for o in self.orte if o != ort)
        optionen.append(("Ort verlassen", "fliehen", None))
        opt = mänx.menu(optionen)
        if isinstance(opt, NSC):
            opt.main(mänx)
            return ort
        else:
            return opt
