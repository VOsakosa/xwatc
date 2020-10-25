from time import sleep
from xwatc.system import Mänx, minput, Spielende, mint, Karawanenfracht
from xwatc.dorf import NSC
import random

class Karawane:
    def __init__(self):
        self.fracht = Karawanenfracht()
        self.angestellte: List['Angestellte'] = []

    def lohn_zahlen(self, mänx: Mänx) -> bool:
        """Zahle Gold an deine Angestellten, solange es reicht. Gib False zurück, falls
        einige nicht bezahlt worden sind."""
        for an in self.angestellte:
            if an.lohn <= mänx.gold:
                mänx.gold -= an.lohn
                an.gold += an.lohn
            else:
                return False
        return True

    def main(self, mänx: Mänx):
        opts = [
                ('Karawanenfracht anzeigen', 'ke', 0),
                ('Reiseziel auswählen und reisen', "reisen", 1),
                ('Mit Angestellten interagieren.', "wetter", 2),
                ('Protokolle einsehen', "geht", 3)
            ]
        opt = mänx.menu(opts, "Was sagst du?")
            
        if opt == 0:
            print(self.fracht.karawanenfracht_anzeigen())

        elif opt == 1:
            print("Lass mich in Ruhe!")
                
        elif opt == 2:
            opts = [(an.name, an.name.lower(), an) for an in self.angestellte]
            
            
        elif opt == 3:
            print("Lass mich in Ruhe!")
            
        else:
            ('')    


class Angestellte(NSC):
    def __init__(self, lohn: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lohn = lohn
        self.dialog("lohn", "Über Lohn reden", type(self).lohn_reden)
    
    def lohn_reden(self, mänx: Mänx):
        w = minput(mänx, "Willst du den Lohn erhöhen oder erniedrigen? h/n ", ["h", "n"])
        if w == "h":
            self.lohn += 1
            self.sprich(f"Hurra! Ich verdiene jetzt {self.lohn} Gold!")
        else: # niedriger
            self.sprich("Wieso nur?!")
            

