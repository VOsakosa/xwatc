"""
Schreibt und liest das Xwatc-Itemverzeichnis.

Die Grammatik des Itemverzeichnisses ist wie folgt:
(Die Grammatik ignoriert Whitespace, Kommentarzeilen mit #)

ITEMVERZEICHNIS := KLASSENBLOCK*
KLASSENBLOCK := KLASSENDEFINITION ITEMDEFINITION*
KLASSENDEFINITION := NAME ":" NAME@OBERKLASSE?
ITEMDEFINITION := NAME (";" KOSTEN )?
KOSTEN := INTEGER | "-"
NAME := "[\w ]+"


Created on 25.10.2020
"""
from __future__ import annotations
import locale
from os import PathLike
from collections import defaultdict
import re
from typing import Tuple, Dict, Optional as Opt, List, DefaultDict

__author__ = "jasper"


def lade_itemverzeichnis(pfad: str | PathLike) -> Tuple[Dict[str, str], Dict[str, str],
                                                        Dict[str, int]]:
    """Lädt das Itemverzeichnis bei Pfad."""
    items = {}
    classes = {}
    preise = {}
    klasse: Opt[str] = None
    with open(pfad, "r") as file:
        for lineno, line in enumerate(file):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            splits = re.split(r"\s*:\s*", line)
            if len(splits) == 1:
                # Item
                if klasse:
                    item, *fields = re.split("\s*;\s*", splits[0])
                    items[item] = klasse
                    if fields:
                        try:
                            if fields[0] != "-":
                                preise[item] = int(fields[0])
                        except ValueError:
                            raise ValueError("Die erste Spalte ist der Preis, "
                                             f"war aber {fields[0]}") from None
                else:
                    raise ValueError(f"{item} sollte zu einer Klasse gehören!",
                                     lineno)
            elif len(splits) == 2:
                # Klassendefinition
                klasse, ober = splits
                if ober:
                    classes[klasse] = ober
            else:
                raise ValueError(f"Mehrere Doppelpunkte in einer Linie: {line}",
                                 lineno)
    return items, classes, preise


def schreibe_itemverzeichnis(pfad, items: Dict[str, str],
                             classes: Dict[str, str],
                             preise: dict[str, int]) -> None:
    """Schreibe das Itemverzeichnis, schön sortiert, in die Datei pfad"""
    klassen: DefaultDict[str, List[str]] = defaultdict(list)
    for unter, ober in classes.items():
        klassen[unter]  # pylint: disable=pointless-statement
    for item, klasse in items.items():
        klassen[klasse].append(item)

    with open(pfad, "w") as file:
        file.write("# Xwatc-Itemverzeichnis\n\n")
        for klasse, item_liste in sorted(klassen.items(),
                                         key=lambda a: locale.strxfrm(a[0])):
            item_liste.sort(key=locale.strxfrm)
            file.write(klasse)
            file.write(":")
            oberk = classes.get(klasse)
            if oberk:
                print(f" {oberk}", file=file)
            else:
                print(file=file)
            for item in item_liste:
                print("  ", item, sep="", file=file, end="")
                if item in preise:
                    print(";", preise[item], end="", file=file)
                print(file=file)
            print(file=file)


if __name__ == '__main__':
    if not __package__:
        __package__ = "xwatc.untersystem.itemverzeichnis"  # pylint: disable=redefined-builtin
    from xwatc import system
    import pathlib
    verzeichnis = pathlib.Path(__file__).absolute(
    ).parents[1] / "itemverzeichnis.txt"
    if not verzeichnis.exists():
        raise OSError("Itemverzeichnis nicht da, wo erwartet:", verzeichnis)

    def main():
        locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
        schreibe_itemverzeichnis(
            verzeichnis, system.ITEMVERZEICHNIS, system.UNTERKLASSEN, system.ALLGEMEINE_PREISE)
        items, klassen, preise = lade_itemverzeichnis(verzeichnis)
        assert items == system.ITEMVERZEICHNIS
        assert klassen == system.UNTERKLASSEN
        assert preise == system.ALLGEMEINE_PREISE
    main()
