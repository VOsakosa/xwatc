"""
Klassen, die Eingaben modellieren.
Created on 16.04.2023
"""
from xwatc import _
from attr import define, field
from collections.abc import Mapping, Sequence
from typing import Generic, TypeVar
from typing import Any  # @UnusedImport
from typing_extensions import TypeAlias
__author__ = "jasper"

Tcov = TypeVar("Tcov", covariant=True)
T = TypeVar("T")
MenuOption: TypeAlias = tuple[str, str, Tcov]


def Option(name: str, wert: T) -> MenuOption[T]:
    """Eine Option für das Menü. Der erste Teil ist ein Name und wird automatisch übersetzt.
    Ended der Name auf einen Text in eckigen Klammern, so wird dieser als Shortcut genutzt."""
    name, __, short = _(name).rpartition("[")
    if short:
        short = short.removesuffix("]")
    else:
        short = name.split()[0].lower()
    return name, short, wert


@define
class Menu(Generic[Tcov]):
    """Repräsentiert ein Menu."""
    optionen: Sequence[MenuOption[Tcov]]
    frage: str = ""
    versteckt: Mapping[str, Tcov] = field(factory=dict)

    @classmethod
    def ja_nein(cls: "type[Menu[T]] | type[Menu[Any]]", ja: T, nein: T, frage: str = ""
                ) -> "Menu[T]":
        return cls([
            (_("Ja"), _("ja"), ja),
            (_("Nein"), _("nein"), nein)
        ], frage=frage)

    @classmethod
    def ja_nein_bool(cls: "type[Menu[bool]] | type[Menu[Any]]", frage: str = "") -> "Menu[bool]":
        return cls.ja_nein(True, False, frage)

    @classmethod
    def minput(cls: 'type[Menu[str]] | type[Menu[Any]]', options: Sequence[str], frage: str = ""
               ) -> 'Menu[str]':
        assert options, "Leere Menge an Optionen"
        return cls([(option, option.lower(), option.lower()) for option in options], frage=frage)


@define
class FreeInput:
    """Repräsentiert eine Ausgabe ohne Einschränkungen."""
    frage: str
