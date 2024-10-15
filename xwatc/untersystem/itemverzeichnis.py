r"""
Schreibt und liest das Xwatc-Itemverzeichnis.
"""
from __future__ import annotations
from collections.abc import Collection, Iterator, Sequence
import locale
from os import PathLike
from collections import defaultdict
import re
import yaml
import pathlib
from enum import Enum, EnumMeta, auto
from attrs import astuple, define, field
from typing import Any, DefaultDict, TypeAlias, assert_never

__author__ = "jasper"


def get_items(name: str) -> list[str]:
    with open((pathlib.Path(__file__).absolute().parents[0] / "enums.yaml"), "r") as file:
        docs = yaml.safe_load_all(file)
        for doc in docs:
            if doc["doc_name"] == name:
                return doc["Enums"]
    raise RuntimeError(f"enums.yaml did not contain Enum {name}")


ItemKlasse: EnumMeta = Enum("ItemKlasse", get_items("ItemKlasse"))  # type: ignore


class Ausrüstungsort(Enum):
    """Der Körperteil, an dem eine Ausrüstung getragen wird."""
    KOPF = auto()
    OBEN = auto()
    UNTEN = auto()
    OBENUNTEN = auto()
    FUSS = auto()
    HAND = auto()
    HALS = auto()


class Ausrüstungsdicke(Enum):
    """Wie eng anliegend Kleidung ist. Kleidung, die unterschiedlich eng ist, kann übereinander
    getragen werden."""
    ANLIEGEND = auto()
    INNEN = auto()
    AUSSEN = auto()
    RÜSTUNG = auto()
    FLATTERN = auto()
    ACCESSOIRE = auto()  # davon kann man mehrere haben!


@define(frozen=True)
class Kleidungsslot:
    """Ein bestimmter Typ von Kleidung, festgelegt durch Ort und Dicke."""
    ort: Ausrüstungsort
    dicke: Ausrüstungsdicke

    def as_tuple(self) -> tuple[Ausrüstungsort, Ausrüstungsdicke]:
        return astuple(self)

    def __str__(self) -> str:
        return self.ort.name.lower() + " " + self.dicke.name.lower()

    def conflicting(self) -> Collection[Kleidungsslot]:
        """Die Liste von Kleidungsslots, die mit diesem kollidieren."""
        if self.dicke == Ausrüstungsdicke.ACCESSOIRE:
            return ()
        if self.ort in (Ausrüstungsort.OBEN, Ausrüstungsort.UNTEN):
            return (self, Kleidungsslot(Ausrüstungsort.OBENUNTEN, self.dicke))
        elif self.ort == Ausrüstungsort.OBENUNTEN:
            return (self,
                    Kleidungsslot(Ausrüstungsort.OBEN, self.dicke),
                    Kleidungsslot(Ausrüstungsort.UNTEN, self.dicke))
        return (self,)


class Waffenhand(Enum):
    """In welcher Hand die Waffe gehalten wird. (nur Haupt- und Nebenhand kollidieren nicht)"""
    HAUPTHAND = 1
    NEBENHAND = 2
    BEIDHÄNDIG = 3

    def conflicting(self) -> Collection[Waffenhand]:
        """Die Liste von Waffenhänden, die mit dieser kollidieren
        (nur Haupt- und Nebenhand kollidieren nicht)"""
        if self == Waffenhand.BEIDHÄNDIG:
            return list(Waffenhand)
        elif self == Waffenhand.NEBENHAND:
            return (Waffenhand.BEIDHÄNDIG, Waffenhand.NEBENHAND)
        elif self == Waffenhand.HAUPTHAND:
            return (Waffenhand.BEIDHÄNDIG, Waffenhand.HAUPTHAND)
        assert_never(self)


Ausrüstungstyp: TypeAlias = Waffenhand | Kleidungsslot


def parse_ausrüstungstyp(name: str) -> Ausrüstungstyp:
    """Parse einen Ausrüstungstyp aus einem String.

    >>> parse_ausrüstungstyp("nebenhand")
    <Waffenhand.NEBENHAND: 2>
    >>> parse_ausrüstungstyp("oben anliegend")
    Kleidungsslot(ort=<Ausrüstungsort.OBEN: 2>, dicke=<Ausrüstungsdicke.ANLIEGEND: 1>)
    """
    name = name.upper()
    try:
        return Waffenhand[name]
    except KeyError:
        pass
    name1, name2 = name.split()
    return Kleidungsslot(Ausrüstungsort[name1], Ausrüstungsdicke[name2])


@define
class Item:
    """ Alle Items, die eine Figur im Inventar haben kann"""
    name: str
    gold: int
    beschreibung: str = field(default="?")
    item_typ: 'list[ItemKlasse]' = field(factory=list)  # type: ignore
    stapelbar: bool = field(default=True)
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
            kwargs["beschreibung"] = dct.pop("beschreibung")
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

    def add_typ(self, klasse: str) -> None:
        self.item_typ.append(ItemKlasse[klasse])


def _lade_item(item_dict: str | dict[str, Any], klassen_name: str, common: dict[str, Any]) -> Item:
    """Lade ein Item aus seiner Serialisierung.

    >>> _lade_item("Hose;12", "Kleidung", {}) # doctest: +ELLIPSIS
    Item(name='Hose', gold=12, beschreibung='?', item_typ=[<ItemKlasse.Kleidung:...>], ...)
    """
    if isinstance(item_dict, str):
        item_name, *fields = re.split(r"\s*;\s*", item_dict)
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
    return item_obj


def lade_itemverzeichnis(pfad: str | PathLike) -> dict[str, Item]:
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
            item_obj = _lade_item(item_dict, klassen_name, common)
            item_verzeichnis[item_obj.name] = item_obj

    for item_obj in item_verzeichnis.values():
        item_class = item_obj.item_typ[0].name
        while item_class in classes:
            item_class = classes[item_class]
            item_obj.add_typ(item_class)

            # for attacke in attacken:
            #     fähigkeit = Fertigkeit(name=attacke["name"], schaden=attacke["Schaden"])
            #     for stat in attacke:
            #         match stat.lower():
            #             case "mana":
            #                 fähigkeit.set_mana(attacke[stat])
            #             case "stamina":
            #                 fähigkeit.set_stamina(attacke[stat])
            #             case "abklingzeit":
            #                 fähigkeit.set_abklingzeit(attacke[stat])
            #             case "effekte":
            #                 for effekt in attacke[stat]:
            #                     fähigkeit.add_effekt(effekt)
            #     waffe.add_fähigkeit(fähigkeit)

    return item_verzeichnis


def schreibe_itemverzeichnis(pfad, items: dict[str, str],
                             classes: dict[str, str],
                             preise: dict[str, int]) -> None:
    """Schreibe das Itemverzeichnis, schön sortiert, in die Datei pfad"""
    klassen: DefaultDict[str, list[str]] = defaultdict(list)
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

    lade_itemverzeichnis(verzeichnis)
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
