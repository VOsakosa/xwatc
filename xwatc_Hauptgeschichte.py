import pickle
from xwatc.lg.norden import norden
from xwatc.lg.westen import westen
from xwatc.lg.osten import osten
from xwatc.lg.süden import süden
from xwatc.system import (Mänx, Spielende, mint, malp, SPEICHER_VERZEICHNIS,
                          Fortsetzung, MenuOption)
import random
from xwatc import system
from xwatc import weg
from pathlib import Path
from typing import Optional as Opt


def hauptmenu() -> None:
    """Das Hauptmenu von Xwatc, erlaubt Laden und neues Spiel starten.
    (Nur Terminal-Modus)"""
    while True:
        mgn1 = [("Lade Spielstand", "lade", False),
                ("Neuer Spielstand", "neu", True)]
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
    mint("Du wirst nun einem kleinen Persönlichkeitstest unterzogen.")
    if mänx.ausgabe.terminal:
        mgn = None
    else:
        mgn = ["Mensch"]
    rasse = mänx.minput("Was willst du sein?", mgn, save=waffe_wählen)
    mänx.rasse = "Arak"
    if rasse.lower() not in ("mensch", "arak"):
        malp("Nun, eigentlich ist es egal was du sein willst.")
        malp("So oder so, du bist ein Mensch vom Volke der Arak.")
        mint("Im Laufe des Spieles kannst du allerdings weitere Spezies "
             "und Völker freischalten!")

        if mänx.ja_nein("Naja, willst du eigentlich ein Mensch sein?"):
            malp("Na, dann ist ja alles gut.")
        else:
            a = random.randint(1, 11)
            if a != 11:
                malp("Tja, Pech gehabt. Du bist trotzdem einer.")
            else:
                malp("Na gut. "
                     "Dann bist du eben eine seltene Lavaschnecke. "
                     "Das hast du nun von deinem Gejammer!")
                mänx.rasse = "Lavaschnecke"
    else:
        malp("Du wärst sowieso ein Mensch geworden.")

    waffe = mänx.minput("Wähle zwischen Schwert, Schild und Speer: ",
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
    malp(f"Übrigens, dein Inventar enthält jetzt: {mänx.inventar_zeigen()}. "
         "(Mit der Taste e kannst du dein Inventar überprüfen.)")
    return himmelsrichtungen


def main(mänx: Mänx):
    """Die Hauptschleife von Xwatc."""
    if not mänx.speicherpunkt:
        malp("Willkommen bei Xwatc")
    ende = False
    punkt: Fortsetzung | None = mänx.speicherpunkt
    while not ende:
        if not punkt:
            punkt = waffe_wählen
        try:
            while punkt:
                if isinstance(punkt, weg.Wegpunkt):
                    punkt = weg.wegsystem(mänx, punkt, return_fn=True)
                    break
                elif callable(punkt):
                    punkt = punkt(mänx)
                else:
                    punkt = punkt.main(mänx)
        except Spielende:
            malp("Du bist tot")
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


def himmelsrichtungen(mänx: Mänx):
    richtung = mänx.minput(
        "Wohin gehst du jetzt? "
        "In Richtung Norden ist das nächste Dorf, im Süden warten "
        "Monster auf dich, im Westen liegt "
        "das Meer und der Osten ist unentdeckt.",
        ["Norden", "Osten", "Süden", "Westen"],
        save=himmelsrichtungen)
    if richtung == "norden":
        norden.norden(mänx)
    elif richtung == "osten":
        osten.osten(mänx)
    elif richtung == "süden":
        süden.süden(mänx)
    else:  # if richtung == "westen":
        westen.westen(mänx)


if __name__ == '__main__':
    hauptmenu()
