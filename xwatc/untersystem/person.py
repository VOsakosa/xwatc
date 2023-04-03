"""
Verschiedene Eigenschaften vom Mänxen und anderen Personen.
Created on 03.04.2023
"""
__author__ = "Jasper Ischebeck"

from enum import auto, Enum


class Rasse(Enum):
    """Eine humanoide Rasse."""
    Mensch = 1
    Munin = 2
    Lavaschnecke = 11
    Skelett = 12

class Fähigkeit(Enum):
    """Mögliche Fähigkeiten, die der Mänx erlernen kann. Je nachdem, ob der Mensch
    eine Fähigkeit hat, werden verschiedene neue Dialoge freigeschaltet."""
    # Halte diese Liste alphabetisch.
    Ausweichen = auto()
    Orgel = auto()
    Schnellplündern = auto()