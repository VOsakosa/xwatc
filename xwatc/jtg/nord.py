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
from xwatc.jtg import SÜD_DORF_NAME
__author__ = "jasper"
REGISTER = {}


def register(name):
    def do_register(fkt):
        REGISTER[name] = fkt
        return fkt
    return do_register

def registrieren(mänx: Mänx):
    for name, fkt in REGISTER.items():
        if name not in mänx.welt:
            mänx.welt[name] = fkt()

def frage_melken(nsc: NSC, _mänx: Mänx):
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
    # TODO Tod berichten 
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

def kampf_axtmann(nsc: NSC, mänx: Mänx):
    print("Ganz miese Idee, dich mit ihm anzulegen.")
    if mänx.ja_nein("Willst du es wirklich tun?"):
        if mänx.hat_klasse("legendäre Waffe") and random.random() > 0.97:
            print("Das Glück ist auf deiner Seite und in einem anstrengenden "
                "Kampf bringst du ihn um.")
        elif not mänx.hat_klasse("Waffe"):
            mint("Du hast Glück")
            print("Nein, du hast nicht gewonnen. Aber du hast es geschafft, so"
                  " erbärmlich dich anzustellen, dass er es als Scherz sieht.")
            nsc.freundlich -= 10
        else:
            print("Ist ja nicht so, dass du nicht gewarnt worden wärst.")
            mint("Als Neuling einen Veteran anzugreifen...")
            raise Spielende
    else:
        print("Der Axtmann starrt dich mit hochgezogenen Augenbrauen an.")
        mint("Seine mächtigen Muskel waren nur für einen kurzen Augenblick "
             "angespannt.")
            
        
@register("jtg:axtmann")
def axtmann() -> NSC:
    n =  NSC("?", "Axtmann", kampf_axtmann, startinventar={
        "mächtige Axt": 1,
        "Kettenpanzer": 1,
        "T-Shirt": 1,
        "Pausenbrot": 2,
        "Tomate": 1,
        "Ehering": 1,
        "Kapuzenmantel": 1,
        "Speisekarte": 1,
        "Lederhose": 1,
    })
    n.dialog("hallo", '"Hallo"', [".."])
    return n

@register("jtg:fred")
def fred() -> NSC:
    n = NSC("Fréd Fórmayr", "Dorfvorsteher", kampf_in_disnayenbum,
            startinventar={
        "Messer": 1,
        "Anzug": 1,
        "Anzugjacke": 1,
        "Lederschuh": 2,
        "Ledergürtel": 1,
        "Kräutersud gegen Achselgeruch": 2,
        "Armbanduhr": 1,
    })
    n.dialog("hallo", '"Hallo"', [
        "Willkommen in Disnajenbun! Ich bin der Dorfvorsteher Fred.",
        "Ruhe dich ruhig in unserem bescheidenen Dorf aus."])
    n.dialog("woruhen", '"Wo kann ich mich hier ausruhen?"', 
            ["Frag Lina, gleich im ersten Haus direkt hinter mir."], "hallo")
    n.dialog("wege", '"Wo führen die Wege hier hin?"',[
        "Also...",
        "Der Weg nach Osten führt nach Tauern, aber du kannst auch nach " +
        SÜD_DORF_NAME + " abbiegen.",
        "Der Weg nach Süden führt, falls du das nicht schon weißt, nach " + 
        "Grökrakchöl.",
        "Zuallerletzt gäbe es noch den Weg nach Westen...",
        "Da geht es nach Eo. Ich muss stark davon abraten, dahin zu gehen.",
        "Wenn Ihnen Ihr Leben lieb ist."
    ], "hallo")
    return n
            