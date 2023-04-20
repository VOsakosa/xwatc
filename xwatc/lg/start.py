"""
Die Erstellung des Charakters.
"""

from xwatc.system import (Mänx, mint, malp, sprich, Fortsetzung)
from xwatc import _
from xwatc.lg import mitte
from xwatc.untersystem.person import Rasse, Geschlecht

__author__ = "Leo Ischebeck"


def waffe_wählen(mänx: Mänx) -> Fortsetzung:
    malp(_("Lass uns zunächst deinen Charakter erstellen."))
    malp("Von welcher Rasse soll dein Charakter sein?")
    mänx.person.rasse = mänx.menu([
        (_("Mensch"), "mensch", Rasse.Mensch),
        (_("Munin"), "munin", Rasse.Munin)
    ], versteckt={_("lavaschnecke"): Rasse.Lavaschnecke},
        save=waffe_wählen)
    if mänx.rasse == Rasse.Lavaschnecke:
        malp(_("Nanu?"))
        malp("Du hast die geheime Rasse Lavaschnecke gefunden.")
        malp("Dann bist du eben eine seltene Lavaschnecke. "
             "Das hast du nun von deinem Gejammer!")
        malp("Eigentlich solltest du jetzt eine richtige Lavaschnecken-Geschichte erleben, aber "
             "diese ist noch nicht geschrieben.")
        mint()
        sprich(_("Gott der Lavaschnecken"),
               _("Dann lass meine Kleine doch die normale Geschichte leben."))
        malp("Aber als Lavaschnecke kann der Charakter doch gar nicht normal leben!")
        sprich(_("Gott der Lavaschnecken"),
               _("Dann mache ich meiner Kleinen die Form eines Menschen."))
        malp("Du bist dann wohl ein Lavaschnecke in der Form eines Menschen.")
        malp("Apropos Mensch, soll er denn männlich oder weiblich aussehen?")
    else:
        malp("Kommen wir zur einfachsten Frage: Welches Geschlecht willst du haben?")
        malp("Menschen und Munin haben in diesem Spiel zwei Geschlechter: männlich und weiblich.")
    mänx.person.geschlecht = mänx.menu([
        (_("weiblich"), "weiblich", Geschlecht.Weiblich),
        (_("männlich"), "männlich", Geschlecht.Männlich)
    ], save=waffe_wählen)

    malp(_("Du wirst nun einem kleinen Persönlichkeitstest unterzogen:"))
    malp("Du musst nämlich eine von drei Waffen wählen.")

    waffe = mänx.minput(_("Wähle zwischen Schwert, Schild und Speer: "),
                        ["Schwert", "Speer", "Schild"])
    if waffe == "speer":
        malp("Du hast den Speer aufgenommen.")
        malp("Das ist, soviel kann ich dir verraten, die sicherste aber auch die langweiligste "
             "Wahl.")
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
    mänx.erhalte(waffe.capitalize())

    malp("Dein Inventar besteht übrigens nicht nur aus der Waffe. Du hast auch ein Set Kleidung "
         "bekommen. ")
    malp("Mit der Taste 'e' kannst du jederzeit dein Inventar überprüfen.")
    mint()
    return mitte.MITTE_EINTRITT


def respawn(_mänx: Mänx) -> Fortsetzung:
    malp("Du darfst dein Inventar behalten und wirst an den ursprünglichen Ort zurückgesetzt.")
    return mitte.MITTE_EINTRITT
