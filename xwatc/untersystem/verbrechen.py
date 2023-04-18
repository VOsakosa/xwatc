"""
Created on 12.08.2021
"""
from enum import Enum, auto
from attrs import define
__author__ = "leo"

class Verbrechensart(Enum):
    MORD = auto()
    AUSBRUCH = auto()
    DIEBSTAHL = auto()
    SACHBESCHÄDIGUNG = auto()

@define(frozen=True)
class Verbrechen:
    art: Verbrechensart
    versuch: bool = False
