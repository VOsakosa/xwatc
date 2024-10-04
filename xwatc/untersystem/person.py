"""
Verschiedene Eigenschaften vom Mänxen und anderen Personen.
Created on 03.04.2023
"""
__author__ = "Jasper Ischebeck"

from enum import auto, Enum
from attrs import define, field
from typing import Literal


class Rasse(Enum):
    """Eine humanoide Rasse."""
    Mensch = 1
    Munin = 2
    Lavaschnecke = 11  # ja, humanoid!
    Skelett = 12


class Fähigkeit(Enum):
    """Mögliche Fähigkeiten, die der Mänx erlernen kann. Je nachdem, ob der Mensch
    eine Fähigkeit hat, werden verschiedene neue Dialoge freigeschaltet."""
    # Halte diese Liste alphabetisch.
    Ausweichen = auto()
    Orgel = auto()
    Schnellplündern = auto()


class Geschlecht(Enum):
    """Alle humanoiden Wesen sind weiblich oder männlich."""
    Weiblich = 0
    Männlich = 1


def to_geschlecht(attr: Literal["m"] | Literal["w"] | Geschlecht) -> Geschlecht:
    """Wandelt eine Eingabe zu Geschlecht um."""
    match attr:
        case "m":
            return Geschlecht.Männlich
        case Geschlecht():
            return attr
        case "w":
            return Geschlecht.Weiblich
        case str(other):
            raise ValueError(f"Unbekanntes Geschlecht: {other}")
    raise TypeError(f"Falscher Typ für Geschlecht: {type(attr)} ({attr})")


@define
class Person:
    """Definiert Eigenschaften, die jedes intelligente Wesen in Xvatc hat. Ein nicht-intelligentes
    Wesen hat diese Eigenschaft nicht."""
    geschlecht: Geschlecht = field(converter=to_geschlecht)
    rasse: Rasse = Rasse.Mensch
