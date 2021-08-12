"""
Created on 12.08.2021
"""
from enum import Enum, auto
from typing import NamedTuple
__author__ = "leo"

class Verbrechensart(Enum):
    MORD = auto()
    AUSBRUCH = auto()
    DIEBSTAHL = auto()
    SACHBESCHÄDIGUNG = auto()


class Verbrechen(NamedTuple):
    art: Verbrechensart
    versuch: bool = False
