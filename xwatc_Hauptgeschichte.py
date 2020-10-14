from time import sleep

from xwatc.lg.norden import norden
from xwatc.lg.westen import westen
from xwatc.lg.osten import osten
from xwatc.lg.süden import süden
from xwatc.system import Mänx, minput, Gefährte, ja_nein, Spielende, kursiv
import random

def waffe_wählen(mänx):
    
    Rasse = input("Was willst du sein?")
    rasse = input ("Nun, eigentlich ist es egal was du sein willst.")
    rase = input ("So oder so, du bist ein Mensch vom Volke der Arak.")
    rose = input ("Im Laufe des Spieles kannst du allerdings weitere Spezies und Völker freischalten!")
    rosse = input ("Naja, willst du eigentlich ein Mensch sein?")
    if rosse == "ja"or rosse=="j":
        p = input ("Na, dann ist ja alles gut.")
        
    if rosse == "nein" or rosse=="n":
        a=random.randint(1,11)
        if a != 11:
            print("Tja, Pech gehabt. Du bist trotzdem einer.")
        else:
            print("Na gut. "
                  "Dann bist du eben eine seltene Lavaschnecke. "
                  "Das hast du nun von deinem Gejammer!")
    
    waffe = input("Wähle zwischen Schwert, Schild und Speer")
    if waffe=="Speer"or waffe=="speer":
        print("Du hast den Speer aufgenommen.")
    elif waffe == "Schild"or waffe == "schild":
        print("Du hast den Schild aufgenommen. Das könnte sowohl eine gute als auch eine "
              "schlechte Wahl gewesen sein.")
    elif waffe=="Schwert"or waffe=="schwert":
        print("Jetzt bist du der Besitzer eines Schwertes namens Seralic. "
              "Möglicherweise erweist es sich ja "
              "als magisches Schwert.")
    else:
        print(f'Hier liegt kein/e/er "{waffe}"!')
        waffe = "Leere"
    mänx.inventar[waffe.capitalize()] += 1
    print(f"Übrigens, dein Inventar enthält jetzt: {mänx.inventar_zeigen()}. "
          "(Mit der Taste e kannst du dein Inventar überprüfen.)")
    
def main():
    mänx = Mänx()
    ende = False
    while not ende:
        waffe_wählen(mänx)
        try:
            himmelsrichtungen(mänx)
        except Spielende:
            print("Du bist tot")
            ende = True
        else:
            ende = not mänx.will_weiterleben()
        print("Hier ist die Geschichte zu Ende.")
        if mänx.titel:
            print("Du hast folgende Titel erhalten:", ", ".join(mänx.titel))
        if not ende:
            mänx.inventar_leeren()
            print("Aber keine Sorge, du wirst wiedergeboren")

def himmelsrichtungen(mänx):
    richtung=minput (mänx, "Wohin gehst du jetzt? "
              "In Richtung Norden ist das nächste Dorf, im Süden warten "
              "Monster auf dich, im Westen liegt "
              "das Meer und der Osten ist unentdeckt"
              ".",["norden","osten","süden","westen"])
    if richtung=="Norden"or richtung=="norden":
        norden.norden(mänx)
    elif richtung=="Osten"or richtung=="osten":
        osten.osten(mänx)
    elif richtung=="süden":
        süden.süden(mänx)
    elif richtung=="westen":
        westen.westen(mänx)
        
    
                      
if __name__ == '__main__':
    main()