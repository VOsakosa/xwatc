import pickle
from logging import getLogger
from xwatc.system import (Mänx, Spielende, mint, malp, SPEICHER_VERZEICHNIS,
                          Fortsetzung, MenuOption)
from xwatc import _
from xwatc import system
from xwatc import weg
from pathlib import Path
from typing import Optional as Opt
from xwatc.lg import mitte
from xwatc.untersystem.person import Rasse


def hauptmenu() -> None:
    """Das Hauptmenu von Xwatc, erlaubt Laden und neues Spiel starten.
    (Nur Terminal-Modus)"""
    while True:
        mgn1 = [(_("Lade Spielstand"), "lade", False),
                (_("Neuer Spielstand"), "neu", True)]
        if system.ausgabe.menu(None, mgn1):
            main(Mänx())
            return
        mgn2: list[MenuOption[Opt[Path]]] = [
            (path.name, path.name.lower(), path) for path in
            SPEICHER_VERZEICHNIS.iterdir()  # @UndefinedVariable
        ]
        mgn2.append(("Zurück", "zurück", None))
        wahl = system.ausgabe.menu(None, mgn2)
        if wahl:
            with wahl.open("rb") as file:
                mänx = pickle.load(file)
            assert isinstance(mänx, Mänx)
            main(mänx)
            return


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


def main(mänx: Mänx):
    """Die Hauptschleife von Xwatc."""
    if not mänx.speicherpunkt:
        malp(_("Willkommen bei Xwatc"))
    ende = False
    punkt: Fortsetzung | None = mänx.speicherpunkt
    while not ende:
        if not punkt:
            punkt = waffe_wählen
        try:
            while punkt:
                getLogger("xwatc").info(f"Betrete {punkt}.")
                if isinstance(punkt, weg.Wegpunkt):
                    punkt = weg.wegsystem(mänx, punkt, return_fn=True)
                elif callable(punkt):
                    punkt = punkt(mänx)
                else:
                    punkt = punkt.main(mänx)
        except Spielende:
            malp(_("Du bist tot"))
            punkt = None
        except EOFError:
            ende = True
        else:
            ende = False
        malp("Hier ist die Geschichte zu Ende.")
        if mänx.titel:
            malp("Du hast folgende Titel erhalten:", ", ".join(mänx.titel))
        if not ende:
            mänx.inventar_leeren()
            malp("Aber keine Sorge, du wirst wiedergeboren")
        elif not mänx.ausgabe.terminal:
            mänx.menu([("Beenden", "weiter", None)])


if __name__ == '__main__':
    hauptmenu()
