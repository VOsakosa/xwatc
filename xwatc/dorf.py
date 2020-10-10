"""
Xwatc' Ort- und Menschensystem.

Seit 10.10.2020
"""
from typing import List, Dict
from typing import Optional as Opt
from dataclasses import dataclass, field
from xwatc.system import mint, schiebe_inventar, Spielende
from xwatc import system
from collections import defaultdict
__author__ = "jasper"


@dataclass
class NSC:
    # TODO inventar base
    name: str
    art: str
    inventar: Dict[str, int] = field(
        default_factory=lambda: defaultdict(lambda: 0))

    def kampf(self, mänx) -> None:
        if mänx.hat_klasse("Waffe", "magische Waffe"):
            mint("Du streckst den armen Typen nieder.")
            schiebe_inventar(self.inventar, mänx.inventar)
        elif self.hat_klasse("Waffe", "magische Waffe"):
            # TODO Geschlecht
            mint(f"Du rennst auf {self.name} zu und schlägst wie wild auf sie ein.")
            if "Dolch" in self.inventar:
                mint("Aber sie zieht seinen Dolch und sticht dich nieder")
                raise Spielende
        else:
            mint("Ihr schlagt euch, bis ihr nicht mehr könnt.")

    def hat_klasse(self, *klassen) -> bool:
        """Prüfe, ob mänx item aus einer der Klassen besitzt."""
        for item in self.inventar:
            if system.get_class(item) in klassen:
                return True
        return False


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
        return None
        
            
