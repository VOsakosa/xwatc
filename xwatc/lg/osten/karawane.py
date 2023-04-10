
from typing import List
from xwatc.nsc import OldNSC
from xwatc.system import Mänx, minput, InventarBasis, malp, get_item, get_preise, Inventar



def karawanenfracht_anzeigen(inventar: Inventar):
    ans = []
    if not any(inventar.values()):
        return "Nichts da."
    for item, anzahl in sorted(inventar.items()):
        if anzahl and item != "Gold":
            item_obj = get_item(item)
            kosten = get_preise(item)
            ans.append(f"{anzahl:>4}x {item_obj:<20} ({kosten:>3}G)")
    return "\n".join(ans)


class Karawane:
    def __init__(self):
        self.fracht = InventarBasis()
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
            malp(karawanenfracht_anzeigen(self.fracht.inventar))

        elif opt == 1:
            malp("Lass mich in Ruhe!")

        elif opt == 2:
            opts2 = [(an.name, an.name.lower(), an) for an in self.angestellte]
            mänx.menu(opts2).main(mänx)

        elif opt == 3:
            malp("Lass mich in Ruhe!")

        else:
            pass


class Angestellte(OldNSC):
    def __init__(self, lohn: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lohn = lohn
        # self.dialog("lohn", "Über Lohn reden", type(self).lohn_reden)

    def lohn_reden(self, mänx: Mänx):
        w = minput(
            mänx, "Willst du den Lohn erhöhen oder erniedrigen? h/n ", ["h", "n"])
        if w == "h":
            self.lohn += 1
            self.sprich(f"Hurra! Ich verdiene jetzt {self.lohn} Gold!")
        else:  # niedriger
            self.sprich("Wieso nur?!")
