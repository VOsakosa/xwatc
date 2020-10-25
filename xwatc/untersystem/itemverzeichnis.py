"""
Schreibt und liest das Xwatc-Itemverzeichnis.


Created on 25.10.2020
"""
__author__ = "jasper"
from collections import defaultdict
import re
from typing import Tuple, Dict, Optional as Opt, List, DefaultDict


def lade_itemverzeichnis(pfad) -> Tuple[Dict[str, str], Dict[str, str]]:
    items = {}
    classes = {}
    klasse: Opt[str] = None
    with open(pfad, "r") as file:
        for lineno, line in enumerate(file):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            splits = re.split(r"\s*:\s*", line)
            if len(splits) == 1:
                # Item
                item = splits[0]
                if klasse:
                    items[item] = klasse
                else:
                    raise ValueError(f"{item} sollte zu einer Klasse gehören!",
                                     lineno)
            elif len(splits) == 2:
                klasse, ober = splits
                if ober:
                    classes[klasse] = ober
            else:
                raise ValueError(f"Drei Doppelpunkte in einer Linie: {line}",
                                 lineno)
    return items, classes


def schreibe_itemverzeichnis(pfad, items: Dict[str, str],
                             classes: Dict[str, str]) -> None:
    """Schreibe das Itemverzeichnis, schön sortiert, in die Datei pfad"""
    klassen: DefaultDict[str, List[str]] = defaultdict(list)
    for unter, ober in classes.items():
        klassen[unter]  # pylint: disable=pointless-statement
        klassen[ober]  # pylint: disable=pointless-statement
    for item, klasse in items.items():
        klassen[klasse].append(item)

    with open(pfad, "w") as file:
        file.write("# Xwatc-Itemverzeichnis\n\n")
        for klasse, item_liste in sorted(klassen.items()):
            item_liste.sort()
            print(klasse, ":", file=file, end="", sep="")
            oberk = classes.get(klasse)
            if oberk:
                print(f" {oberk}", file=file)
            else:
                print(file=file)
            for item in item_liste:
                print("  ", item, sep="", file=file)
            print(file=file)




if __name__ == '__main__':
    if not __package__:
        __package__ = "xwatc.untersystem.itemverzeichnis"  #pylint: disable=redefined-builtin
    from xwatc import system
    import pathlib
    verzeichnis = pathlib.Path(__file__).absolute(
    ).parents[1] / "itemverzeichnis.txt"
    if not verzeichnis.exists():
        raise OSError("Itemverzeichnis nicht da, wo erwartet:", verzeichnis)
    def main():
        schreibe_itemverzeichnis(
            verzeichnis, system.ITEMVERZEICHNIS, system.UNTERKLASSEN)
        items, klassen = lade_itemverzeichnis(verzeichnis)
        assert items == system.ITEMVERZEICHNIS
        assert klassen == system.UNTERKLASSEN
    main()
