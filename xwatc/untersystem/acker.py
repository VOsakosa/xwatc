"""
Anbau von Pflanzen.
Created on 29.10.2020
"""
from xwatc.system import Inventar, MänxFkt
from xwatc.effect import NurWenn, TextGeschichte, Cooldown
__author__ = "jasper"


def wildpflanze(id_: str, reife: int, beute: Inventar, text: str) -> MänxFkt[None]:
    return NurWenn(Cooldown(id_, reife), TextGeschichte([text], schatz=beute))
