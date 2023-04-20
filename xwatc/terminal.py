"""
Anzeige von Xwatc durch das Terminal.
"""
from __future__ import annotations
import re
from typing import (Optional, Mapping, TypeVar, TYPE_CHECKING, Optional as Opt)
from time import sleep
from xwatc import _
from xwatc.untersystem.menus import Menu
__author__ = "jasper"

if TYPE_CHECKING:
    from xwatc.system import Mänx, Speicherpunkt

T = TypeVar("T")


class Terminal:
    """Ausgaben über das Terminal"""

    terminal = True

    @staticmethod
    def menu(mänx: Mänx | None,
             menu: Menu[T],
             save: Speicherpunkt | None = None) -> T:
        """Ähnlich wie Minput, nur werden jetzt Optionen als Liste gegeben.

        Die Zuordnung geschieht in folgender Reihenfolge
        #. Versteckte Optionen
        #. Optionen
        #. Gucken
        #. Spezialtasten
        #. Nummer
        #. Passendste Antwort
        """
        # print("Du kannst")
        optionen = menu.optionen
        frage = menu.frage
        print()
        for i, (name, kurz, _) in enumerate(optionen):
            print(i + 1, ".", name, " [", kurz, "]", sep="")
        kurz_optionen = " " + "/".join(o[1] for o in optionen)
        if len(kurz_optionen) < 50:
            frage += kurz_optionen + " "
        while True:
            eingabe = input(frage).lower()
            if eingabe in menu.versteckt:
                return menu.versteckt[eingabe]
            kandidaten = []
            for _, o, v in optionen:
                if o == eingabe:  # Genauer Match
                    return v
                elif o.startswith(eingabe):
                    kandidaten.append((o, v))
            if not (mänx and Terminal.spezial_taste(mänx, eingabe, save)) and eingabe:
                try:
                    return optionen[int(eingabe) - 1][2]
                except (IndexError, ValueError):
                    pass
                if len(kandidaten) == 1:
                    return kandidaten[0][1]
                elif not kandidaten:
                    print("Keine Antwort beginnt mit", eingabe)
                else:
                    print("Es könnte eines davon sein:",
                          ",".join(o for o, v in kandidaten))

    @staticmethod
    def minput(mänx: Mänx | None, frage: str, lower=True,
               save: Speicherpunkt | None = None) -> str:
        """Manipulierter Input
        Wenn möglichkeiten (in kleinbuchstaben) gegeben, dann muss die Antwort eine davon sein."""
        if not frage.endswith(" "):
            frage += " "
        while True:
            taste = input(frage)
            if lower:
                taste = taste.lower()
            if mänx and Terminal.spezial_taste(mänx, taste, save=save):
                pass
            else:
                return taste

    @staticmethod
    def spezial_taste(mänx: Mänx, taste: str,
                      save: 'Speicherpunkt | None' = None) -> bool:
        """Führe die Spezialaktion taste aus, oder gebe Falsch zurück."""
        from xwatc.system import Spielende, ZumHauptmenu
        from xwatc.untersystem import hilfe
        if taste == "e":
            print(mänx.inventar_zeigen())
        elif taste == "ee":
            print(mänx.erweitertes_inventar())
        elif taste == "uhr" or taste == "uhrzeit":
            print("Tag {}, {:02}:{:02} Uhr".format(
                mänx.welt.get_tag() + 1, *mänx.welt.uhrzeit()))
        elif taste == "hilfe":
            print("Entkomme mit 'sofort sterben'. Nebeneffekt: Tod.")
            print("Wenn du einfach nur Hilfe zu irgendwas haben willst, schreibe"
                  " 'hilfe [frage]'.")
        elif taste == "speichern" or taste.startswith("speichern "):
            if save:
                if taste == "speichern":
                    mänx.save(save)
                else:
                    mänx.save(save, taste.split()[1])
                print("Spiel gespeichert.")
            else:
                print("Hier kannst du nicht speichern.")
        elif taste.startswith("hilfe "):
            args = taste[6:]
            if args.lower() in hilfe.HILFEN:
                for line in hilfe.HILFEN[args.lower()]:
                    print(line)
            elif any(args == inv.lower() for inv in mänx.inventar
                     ) and args in hilfe.ITEM_HILFEN:
                lines = hilfe.ITEM_HILFEN[args]
                if isinstance(lines, str):
                    print(lines)
                else:
                    for line in lines:
                        print(line)
            else:
                print("Keine Hilfe für", args, "gefunden.")
        elif taste == "sofort sterben":
            raise ZumHauptmenu()
        elif taste == "sterben":
            raise Spielende()
        else:
            return False
        return True

    @staticmethod
    def mint(*text: object) -> None:
        """Printe und warte auf ein Enter."""
        input(" ".join(str(t) for t in text))

    @staticmethod
    def sprich(sprecher: str, text: str, warte: bool = False, wie: str = "") -> None:
        if wie:
            sprecher += f"({wie})"
        if warte:
            Terminal.mint(f'{sprecher}: »{text}«')
        else:
            print(end=f'{sprecher}: »')
            for word in re.split(r"(\W)", text):
                print(end=word, flush=True)
                sleep(0.05)
            print('«')

    @staticmethod
    def malp(*text, sep=" ", end='\n', warte=False) -> None:
        """Angenehm zu lesender, langsamer Print."""
        start = False
        for words in text:
            if start:
                print(end=sep)
            else:
                start = True
            for word in re.split(r"(\W)", str(words)):
                print(end=word, flush=True)
                sleep(0.04)
        if warte:
            Terminal.mint(end)
        else:
            print(end=end)

    @staticmethod
    def kursiv(text: str) -> str:
        """Packt text so, dass es kursiv ausgedruckt wird."""
        return "\x1b[3m" + text + "\x1b[0m"

def hauptmenu() -> None:
    """Das Hauptmenu von Xwatc, erlaubt Laden und neues Spiel starten.
    (Nur Terminal-Modus)"""
    from xwatc import system
    while True:
        if system.ausgabe.menu(None, Menu([(_("Lade Spielstand"), "lade", False),
                (_("Neuer Spielstand"), "neu", True)])):
            system.main_loop(system.Mänx())
            return
        mgn2 = Menu([
            (path.name, path.name.lower(), path) for path in
            system.SPEICHER_VERZEICHNIS.iterdir()  # @UndefinedVariable
        ] + [("Zurück", "zurück", None)])
        wahl = system.ausgabe.menu(None, mgn2)
        if wahl:
            mänx, punkt = system.Mänx.load_from_file(wahl)
            system.main_loop(mänx, punkt)
            return
