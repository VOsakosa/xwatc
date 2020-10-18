"""
NSCs für Disnajenbun
Created on 18.10.2020
"""
from xwatc.system import Mänx, mint, Spielende
from xwatc.dorf import NSC
import random
import re
from typing import Optional
from xwatc.scenario import Scenario
__author__ = "jasper"
REGISTER = {}


def register(name):
    def do_register(fkt):
        REGISTER[name] = fkt
        return fkt
    return do_register

def frage_melken(nsc: NSC, mänx: Mänx):
    if nsc.freundlich >= 0:
        nsc.sprich("Aber nur weil du es bist.")
        print(f"{nsc.name} wirkt leicht beschämt.")
    else:
        nsc.sprich("Nein! Natürlich nicht!")
        print("Sie ist echt wütend!")

def kampf_in_disnayenbum(nsc: NSC, mänx: Mänx):
    mint(f"Du greifst {nsc.name} an.")
    if isinstance(mänx.context, Scenario):
        # mänx.context.warne_kampf(nsc, mänx)
        if "jtg:axtmann" in mänx.welt and not mänx.welt["jtg:axtmann"].tot:
            print("Aber das ist dem Mann mit der Axt nicht entgangen.")
            print("Er macht kurzen Prozess aus dir.")
            raise Spielende()
    mint("Ein leichter Kampf.")
    nsc.tot = True
    nsc.plündern(mänx)
        

@register("jtg:nomuh")
class NoMuh(NSC):
    def __init__(self):
        super().__init__("No Muh", "Kuh", freundlich=-10,
                         kampfdialog=kampf_in_disnayenbum)
        self.inventar["Glocke"] += 1
        self.dialog("hallo", '"Hallo"', ("Hallo.",))
        self.dialog("futter", '"Was hättest du gerne zu essen?"',
                     ("Erbsen natürlich."))
        self.dialog("melken", '"Darf ich dich melken?"', frage_melken)
        self.verstanden = False
        self.letztes_melken: Optional[int] = None

    def vorstellen(self, mänx: Mänx):
        print("Eine große Kuh frisst Gras.")
        self.sprich("Pfui, so jemand starrt mich an.")
        self.sprich("No nie so eine Schönheit gesehen, was?")

    def fliehen(self, mänx: Mänx):
        if self.freundlich < 0:
            if random.random() < 0.3:
                print("Beim Fliehen streift dich eines von NoMuhs Hörnern.")
                mint("Es tut verdammt weh.")
            else:
                mint("Du entkommst der wütenden NoMuh")

    def main(self, mänx: Mänx):
        self.verstanden = mänx.hat_item("Mugel des Verstehens")
        return super().main(mänx)
    
    def sprich(self, text:str, *args, **kwargs)->None:
        if self.verstanden:
            NSC.sprich(self, text, *args, **kwargs)
        else:
            text = re.sub(r"\w+", "Muh", text)
            NSC.sprich(self, "Muh", *args, **kwargs)

    def optionen(self, mänx: Mänx):
        yield from super().optionen(mänx)
        yield ("versuchen, NoMuh zu melken", "melken", self.melken)
        yield ("NoMuh füttern", "füttern", self.füttern)

    def füttern(self, mänx: Mänx):
        opts = [("Gras ausreißen", "gras", "gras")]
        if mänx.hat_item("Gänseblümchen"):
            opts.append(("Gänseblümchen", "gänseblümchen", "gb"))
        if mänx.hat_item("Erbse"):
            opts.append(("Erbsen", "erbsen", "eb"))
        if mänx.hat_item("Mantel"):
            opts.append(("Mantel", "mantel", "mt"))
        ans = mänx.menu(opts, frage="Was fütterst du sie?")
        if ans == "gras":
            print("NoMuh frisst das Gras aus deiner Hand")
            mint("und kaut gelangweilt darauf herum.")
        elif ans == "eb":
            print("NoMuh leckt dir die Erbsen schnell aus der Hand.")
            mänx.inventar["Erbse"] -= 1
            self.sprich("Endlich jemand, der mich versteht. Danke!")
            self.freundlich += 10
    
    def melken(self, mänx: Mänx):
        if self.freundlich >= 0:
            if self.letztes_melken is None or self.letztes_melken < mänx.welt.get_tag():
                self.letztes_melken = mänx.welt.get_tag()
                mänx.erhalte("magische Milch", 1)
            else:
                mint("No Muh wurde heute schon gemolken.")
        else:
            self.sprich("Untersteh dich, mich da anzufassen!")
            mint("NoMuh tritt dich ins Gesicht.")
            