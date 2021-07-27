"""
Anzeige von Xwatc durch das Terminal.
"""
from __future__ import annotations
import re
from typing import Sequence, Optional, List, Mapping, TypeVar, TYPE_CHECKING
from time import sleep
__author__ = "jasper"

if TYPE_CHECKING:
    from xwatc.system import Mänx, MenuOption

T = TypeVar("T")
def menu(mänx: Mänx,
         optionen: list[MenuOption[T]],
         frage: str = "",
         gucken: Optional[Sequence[str]] = None,
         versteckt: Optional[Mapping[str, T]] = None) -> T:
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
    print()
    for i, (name, kurz, _) in enumerate(optionen):
        print(i + 1, ".", name, " [", kurz, "]", sep="")
    kurz_optionen = " " + "/".join(o[1] for o in optionen)
    if len(kurz_optionen) < 50:
        frage += kurz_optionen + " "
    while True:
        eingabe = input(frage).lower()
        if versteckt and eingabe in versteckt:
            return versteckt[eingabe]
        kandidaten = []
        for _, o, v in optionen:
            if o == eingabe:  # Genauer Match
                return v
            elif o.startswith(eingabe):
                kandidaten.append((o, v))
        if eingabe == "g" or eingabe == "gucken":
            if isinstance(gucken, str):
                print(gucken)
            elif gucken:
                for zeile in gucken:
                    print(zeile)
            else:
                print("Hier gibt es nichts zu sehen")

        elif not spezial_taste(mänx, eingabe) and eingabe:
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


def minput(mänx: Mänx, frage: str, möglichkeiten=None, lower=True) -> str:
    """Manipulierter Input
    Wenn möglichkeiten (in kleinbuchstaben) gegeben, dann muss die Antwort eine davon sein."""
    if not frage.endswith(" "):
        frage += " "
    while True:
        taste = input(frage)
        if lower:
            taste = taste.lower()
        if spezial_taste(mänx, taste):
            pass
        elif not möglichkeiten or taste in möglichkeiten:
            return taste


def spezial_taste(mänx: Mänx, taste: str) -> bool:
    """Führe die Spezialaktion taste aus, oder gebe Falsch zurück."""
    from xwatc.system import Spielende
    from xwatc.untersystem import hilfe
    if taste == "e":
        print(mänx.inventar_zeigen())
    elif taste == "ee":
        print(mänx.erweitertes_inventar())
    elif taste == "q":
        print(mänx.missionen_zeigen())
    elif taste == "sterben":
        mänx.lebenswille = 0
    elif taste == "hilfe":
        print("Entkomme mit 'sofort sterben'. Nebeneffekt: Tod.")
        print("Wenn du einfach nur Hilfe zu irgendwas haben willst, schreibe"
              " 'hilfe [frage]'.")
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
        raise Spielende()
    else:
        return False
    return True


def mint(*text):
    """Printe und warte auf ein Enter."""
    input(" ".join(str(t) for t in text))


def sprich(sprecher: str, text: str, warte: bool = False, wie: str = ""):
    if wie:
        sprecher += f"({wie})"
    if warte:
        mint(f'{sprecher}: »{text}«')
    else:
        print(end=f'{sprecher}: »')
        for word in re.split(r"(\W)", text):
            print(end=word, flush=True)
            sleep(0.05)
        print('«')


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
        mint(end)
    else:
        print(end=end)


def ja_nein(mänx, frage):
    """Ja-Nein-Frage"""
    ans = minput(mänx, frage, ["j", "ja", "n", "nein"]).lower()
    return ans == "j" or ans == "ja"


def kursiv(text: str) -> str:
    """Packt text so, dass es kursiv ausgedruckt wird."""
    return "\x1b[3m" + text + "\x1b[0m"
