"""
Klassen, die Eingaben modellieren.
Created on 16.04.2023
"""
from xwatc import _
from attr import define, field, validators
from collections.abc import Mapping, Sequence
from typing import Generic, TypeVar
from typing_extensions import TypeAlias
__author__ = "jasper"

Tcov = TypeVar("Tcov", covariant=True)
T = TypeVar("T")
MenuOption: TypeAlias = tuple[str, str, Tcov]


@define
class Menu(Generic[Tcov]):
    """Repräsentiert ein Menu."""
    optionen: Sequence[MenuOption[Tcov]] = field(validator=validators.min_len(1))
    frage: str = ""
    versteckt: Mapping[str, Tcov] = field(factory=dict)

    @classmethod
    def ja_nein(cls: "type[Menu[T]]", ja: T, nein: T, frage: str = "") -> "Menu[T]":
        return cls([
            (_("Ja"), _("ja"), ja),
            (_("Nein"), _("nein"), nein)
        ], frage=frage)

    @classmethod
    def ja_nein_bool(cls: "type[Menu[bool]]", frage: str = "") -> "Menu[bool]":
        return cls.ja_nein(True, False, frage)

    @classmethod
    def minput(cls: 'type[Menu[str]]', options: Sequence[str], frage: str = "") -> 'Menu[str]':
        assert options, "Leere Menge an Optionen"
        return cls([(option, option.lower(), option.lower()) for option in options], frage=frage)

@define
class FreeInput:
    """Repräsentiert eine Ausgabe ohne Einschränkungen."""
    frage: str