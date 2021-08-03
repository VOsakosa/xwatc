
from xwatc.lg.norden import norden
from xwatc.lg.westen import westen
from xwatc.lg.osten import osten
from xwatc.lg.süden import süden
from xwatc.system import Mänx, minput, Spielende, mint, malp
import random


def waffe_wählen(mänx: Mänx):
    rasse = mänx.minput("Was willst du sein?", ["Mensch"])
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


def main(mänx: Mänx):
    malp("Willkommen bei Xwatc")
    mint("Du wirst nun einem kleinen Persönlichkeitstest unterzogen.")
    ende = False
    while not ende:
        waffe_wählen(mänx)
        try:
            himmelsrichtungen(mänx)
        except Spielende:
            malp("Du bist tot")
            ende = True
        else:
<<<<<<< HEAD
            ende = not mänx.will_weiterleben()
        malp("Hier ist die Geschichte zu Ende.")
=======
            ende = False
        print("Hier ist die Geschichte zu Ende.")
>>>>>>> refs/heads/kampf
        if mänx.titel:
            malp("Du hast folgende Titel erhalten:", ", ".join(mänx.titel))
        if not ende:
            mänx.inventar_leeren()
            malp("Aber keine Sorge, du wirst wiedergeboren")


def himmelsrichtungen(mänx):
    richtung = minput(mänx, "Wohin gehst du jetzt? "
                      "In Richtung Norden ist das nächste Dorf, im Süden warten "
                      "Monster auf dich, im Westen liegt "
                      "das Meer und der Osten ist unentdeckt"
                      ".", ["Norden", "Osten", "Süden", "Westen"])
    if richtung == "norden":
        norden.norden(mänx)
    elif richtung == "osten":
        osten.osten(mänx)
    elif richtung == "süden":
        süden.süden(mänx)
    else: # if richtung == "westen":
        westen.westen(mänx)


if __name__ == '__main__':
    main(Mänx())
