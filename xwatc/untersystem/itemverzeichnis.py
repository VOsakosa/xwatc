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
from collections.abc import Iterator, Sequence
import locale
from os import PathLike
from collections import defaultdict
import re
import yaml
import pathlib
from enum import Enum, EnumMeta, auto
from attrs import define, field
from typing import Any, Dict, Optional as Opt, List, DefaultDict, Self

__author__ = "jasper"


def get_items(name: str) -> list[str]:
    with open((pathlib.Path(__file__).absolute().parents[0] / "enums.yaml"), "r") as file:
        docs = yaml.safe_load_all(file)
        for doc in docs:
            if doc["doc_name"] == name:
                return doc["Enums"]
    raise RuntimeError(f"enums.yaml did not contain Enum {name}")


ItemKlasse: EnumMeta = Enum("ItemKlasse", get_items("ItemKlasse"))  # type: ignore


class Ausrüstungsslot(Enum):
    KOPF = auto()
    OBEN = auto()
    UNTEN = auto()
    OBENUNTEN = auto()
    FUSS = auto()
    HAND = auto()
    HALS = auto()


class Ausrüstungsdicke(Enum):
    ANLIEGEND = auto()
    INNEN = auto()
    AUSSEN = auto()
    RÜSTUNG = auto()
    FLATTERN = auto()
    ACCESSOIRE = auto()  # davon kann man mehrere haben!


class Waffenhand(Enum):
    HAUPTHAND = 1
    NEBENHAND = 2
    BEIDHÄNDIG = 3


Ausrüstungstyp = Waffenhand | tuple[Ausrüstungsslot, Ausrüstungsdicke]


def parse_ausrüstungstyp(name: str) -> Ausrüstungstyp:
    name = name.upper()
    try:
        return Waffenhand[name]
    except KeyError:
        pass
    name1, name2 = name.split()
    return Ausrüstungsslot[name1], Ausrüstungsdicke[name2]


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
    item_typ: 'list[ItemKlasse]' = field(factory=list)  # type: ignore
    stapelbar: bool = field(default=True)
    fähigkeiten: list[Fähigkeit] = field(factory=list)
    ausrüstungsklasse: None | Ausrüstungstyp = field(default=None)

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> 'Item':
        name = dct.pop("name")
        gold = dct.pop("preis", 0)
        kwargs = {}
        if "ausrüstungsklasse" in dct:
            raise TypeError(f"Item {name}: ausrüstungsklasse darf nicht gegeben werden.")
        if "ausrüstung" in dct:
            kwargs["ausrüstungsklasse"] = parse_ausrüstungstyp(dct.pop("ausrüstung"))
        if "beschreibung" in dct:
            kwargs["beschreibung"] = dct["beschreibung"]
        if dct:
            raise TypeError("Unknown keys left")
        return Item(name, gold, **kwargs)  # type: ignore

    def __str__(self) -> str:
        return "{} [{}]".format(self.name, self.item_typ[0].name)

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)

    def get_preis(self) -> int:
        return self.gold

    def yield_classes(self) -> Iterator[ItemKlasse]:
        return iter(self.item_typ)

    def add_fähigkeit(self, fähigkeit: Fähigkeit) -> None:
        self.fähigkeiten.append(fähigkeit)

    def add_typ(self, klasse: str) -> None:
        self.item_typ.append(ItemKlasse[klasse])


def lade_itemverzeichnis(pfad: str | PathLike, waffenpfad: str | PathLike) -> dict[str, Item]:
    """Lädt das Itemverzeichnis bei Pfad."""
    with open(pfad, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    item_verzeichnis: dict[str, Item] = {}
    classes: dict[str, str] = {}
    for klassen_name, items in data.items():
        if isinstance(items[0], dict) and not hasattr(items[0], "name"):  # Class data
            klasse: dict = items[0]
            if "parent" in klasse:
                classes[klassen_name] = klasse.pop("parent")
            start = 1
            common: dict[str, Any] = klasse.get("common") or {}
        else:
            common = {}
            start = 0
        for item_dict in items[start:]:
            if isinstance(item_dict, str):
                item_name, *fields = re.split("\s*;\s*", item_dict)
                if len(fields) > 1:
                    raise ValueError(f"Unerwartet viele Semikolons für {item_name}")
                if fields and fields[0] != "-":
                    preis = int(fields[0])
                else:
                    preis = 0
                item_obj = Item.from_dict(common | {"name": item_name, "preis": preis})
            elif isinstance(item_dict, dict):
                item_obj = Item.from_dict(common | item_dict)
            else:
                raise ValueError(f"Unerwarteter Typ als Item in {klassen_name}")
            item_obj.add_typ(klassen_name)
            item_verzeichnis[item_obj.name] = item_obj

    for item_obj in item_verzeichnis.values():
        item_class = item_obj.item_typ[0].name
        while item_class in classes:
            item_class = classes[item_class]
            item_obj.add_typ(item_class)

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

    verzeichnis = pathlib.Path(__file__).absolute().parents[1] / "itemverzeichnis.yaml"
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
