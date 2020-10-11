"""
Xwatc' Ort- und Menschensystem.

Seit 10.10.2020
"""
from typing import List, Union, Callable
from typing import Optional as Opt
from dataclasses import dataclass, field
from xwatc.system import mint, schiebe_inventar, Spielende, MenuOption, sprich
from xwatc import system
from abc import ABC, abstractmethod
__author__ = "jasper"

NSCOptionen = List[MenuOption[Callable[[system.Mänx], None]]]


class NSC(ABC, system.InventarBasis):
    name: str
    art: str

    def __init__(self, name: str, art: str):
        super().__init__()
        self.name = name
        self.art = art
        self.kennt_spieler = False

    @abstractmethod
    def kampf(self, mänx: system.Mänx) -> None:
        pass

    @abstractmethod
    def optionen(self, mänx: system.Mänx) -> NSCOptionen:
        return [("kämpfen", "k", self.kampf)]

    def main(self, mänx: system.Mänx) -> None:
        opts = self.optionen(mänx)
        mänx.menu(":", opts)(mänx)


class Dorfbewohner(NSC):
    def __init__(self, name: str, geschlecht: bool):
        super().__init__(name, "Dorfbewohner" if geschlecht
                         else "Dorfbewohnerin")
        self.geschlecht = geschlecht

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

    def reden(self, _mänx: system.Mänx) -> None:
        if not self.kennt_spieler:
            sprich(self.name, f"Hallo, ich bin {self.name}. "
                   "Freut mich, dich kennenzulernen.")
            self.kennt_spieler = True
        else:
            sprich(self.name, "Hallo wieder.")

    def optionen(self, mänx: system.Mänx) -> NSCOptionen:
        ans = super().optionen(mänx)
        ans.append(("reden", "r", self.reden))
        return ans


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

    def main(self, mänx):
        print(f"Du bist in {self.name}. Möchtest du einen der Orte betreten oder "
              "draußen bleiben?")
        for ort in self.orte:
            print(ort.name)
        orte = [(ort.name, ort.name.lower(), ort) for ort in self.orte]
        orte.append("Bleiben", "", self.orte[0])
        orte.append(f"{self.name} verlassen", "v", None)
        loc = mänx.menu("Wohin? ", orte)
        while loc:
            loc = self.ort_main(mänx, loc)

    def ort_main(self, mänx, ort: Ort) -> Opt[Ort]:
        if ort.menschen:
            print("Hier sind:")
            for mensch in ort.menschen:
                print(f"{mensch.name}, {mensch.art}")
        else:
            print("Hier ist niemand.")
        optionen: List[MenuOption[Union[NSC, Ort, None]]]
        optionen = [("Mit " + mensch.name + " reden", "r" + mensch.name.lower(),
                     mensch) for mensch in ort.menschen]
        optionen.extend((f"Nach {ort.name} gehen", "o" + ort.name.lower(), ort)
                        for ort in self.orte)
        optionen.append(("Ort verlassen", "fliehen", None))
        opt = mänx.menu("Was machst du?", optionen)
        if isinstance(opt, NSC):
            opt.main(mänx)
            return ort
        else:
            return opt
