"""
Xwatc' Ort- und Menschensystem.

Seit 10.10.2020
"""
from typing import List, Union, Callable, Dict, Tuple
from typing import Optional as Opt
from dataclasses import dataclass, field
from xwatc.system import mint, schiebe_inventar, Spielende, MenuOption, sprich
from xwatc import system
__author__ = "jasper"

NSCOptionen = List[MenuOption[Callable[[system.Mänx], None]]]
DialogFn = Callable[["NSC", system.Mänx], Opt[bool]]


class NSC(system.InventarBasis):
    name: str
    art: str

    def __init__(self, name: str, art: str, kampfdialog: Opt[DialogFn] = None,
                 fliehen: Opt[Callable[[system.Mänx], None]] = None):
        super().__init__()
        self.name = name
        self.art = art
        self.kennt_spieler = False
        self.tot = False
        self.kampf_fn = kampfdialog
        self.dialoge: List[Dialog] = []
        self.dialog_anzahl: Dict[str, int] = {}
        if fliehen:
            self.fliehen = fliehen  # type: ignore

    def kampf(self, mänx: system.Mänx) -> None:
        raise ValueError(f"Xwatc weiß nicht, wie {self.name} kämpft")

    def fliehen(self, _mänx: system.Mänx) -> None:  # pylint: disable=method-hidden
        mint("Du entkommst mühelos.")

    def optionen(self, _mänx: system.Mänx) -> NSCOptionen:
        return [("kämpfen", "k", self.kampf),
                ("reden", "r", self.reden),
                ("fliehen", "f", self.fliehen)]

    def main(self, mänx: system.Mänx) -> None:
        if self.tot:
            mint(f"{self.name}s Leiche liegt still auf dem Boden.")
        else:
            opts = self.optionen(mänx)
            mänx.menu(":", opts)(mänx)

    def sprich(self, text) -> None:
        system.sprich(self.name, text)

    def reden(self, mänx: system.Mänx) -> None:
        dlg_anzahl = self.dialog_anzahl
        cont = True
        start = True
        while cont:
            optionen: List[MenuOption[Opt[Dialog]]]
            optionen = [d.zu_option() for d in self.dialoge
                        if d.verfügbar(self, mänx)]
            if not optionen:
                if start:
                    print("Du weißt nicht, was du könntest.")
                else:
                    print("Du hast nichts mehr zu sagen.")
            optionen.append(("fliehen", "f", None))
            dlg: Opt[Dialog] = mänx.menu("", optionen)
            if not dlg:
                cont = False
            else:
                cont = bool(dlg.geschichte(self, mänx))
                dlg_anzahl[dlg.name] = dlg_anzahl.setdefault(dlg.name, 0) + 1
            start = False

    def dialog(self, *args, **kwargs) -> Dialog:
        "Erstelle einen Dialog"
        dia = Dialog(*args, **kwargs)
        self.dialoge.append(dia)
        return dia


class Dialog:
    """Ein einzelner Gesprächsfaden beim Gespräch mit einem NSC"""
    wenn_fn: Opt[DialogFn]

    def __init__(self, name: str, text: str, geschichte: DialogFn,
                 vorherige: Union[str, None, List[Union[str, Tuple[str, int]]]] = None):
        self.name = name
        self.text = text
        self.geschichte = geschichte
        if vorherige is not None:
            self.vorherige = vorherige
        elif isinstance(vorherige, str):
            self.vorherige = list(vorherige)
        else:
            self.vorherige = []

        self.wenn_fn = None
        self.anzahl = 0

    def wenn(self, fn: DialogFn) -> 'Dialog':
        self.wenn_fn = fn
        return self

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
    def __init__(self, name: str, geschlecht: bool):
        super().__init__(name, "Dorfbewohner" if geschlecht
                         else "Dorfbewohnerin")
        self.geschlecht = geschlecht
        self.dialog("hallo", "Hallo", lambda n, _: 
                    sprich(n.name, f"Hallo, ich bin {n.name}. "
                   "Freut mich, dich kennenzulernen.")).wiederhole(1)
        self.dialog("hallo2", "Hallo", lambda n, _:
                    sprich(n.name, "Hallo nochmal!"), "hallo")

    def kampf(self, mänx: system.Mänx) -> None:
        if mänx.hat_klasse("Waffe", "magische Waffe"):
            mint("Du streckst den armen Typen nieder.")
            schiebe_inventar(self.inventar, mänx.inventar)
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
                    mint("Aber er wehrt sich.")
                else:
                    mint("Aber sie wehrt sich.")
                raise Spielende
        else:
            mint("Ihr schlagt euch, bis ihr nicht mehr könnt.")

@dataclass
class Ort:
    """Ein Ort im Dorf, wo sich Menschen aufhalten können"""
    name: str
    menschen: List[NSC] = field(default_factory=list)

    def platzangabe(self):
        if self.name == "Draußen":
            print("Du bist draußen.")
        else:
            # TODO Genus
            print("Du bist im {self.name}.")


class Dorf:
    """Ein Dorf besteht aus mehreren Orten, an denen man Menschen treffen kann.
    Es gibt einen Standard-Ort, nämlich "draußen".
    """

    def __init__(self, name: str, orte: Opt[List[Ort]] = None) -> None:
        if orte:
            self.orte = orte
        else:
            self.orte = [Ort("Draußen")]
        self.name = name

    def main(self, mänx) -> None:
        print(f"Du bist in {self.name}. Möchtest du einen der Orte betreten oder "
              "draußen bleiben?")
        orte: List[MenuOption[Opt[Ort]]]
        orte = [(ort.name, ort.name.lower(), ort) for ort in self.orte]
        orte.append(("Bleiben", "", self.orte[0]))
        orte.append((f"{self.name} verlassen", "v", None))
        loc = mänx.menu("Wohin? ", orte)
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
        opt = mänx.menu("Was machst du?", optionen)
        if isinstance(opt, NSC):
            opt.main(mänx)
            return ort
        else:
            return opt
