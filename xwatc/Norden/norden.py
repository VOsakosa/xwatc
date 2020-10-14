from time import sleep
import xwatc_Hauptgeschichte as xwatc
from xwatc.system import Mänx, minput, Gefährte, ja_nein, Spielende
from xwatc.scenario import lade_scenario

def norden(mänx):
    print("Du wanderst 9 Tage lang gen Norden, bis du zu einem kleinen Fischerdorf "
          "kommst.")
    print("An einem Stand verkauft eine alte Frau Fische. ")
    while True:
        antwort=minput(mänx, 
                "Gehst du etwas kaufen,greifst du sie an oder gehst du einfach weiter?(antworte mit handeln/angreifen/"
                "weitergehen (großkleinschreibung))", ["handeln","angreifen", "weitergehen"])
        if antwort=="handeln":
            if mänx.inventar["Gold"] >= 5:
                fisch=minput(mänx, "Du kannst eine Scholle, eine Sardine oder einen Hering kaufen. "
                             "abbrechen/Scholle/Sardine/Hering", ["abbrechen", "scholle", "sardine", "hering"])
                if fisch != "abbrechen":
                    mänx.inventar[fisch.capitalize()] += 1
                    mänx.inventar["Gold"] -= 5
            else:
                print("Du hast nicht genug Geld dafür")
        else:
            break
    if antwort=="weitergehen":
        print("Du gehst weiter und triffst auf einen Bettler.")
        if mänx.hat_item("Gold"):
            print("Du kannst ihm ein Stück Geld geben oder "
                  "weitergehen.")
            if ja_nein(mänx, "Gibst du ihm Geld?"):
                mänx.inventar["Gold"] -= 1
                print("Der Bettler blickt dich dankend an.")
                print("Du erhältst einen Stein der Bettlerfreundschaft.")
                mänx.inventar["Stein der Bettlerfreundschaft"] += 1
                    
        else:
            print("Du hast leider kein Geld.")
            
        entscheidung=minput (mänx, "Du wanderst durch das kleine Dorf. Einige Gassenjungen "
                             "folgen dir. Bleibst du im Dorf oder gehst du weiter? "
                             "bleiben/w",["bleiben","w"])
        if entscheidung=="w":
            weg=minput(mänx, "Gehst du in die R"
                       "ichtung aus der du gekom"
                       "men bist, in eine völlig"
                       " andere oder weiter in Ri"
                       "chtung Norden? z/a/w"
                       "zurück/anders/weiter", ["z","w","a"])
            if weg=="z":
                xwatc.himmelsrichtungen(mänx)
                
                
            if weg=="a":
                k=minput(mänx, "Gehst du in Richtung Westen oder in Richtung Osten? (w/o",["w","o"])
                if k=="w":
                    print("Hallo")
                                
            if weg=="w":
                print("Du gehst weiter in Richtung Norden")
                
                
                
                
        elif entscheidung=="bleiben":
            lade_scenario(mänx, "S2.txt")
            
        
           
        
    elif antwort=="angreifen":
        
        if mänx.hat_item("Speer"):
            Kampf=minput(mänx, "Du bohrst der Alten deinen Speer in den Rücken, worauf sie mit entsetzten Augen "
                         "verendet.Nun kommt eine Wache auf dich zu.angreifen/sichwappnen/fliehen (a/sw/f")
            mänx.welt.setze("Fischerfrautot")
        elif mänx.hat_item("Schild"):
            print("Du stürzt dich auf die alte Frau und drückst "
                  "sie mit deinem Schild zu Boden, während "
                  "du auf sie einprügelst. Sie kreischt erstaunlich mädchenhaft "
                  "auf. Sie ist nun entweder tot oder bewusstlos. \n"
                  "Du bekommst ein Messer. Wahrscheinlich hat die Frau damit Fische ausgeweidet. \n"
                  "Jetzt greift dich eine Wache an und eine weitere ist im Anmarsch. "
                  "Das hast du nun davon, wenn du eine hilflose, alte Frau angreifst.")
            mänx.inventar["Messer"] += 1
            mänx.welt.setze("Fischerfrautot")
            Kamf=minput(mänx, "parierenundstechen/fliehen/parieren (ps/f/p")
        elif mänx.hat_item("Schwert"):
            print("Du streckst die Alte mit deinem Schwert nieder, worauf es dunkelrot "
                  "zu pulsieren anfängt. Du lachst bösartig wärend "
                   "sich über dir Gewitterwolken sammeln. Die Wachen weichen angsterfüllt zurück.")
            massaker=minput(mänx, "Greifst du sie an, gehst du weg oder raubst du die Fischverkäuferin aus?a/w/au "
                            "(angreifen/weggehen/ausrauben)", ["a","w","au"])
            mänx.welt.setze("Fischerfrauschwerttot")
            
            if massaker=="a":
                print("Ein Blitz fährt herab und streckt einen Wächter "
                      "nieder. Der Andere will fliehen, doch dein Schwe"
                      "rt fliegt dir aus der Hand und steckt nun in sei"
                      "ner Brust.")
                a=minput(mänx, "Raubst du erst einmal alles aus,"
                         "bringst du die anderen Leute im Dorf u"
                         "m oder gehst du weg?r/u/w (räubern/umb"
                         "ringen/weggehen)", ["r","w","u"])
                if a=="r":
                    print("Du bekommst eine Menge Zeug")
                    mänx.inventar["Hering"] += 4
                    mänx.inventar["Scholle"] += 5
                    mänx.inventar["Sardine"] += 6
                    mänx.inventar["Messer"] += 1
                    mänx.inventar["Lederrüstung"] += 2
                    mänx.inventar["Unterhose"] += 2
                    mänx.inventar["Hemd"] += 2
                    mänx.inventar["Hose"] += 2
                    mänx.inventar["Gold"] += 120
                    mänx.inventar["Speer"] += 2
                    mänx.inventar["Schild"] += 2
                    mänx.inventar["Eisenhelm"] += 2
                elif a=="w":
                    print("Du bist wieder dort wo "
                          "alles anfing. Nun stehs"
                          "t du vor einer Lebensve"
                          "rändernden Entscheidung.")
                    weg=minput(mänx, "Schmeißt du das Schwert weg oder nicht?j/n", ["j","n"])
                    
                    if weg=="j":
                        print("Es ist als würde eine schwere Last von dir abfallen.")
                    
                        mänx.inventar["Schwert"] -= 1
                        himmelsrichtungen(mänx)
                    else: # elif weg=="n":
                        print("Du grinst. Und eine Stimme meldet sich "
                              "in den Tiefen von dir. Du spürst wie et"
                              "was dein Gewissen auffrisst. Die Stimme"
                              "fängt an zu lachen. Dieses Lachen... wa"
                              "r eindeutig böse und skrupellos. Und du"
                              "... stimmst in das Lachen ein.")
                        himmelsrichtungen(mänx)
            
            elif massaker=="au":
                print("Du bekommst eine Menge Zeug")
                mänx.inventar["Hering"] += 4
                mänx.inventar["Scholle"] += 5
                mänx.inventar["Sardine"] += 6
                mänx.inventar["Messer"] += 1
                input("Eine mutige Wache sticht dir in den Rücken und du stirbst.")
                    
                    
            elif massaker=="w":
                    print("Du bist wieder dort wo "
                          "alles anfing. Nun stehs"
                          "t du vor einer Lebensve"
                          "rändernden Entscheidung.")
                    weg=minput(mänx, "Schmeißt du das Schwert weg oder nicht?j/n", ["j","n"])
                    
                    if weg=="j":
                        print("Es ist als würde eine schwere Last von dir abfallen.")
                    
                        mänx.inventar["Schwert"] -= 1
                        himmelsrichtungen(mänx)
                    else: # elif weg=="n":
                        print("Du grinst. Und eine Stimme meldet sich "
                              "in den Tiefen von dir. Du spürst wie et"
                              "was dein Gewissen auffrisst. Die Stimme"
                              "fängt an zu lachen. Dieses Lachen wa"
                              "r eindeutig böse und skrupellos. Und du"
                              " stimmst in das Lachen ein.")
                        himmelsrichtungen(mänx)
            
        elif mänx.hat_item("Spitzhacke"):
            print("Du tötest die arme Frau mit einem einzigen wohlplazierten Schlag deiner Spitzhacke")
            mänx.welt.setze("Fischerfrautot")
        
    
        else:  # Leere
            print("Du stürzt dich auf die alte Frau und schlägst auf sie ein."
                  "Sie kreischt und - stößt dir ein Messer in den Bauch. Du starrst entsetzt auf die Wunde"
                  ", Blut rinnt aus ihr. Ein paar Sekunden später bist du tot.")
            mänx.welt.setze("Fischerfraugewarnt")
            raise Spielende()
                # mänx.inventar_leeren()
        
                # waffe_wählen(mänx)    
            
            
    
    
                        
                    
                
            
    
    
