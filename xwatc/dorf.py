"""
Xwatc' Ort- und Menschensystem.

Seit 10.10.2020
"""
from __future__ import annotations
from enum import Enum
import random
from typing import List, Union, Callable, Dict, Tuple, Any, Iterator, Iterable
from typing import Optional as Opt, Sequence
from dataclasses import dataclass
from xwatc.system import (mint, malp, schiebe_inventar, Spielende, MenuOption,
                          sprich, kursiv, MänxFkt, Welt)
from xwatc import system
from xwatc.lg.norden.gefängnis_von_gäfdah import gefängnis_von_gäfdah
from xwatc import weg
__author__ = "jasper"


NSCOptionen = Iterable[MenuOption[MänxFkt]]
DialogFn = Callable[["NSC", system.Mänx], Opt[bool]]
RunType = Union['Dialog', MänxFkt, 'Rückkehr']
_MainOpts = List[MenuOption[RunType]]
DialogGeschichte = Union[Sequence[Union['Malp', str]], DialogFn]


class Rückkehr(Enum):
    WEITER_REDEN = 0
    ZURÜCK = 1
    VERLASSEN = 2


class NSC(system.InventarBasis):
    """Ein NSC hat ein Inventar und verschiedene Dialoge."""
    name: str
    art: str
    _ort: Opt[weg.Wegkreuzung]

    def __init__(self,
                 name: str,
                 art: str,
                 kampfdialog: Opt[DialogFn] = None,
                 fliehen: Opt[Callable[[system.Mänx], None]] = None,
                 direkt_reden: bool = False, freundlich: int = 0,
                 startinventar: Opt[Dict[str, int]] = None,
                 vorstellen: Opt[DialogGeschichte] = None,
                 ort: Opt[weg.Wegkreuzung] = None,
                 max_lp: Opt[int] = None):
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
        self._ort = None
        self.ort = ort
        self.max_lp = max_lp or 100
        if startinventar:
            for a, i in startinventar.items():
                self.inventar[a] += i

    def kampf(self, mänx: system.Mänx) -> None:
        """Starte den Kampf gegen mänx."""
        self.kennt_spieler = True
        if self.kampf_fn:
            ret = self.kampf_fn(self, mänx)
            # if isinstance(ret, Wegpunkt)
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
            if not d.direkt and d.verfügbar(self, mänx):
                yield d.zu_option()

    def direkte_dialoge(self, mänx: system.Mänx) -> Iterator[Dialog]:
        for d in self.dialoge:
            if d.direkt and d.verfügbar(self, mänx):
                yield d

    def main(self, mänx: system.Mänx) -> Any:
        """Starte die Interaktion mit dem Mänxen."""
        if self.tot:
            mint(f"{self.name}s Leiche liegt still auf dem Boden.")
            return
        self.vorstellen(mänx)
        return self._main(mänx)

    def _run(self, option: RunType,
             mänx: system.Mänx) -> Rückkehr:
        """Führe eine Option aus."""
        if isinstance(option, Dialog):
            dlg = option
            dlg_anzahl = self.dialog_anzahl
            ans = self._call_geschichte(mänx, dlg.geschichte,
                                        dlg.geschichte_text)
            dlg_anzahl[dlg.name] = dlg_anzahl.setdefault(dlg.name, 0) + 1
            if dlg.gruppe:
                dlg_anzahl[dlg.gruppe] = dlg_anzahl.setdefault(dlg.gruppe, 0) + 1
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
                         text: Opt[Sequence[Union['Malp', str]]] = (),
                         use_print: bool = False) -> Rückkehr:
        ans = Rückkehr.WEITER_REDEN
        if text:
            if use_print:
                for g in text:
                    malp(g)
            else:
                for g in text:
                    if isinstance(g, Malp):
                        g()
                    else:
                        self.sprich(g)
        if callable(geschichte):
            ans2 = geschichte(self, mänx)
            if ans2 is False:
                ans = Rückkehr.VERLASSEN
            elif isinstance(ans2, Rückkehr):
                ans = ans2
        elif use_print:
            for g in geschichte[:-1]:
                malp(g)
            mint(geschichte[-1])
        else:
            for g in geschichte:
                if isinstance(g, Malp):
                    g()
                else:
                    self.sprich(g)
            mint()
        return ans

    def _main(self, mänx: system.Mänx) -> Any:
        """Das Hauptmenu, möglicherweise ist Reden direkt an."""
        if self.direkt_reden:
            for dia in self.direkte_dialoge(mänx):
                if self._run(dia, mänx) != Rückkehr.WEITER_REDEN:
                    return
        while True:
            opts: _MainOpts
            opts = list(self.optionen(mänx))
            if self.direkt_reden:
                opts.extend(self.dialog_optionen(mänx))
            else:
                opts.append(("reden", "r", self.reden))
            ans = self._run(mänx.menu(opts), mänx)
            if ans not in (Rückkehr.WEITER_REDEN, Rückkehr.ZURÜCK):
                return ans

    def reden(self, mänx: system.Mänx) -> Rückkehr:
        """Das Menu, wo nur reden möglich ist."""
        if not self.kennt_spieler:
            self.kennt_spieler = True
        ans = Rückkehr.WEITER_REDEN
        start = True
        for dia in self.direkte_dialoge(mänx):
            ans = self._run(dia, mänx)
            if ans != Rückkehr.WEITER_REDEN:
                return ans
        while ans == Rückkehr.WEITER_REDEN:
            optionen: List[MenuOption[Union[Dialog, Rückkehr]]]
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

    def sprich(self, text: str|Iterable[str|Malp], *args, **kwargs) -> None:
        """Minte mit vorgestelltem Namen"""
        if isinstance(text, str):
            system.sprich(self.name, text, *args, **kwargs)
        else:
            for block in text:
                if isinstance(block, Malp):
                    block = block.text
                system.sprich(self.name, block, *args, **kwargs)
                    

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
        dia = Dialog(*args, **kwargs)
        self.dialoge.append(dia)
        return dia

    def plündern(self, mänx: system.Mänx) -> Any:
        """Schiebe das ganze Inventar von NSC zum Mänxen."""
        schiebe_inventar(self.inventar, mänx.inventar)

    @property
    def ort(self)-> Opt[weg.Wegkreuzung]:
        return self._ort

    @ort.setter
    def ort(self, ort: Opt[weg.Wegkreuzung]) -> None:
        if self._ort is not None:
            try:
                self._ort.menschen.remove(self)
            except ValueError:
                pass
        self._ort = ort
        if ort is not None:
            if self not in ort.menschen:
                ort.menschen.append(self)

# Vorherige Dialoge, nur str für Name, sonst (name, mindestanzahl)
VorList = List[Union[str, Tuple[str, int]]]


@dataclass
class Malp:
    text: str
    warte: bool = False

    def __call__(self, *__):
        malp(self.text, warte=self.warte)
    
    def __str__(self) -> str:
        return self.text


class Dialog:
    """Ein einzelner Gesprächsfaden beim Gespräch mit einem NSC"""
    wenn_fn: Opt[DialogFn]

    def __init__(self,
                 name: str,
                 text: str,
                 geschichte: DialogGeschichte,
                 vorherige: Union[str, None, VorList] = None,
                 wiederhole: Opt[int] = None,
                 min_freundlich: Opt[int] = None,
                 direkt: bool = False,
                 effekt: Opt[DialogFn] = None,
                 gruppe: Opt[str] = None):
        """
        ```
        Dialog("halloli", "Halloli",
                ["Du bist ein Totenbeschwörer", Malp("Der Mensch weicht zurück")],
               effekt=lambda n,m:m.welt.setze("totenbeschwörer")))
        Dialog("geld", "Gib mir Geld", "Hilfe!", "halloli",
                effekt=lambda n,m: m.erhalte("Gold", n.gold, n))
        ```
        
        :param name: Der kurze Name des Dialogs
        :param text: Der lange Text in der Option
        :param geschichte: Das, was beim Dialog passiert. Kann DialogFn sein
            oder eine Liste von Strings und Malps, die dann gesagt werden.
        :param effekt: Passiert zusätzlich noch nach geschichte.
        :param vorherige: Liste von Dialogen, die schon gesagt sein müssen
        :param min_freundlich: Mindestfreundlichkeit für den Dialog
        :param direkt: Wenn wahr, redet der Mänx dich an, statt du ihn.
        :param gruppe: Nur ein Dialog einer gruppe darf gewählt werden.
        """
        self.direkt = direkt
        self.min_freundlich = min_freundlich
        self.name = name
        self.text = text
        if effekt:
            if callable(geschichte):
                raise TypeError("Geschichte und Effekt dürfen nicht beides "
                                "Funktionen sein.")
            elif isinstance(geschichte, str):
                geschichte = [geschichte]
            self.geschichte: DialogGeschichte = effekt
            self.geschichte_text: Opt[Sequence[Union['Malp', str]]] = geschichte
        else:
            self.geschichte = geschichte
            self.geschichte_text = None
        self.effekt = effekt
        self.vorherige: VorList
        if isinstance(vorherige, str):
            self.vorherige = [vorherige]
        elif vorherige is not None:
            self.vorherige = vorherige
        else:
            self.vorherige = []

        self.gruppe = gruppe
        self.wenn_fn = None
        if wiederhole is None:
            self.anzahl = 1 if direkt else 0
        else:
            self.anzahl = wiederhole

    def wenn(self, fn: DialogFn) -> 'Dialog':
        """Dieser Dialog soll nur aufrufbar sein, wenn die Funktion fn
        erfüllt ist."""
        if self.wenn_fn:
            def neue_wenn(n, m, wf=self.wenn_fn):
                return wf(n, m) and fn(n, m)
            self.wenn_fn = neue_wenn
        else:
            self.wenn_fn = fn
        return self

    def wenn_var(self, *welt_variabeln: str) -> 'Dialog':
        """Dieser Dialog soll nur aufrufbar sein, wenn die Weltvariable
        gesetzt ist."""
        return self.wenn(lambda n, m: all(m.welt.ist(v) for v in welt_variabeln))

    def wiederhole(self, anzahl: int) -> 'Dialog':
        """Füge eine maximale Anzahl von Wiederholungen hinzu"""
        self.anzahl = anzahl
        return self

    def verfügbar(self, nsc: 'NSC', mänx: system.Mänx) -> bool:
        """Prüfe, ob der Dialog als Option verfügbar ist."""
        # Keine Wiederholungen mehr
        if self.anzahl and nsc.dialog_anzahl.get(self.name, 0) >= self.anzahl:
            return False
        # Gruppe
        if self.gruppe and nsc.dialog_anzahl.get(self.gruppe, 0) >= 1:
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
        if (self.min_freundlich is not None and
                nsc.freundlich < self.min_freundlich):
            return False
        if self.wenn_fn:
            return bool(self.wenn_fn(nsc, mänx))
        return True

    def zu_option(self) -> MenuOption['Dialog']:
        return (self.text, self.name, self)


class Dorfbewohner(NSC):
    """Ein NSC, der Hallo sagt und schon eine Kampffunktion hat."""

    def __init__(self, name: str, geschlecht: bool, **kwargs):
        kwargs.setdefault("art", "Dorfbewohner" if geschlecht
                          else "Dorfbewohnerin")
        super().__init__(name, **kwargs)
        self.geschlecht = geschlecht

        def hallo(n, m):
            sprich(n.name, f"Hallo, ich bin {n.name}. "
                   "Freut mich, dich kennenzulernen.")
            return True
        self.dialog("hallo", "Hallo", hallo).wiederhole(1)

        def hallo2(n, m):
            sprich(n.name, f"Hallo nochmal!")
            return True
        self.dialog("hallo2", "Hallo", hallo2, "hallo")

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
            malp("Irgendwann ist dein Gegner bewusstlos.")
            if mänx.ja_nein("Schlägst du weiter bis er tot ist oder gehst du weg?"):
                malp("Irgendwann ist der Arme tot. Du bist ein Mörder. "
                      "Kaltblütig hast du dich dafür entschieden einen lebendigen Menschen zu töten."
                      "", kursiv(" zu ermorden. "), "Mörder.")
            else:
                malp("Du gehst weg.")

        else:
            malp("Diesmal bist du es, der unterliegt.")
            a = random.randint(1, 10)
            if a != 1:
                mint("Als du wieder aufwachst, bist du woanders.")
                gefängnis_von_gäfdah(mänx)


class Ort(weg.Wegkreuzung):
    """Ein Ort im Dorf, wo sich Menschen aufhalten können"""

    def __init__(self,
                 name: str,
                 dorf: Union[None, Dorf, Ort],
                 text: Opt[Sequence[str]] = None,
                 menschen: Opt[List[NSC]] = None):
        """
        ```
        ort = Ort("Taverne Zum Katzenschweif", None, # wird noch hinzugefügt
                  "Eine lebhafte Taverne voller Katzen",
                  [
                      welt.obj("genshin:mond:diona"),
                      welt.obj("genshin:mond:margaret")
                  ])
        ```
        """
        super().__init__(menschen=menschen)
        self.name = name
        if text:
            if isinstance(text, str):
                text = [text]
            self.add_beschreibung(text)
        if isinstance(dorf, Ort):
            self.dorf: Opt[Dorf] = dorf.dorf
        else:
            self.dorf = dorf
        if self.dorf:
            self.dorf.orte.append(self)

    def verbinde(self,
                 anderer: weg.Wegpunkt, richtung: str="",
                 typ: weg.Wegtyp=weg.Wegtyp.WEG, ziel: str=""):
        if isinstance(anderer, Ort) and not richtung:
            anderer.nachbarn[self.name] = weg.Richtung(self)
            self.nachbarn[anderer.name] = weg.Richtung(anderer)
        else:
            super().verbinde(anderer, richtung=richtung, typ=typ, ziel=ziel)

    def add_nsc(self, welt: Welt, name: str, fkt: Callable[..., NSC],
                *args, **kwargs):
        welt.get_or_else(name, fkt, *args, **kwargs).ort = self

    def __repr__(self):
        if self.dorf:
            return f"Ort {self.name} von {self.dorf.name}"
        else:
            return f"Ort {self.name}, Teil keines Dorfes"


class Dorf:
    """Ein Dorf besteht aus mehreren Orten, an denen man Menschen treffen kann.
    Es gibt einen Standard-Ort, nämlich "draußen".
    """

    def __init__(self, name: str, orte: Opt[List[Ort]] = None) -> None:
        if orte:
            self.orte = orte
        else:
            self.orte = []
            Ort("draußen", self, "Du bist draußen.")
        self.name = name

    def main(self, mänx) -> None:
        malp(f"Du bist in {self.name}. Möchtest du einen der Orte betreten oder "
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
        ort.beschreibe(mänx, None)
        if ort.menschen:
            malp("Hier sind:")
            for mensch in ort.menschen:
                malp(f"{mensch.name}, {mensch.art}")
        else:
            malp("Hier ist niemand.")
        optionen: List[MenuOption[Union[NSC, Ort, None]]]
        optionen = [("Mit " + mensch.name + " reden", mensch.name.lower(),
                     mensch) for mensch in ort.menschen]
        optionen.extend((f"Nach {o.name} gehen", o.name.lower(), o)
                        for o in self.orte if o != ort)
        optionen.append(("Ort verlassen", "fliehen", None))
        opt = mänx.menu(optionen)
        if isinstance(opt, NSC):
            opt.main(mänx)
            return ort
        else:
            return opt
