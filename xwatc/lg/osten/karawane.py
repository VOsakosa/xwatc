
from xwatc.nsc import NSC
from xwatc.system import Mänx, InventarBasis, malp, get_item, get_preise, Inventar
from attr import field


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
    fracht: InventarBasis = field(factory=InventarBasis)
    angestellte: list[NSC] = field(factory=list)

    def lohn_zahlen(self, mänx: Mänx) -> bool:
        """Zahle Gold an deine Angestellten, solange es reicht. Gib False zurück, falls
        einige nicht bezahlt worden sind."""
        # for an in self.angestellte:
        #     if an.lohn <= mänx.gold:
        #         mänx.gold -= an.lohn
        #         an.gold += an.lohn
        #     else:
        #         return False
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
