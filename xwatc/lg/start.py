"""
Die Erstellung des Charakters.
"""

from xwatc.system import (Mänx, mint, malp, Fortsetzung)
from xwatc import _
from xwatc.lg import mitte
from xwatc.untersystem.person import Rasse

__author__ = "Leo Ischebeck"


def waffe_wählen(mänx: Mänx) -> Fortsetzung:
    mint(_("Du wirst nun einem kleinen Persönlichkeitstest unterzogen."))
    rasse = mänx.menu([
        (_("Mensch"), "mensch", Rasse.Mensch),
        (_("Munin"), "munin", Rasse.Munin)
    ], _("Was willst du sein?"), versteckt={_("lavaschnecke"): Rasse.Lavaschnecke},
        save=waffe_wählen)
    mänx.rasse = rasse
    if rasse == Rasse.Lavaschnecke:
        malp(_("Na gut. "
             "Dann bist du eben eine seltene Lavaschnecke. "
               "Das hast du nun von deinem Gejammer!"))

    waffe = mänx.minput(_("Wähle zwischen Schwert, Schild und Speer: "),
                        ["Schwert", "Speer", "Schild"])
    if waffe == "speer":
        malp("Du hast den Speer aufgenommen.")
    elif waffe == "schild":
        malp("Du hast den Schild aufgenommen. Das könnte sowohl eine gute als auch eine "
             "schlechte Wahl gewesen sein.")
    elif waffe == "schwert":
        malp("Jetzt bist du der Besitzer eines Schwertes namens Seralic. "
             "Möglicherweise erweist es sich ja "
             "als magisches Schwert.")
    elif not waffe:
        malp("Du wählst nicht? Ok.")
        waffe = "leere"
    else:
        malp(f'Hier liegt kein/e/er "{waffe}"!')
        waffe = "Leere"
    mänx.inventar[waffe.capitalize()] += 1
    mint(f"Übrigens, dein Inventar enthält jetzt: {mänx.inventar_zeigen()}. "
         "(Mit der Taste e kannst du dein Inventar überprüfen.)")
    return mitte.MITTE_EINTRITT
