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
import yaml
import pathlib
from enum import Enum, EnumMeta, auto
from attrs import define, field
from typing import Dict, Optional as Opt, List, DefaultDict

__author__ = "jasper"


def get_items(name: str) -> list[str]:
    with open((pathlib.Path(__file__).absolute().parents[0] / "enums.yaml"), "r") as file:
        docs = yaml.safe_load_all(file)
        for doc in docs:
            if doc["doc_name"] == name:
                return doc["Enums"]


ItemKlasse: EnumMeta = Enum("ItemKlasse", get_items("ItemKlasse"))


class Effekt(Enum):
    Verfluchen = auto()
    Selbstentwaffnung = auto()
    Blocken = auto()
    Selbstverwirrung = auto()
    Entflammung = auto()


@define
class Fähigkeit:
    """ Attacken/Fähigkeiten, die ein Item im Kampf haben kann"""
    name: str
    schaden: int
    mana: int = 0
    stamina: int = 0
    abklingzeit: int = 1
    effekte: list[Effekt] = field(factory=list)

    def add_effekt(self, effekt: str):
        self.effekte.append(Effekt[effekt])

    def set_mana(self, mana: int):
        self.mana = mana

    def set_stamina(self, stamina: int):
        self.stamina = stamina

    def set_abklingzeit(self, abklingzeit: int):
        self.abklingzeit = abklingzeit


@define
class Item:
    """ Alle Items, die eine Figur im Inventar haben kann"""
    name: str
    gold: int
    beschreibung: str = field(default="?")
    item_typ: list[ItemKlasse] = field(factory=list)
    stapelbar: bool = field(default=True)
    fähigkeiten: list[Fähigkeit] = field(factory=list)

    def __str__(self):
        return "{} [{}]".format(self.name, self.item_typ[0].name)

    def __format__(self, format_spec):
        return format(str(self), format_spec)

    def get_preis(self):
        return self.gold

    def yield_classes(self):
        return iter(self.item_typ)

    def add_fähigkeit(self, fähigkeit: Fähigkeit):
        self.fähigkeiten.append(fähigkeit)

    def add_typ(self, klasse: str):
        self.item_typ.append(ItemKlasse[klasse])


def lade_itemverzeichnis(pfad: str | PathLike, waffenpfad: str | PathLike) -> dict[str, Item]:
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
    item_verzeichnis = {}
    for item_name, item_class in items.items():
        item = Item(name=item_name, gold=(preise[item_name] if item_name in preise else 0))
        item.add_typ(item_class)
        if item_class in classes:
            item.add_typ(classes[item_class])
        item_verzeichnis[item_name] = item

    with open(waffenpfad, "r") as file:
        doc = yaml.safe_load(file)
        for name, attacken in doc.items():
            if name in item_verzeichnis:
                waffe = item_verzeichnis[name]
                for attacke in attacken:
                    fähigkeit = Fähigkeit(name=attacke["name"], schaden=attacke["Schaden"])
                    for stat in attacke:
                        match stat.lower():
                            case "mana":
                                fähigkeit.set_mana(attacke[stat])
                            case "stamina":
                                fähigkeit.set_stamina(attacke[stat])
                            case "abklingzeit":
                                fähigkeit.set_abklingzeit(attacke[stat])
                            case "effekte":
                                for effekt in attacke[stat]:
                                    fähigkeit.add_effekt(effekt)
                    waffe.add_fähigkeit(fähigkeit)

    return item_verzeichnis


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

    verzeichnis = pathlib.Path(__file__).absolute().parents[1] / "itemverzeichnis.txt"
    waffenverzeichnis = pathlib.Path(__file__).absolute().parents[1] / 'waffenverzeichnis.yaml'

    lade_itemverzeichnis(verzeichnis, waffenverzeichnis)
    if not verzeichnis.exists():
        raise OSError("Itemverzeichnis nicht da, wo erwartet:", verzeichnis)

    # def main():
    #     locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    #     schreibe_itemverzeichnis(
    #         verzeichnis, system.ITEMVERZEICHNIS, system.UNTERKLASSEN, system.ALLGEMEINE_PREISE)
    #     items, klassen, preise = lade_itemverzeichnis(verzeichnis)
    #     assert items == system.ITEMVERZEICHNIS
    #     assert klassen == system.UNTERKLASSEN
    #     assert preise == system.ALLGEMEINE_PREISE
    #
    #
    # main()
