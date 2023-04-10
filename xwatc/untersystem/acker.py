"""
Anbau von Pflanzen.
Created on 29.10.2020
"""
from typing import Optional as Opt
from xwatc.system import Inventar, malp, Mänx, MänxFkt
from xwatc.effect import NurWenn, TextGeschichte, Cooldown
__author__ = "jasper"


def wildpflanze(id_: str, reife: float, beute: Inventar, text: str) -> MänxFkt[None]:
    return NurWenn(Cooldown(id_, reife), TextGeschichte([text], schatz=beute))  # type: ignore