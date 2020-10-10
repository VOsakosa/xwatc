from time import sleep
import xwatc_Hauptgeschichte as xwatc
from xwatc.system import Mänx, minput, Gefährte, ja_nein
from xwatc import jaspersteilgeschichte
import random

def osten(mänx):
    print("Du wanderst lange, lange in Richtung Osten, "
              "dein Proviant ist aufgebraucht, dein Mund trocken und"
              " dein Magen knurrt.")
    print("Es ist heiß, höllisch heiß. In der Ferne siehst du einen Höhleneingang. In der anderen Richtung"
          " siehst du etwas das wie eine Oase aussieht.")
    richtung=minput(mänx, "Gehst du einfach geradeaus, gehst du zur Oase oder zum Höhleneingang?"
                    "w/Oase/Höhle", ["w","oase","höhle"]).lower()
    if richtung=="oase" :
        print("Du läufst zur Oase, aber als du dort ankommst ist sie weg. An ihrer Stelle"
              "stehen dort zwei Türen. Eine Inschrift verkündet: Die eine in den Tode führet, "
              "die andre zu nem andren Ort.")
        weg=minput(mänx, "In welche Tür gehst du? t1/t2",["t2","t1"])
        if weg=="t1" :
             print("Du bist tot")
           #  mänx.inventar_leeren()
             
            # waffe_wählen(mänx)
             
        elif weg=="t2":
            
             jaspersteilgeschichte.t2(mänx)
    elif richtung=="w" :
        print("Du läufst weiter bis du eine Karawane siehst. Ein sonnengebräunter Mann läuft zu dir. ")
        print("Du hast die Wahl, sagt der Mann. Wenn du mich "
              "tötest gehört die gesamte Karawane dir. Du kannst aber auch mein Sklave werden."
              " Dann bekommst du täglich Essen und dir wird sogar ein kleiner Lohn für 1 Gold pro"
              " Woche ausgezahlt. Mit 10 Gold kannst du dich dann freikaufen.")
        Entscheidung=minput(mänx, "Wirst du sein Sklave oder kämpfst du gegen ihn?"
                            "sklave/kampf.(s/k)", ["sklave","kampf"])
        
    elif richtung=="höhle":
        print("In der Höhle ist es dunkel, aber es gibt sauberes Wasser und hier wachsen essbare Pilze.")
        if ja_nein  (mänx, "Willst du die Höhle erkunden?"):
            abzweigung=minput(mänx, "Du gehst tiefer und tiefer. Du stehst nun vor einer Abzweigung."
                              "Auf dem Schildchen über der einen steht bergbau"
                              "und über der anderen steht monster. (b/m)", ["b","m"])
            
            if abzweigung=="b":
                print ("Du nimmst dir eine Spitzhacke und fängst an den Stein zu bearbeiten. Warte eine Minute.")
                sleep (61)
                mänx.inventar ["Spitzhacke"] +=1
                mänx.inventar ["Stein"] += 4
                bla=minput(mänx, "Du bekommst Zeug")
                
            elif abzweigung=="m":
                print("Du hörst ein Klatschen.")
                print("Es klingt ein wenig so, wie wenn man einen nassen Frosch an eine nasse Wand wirft.")
                print("Vorsichtig gehst du weiter.")
                a=random.randint(1,5)
                if a==1:
                    print("Bis plötzlich vor dir ein F®X↓ŋ auftaucht. "
                          "Diese Wesen sehen eigentlich aus wie Frösche."
                          "Also, wenn man mal von der Größe, "
                          "der lilanen Färbung sowie der großen, haarigen, heraushängenden Zunge absah.")
                    
                elif a==2:
                    print("Und hältst inne als vor dir ein Zombie aus der Dunkelheit torkelt.")
                    
                elif a==3:
                    print("Und bleibst stehen als vor dir das uralte Skelett eines Minotaurus,"
                          "offenbar durch böse Magie wiederbelebt,"
                          "aus dem Schatten trat und dabei seine anscheinend noch gut erhaltene Steitaxt schwang.")
                    
                elif a==4:
                    print("Ohne dir Zeit zum Reagieren zu geben,"
                          "schlagen dich einige vermummten Gestalten bewusstlos und stecken dich in einen Sack.")
                    
                elif a==5:
                    print("Vor dir tretet ein bärtiger, nach Alkohohl stinkender Mann aus dem Schatten.")
                
                
                
                
                
