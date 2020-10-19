from time import sleep
import xwatc_Hauptgeschichte as xwatc
from xwatc.system import Mänx, minput, kursiv, ja_nein, mint, Spielende
from xwatc import jtg as jaspersteilgeschichte
import random


def osten(mänx: Mänx):
    mint("Du wanderst lange, lange in Richtung Osten, "
         "dein Proviant ist aufgebraucht, dein Mund trocken und"
         " dein Magen knurrt.")
    print("Es ist heiß, höllisch heiß. In der Ferne siehst du einen Höhleneingang. In der anderen Richtung"
          " siehst du etwas das wie eine Oase aussieht.")
    richtung = minput(mänx, "Gehst du einfach geradeaus, gehst du zur Oase oder zum Höhleneingang?"
                      "w/Oase/Höhle", ["w", "oase", "höhle"]).lower()
    if richtung == "oase":
        mint("Du läufst zur Oase, aber als du dort ankommst ist sie weg. An ihrer Stelle"
             "stehen dort zwei Türen. Eine Inschrift verkündet: Die eine in den Tode führet, "
             "die andre zu nem andren Ort.")
        weg = minput(mänx, "In welche Tür gehst du? t1/t2", ["t2", "t1"])
        if weg == "t1":
            print("Du spürst instinktiv, dass das die falsche Entscheidung war.")
            raise Spielende
        elif weg == "t2":
            print("Hinter der Tür ist es warm und sonnig.")
            sleep(1)
            mänx.welt.setze("jtg:t2")
            jaspersteilgeschichte.t2(mänx)
    elif richtung == "w":
        mint("Du läufst weiter bis du eine Karawane siehst. Ein sonnengebräunter Mann läuft zu dir. ")
        mint("Du hast die Wahl, sagt der Mann. Wenn du mich "
             "tötest gehört die gesamte Karawane dir. Du kannst aber auch mein Leibdiener werden."
             " Dann bekommst du täglich Essen und dir wird sogar ein kleiner Lohn für 1 Gold pro"
             " Woche ausgezahlt. Mit 10 Gold kannst du dich dann freikaufen.")
        Entscheidung = minput(mänx, "Wirst du sein Leibdiener oder kämpfst du gegen ihn?"
                              "leibdiener/kampf/flucht.(l/k/f)", ["l", "k", "f"])

        if Entscheidung == "l":
            print('"Hurra!", der Mann strahlt. Ich hatte noch nie einen Arak als Diener!')
            sleep(1)
            mint("Nun beginnt dein Leben als Diener")

        elif Entscheidung == "k":
            mint("")

        elif Entscheidung == "f":
            mint('Du rennst weg,'
                 'doch der Karawanenbesitzer holt dich mit einer übermenschlichen Geschwindigkeit wieder ein '
                 'und fasst dich am Kragen: '
                 '"Schön hier geblieben." '
                 'Dann siehst du beinahe in Zeitlupe eine Klinge herannahen.')

            raise Spielende

    else:  # richtung == "höhle":
        höhle(mänx)


def höhle(mänx: Mänx):
    mint("In der Höhle ist es dunkel, aber es gibt sauberes Wasser und hier wachsen essbare Pilze.")
    if ja_nein(mänx, "Willst du die Höhle erkunden?"):
        abzweigung = minput(mänx, "Du gehst tiefer und tiefer. Du stehst nun vor einer Abzweigung."
                            "Auf dem Schildchen über dem einen Weg steht \"bergbau\""
                            "und über dem anderen steht  \"monster\". (b/m)", ["b", "m"])

        if abzweigung == "b":
            bergbau(mänx)
        else:
            monster(mänx)
    mint("Urplötzlich fängt die Luft um dich herum an zu flimmern. Und dann...")
    mänx.welt.setzt("jtg:flimmern")
    jaspersteilgeschichte.t2(mänx)

def bergbau(mänx: Mänx):
    print("Du nimmst dir eine Spitzhacke und fängst an den Stein zu bearbeiten. Warte eine Minute.")
    sleep(61)
    mänx.inventar["Spitzhacke"] += 1
    mänx.inventar["Stein"] += 4
    minput(mänx, "Du bekommst Zeug")
    bopo = minput(mänx, "Arbeitest du weiter?", ["j", "ja", "n", "nein"])
    if bopo == "j" or "ja":
        sleep(59)
        a = random.randint(1, 120)
        if 1 <= a <= 27:
            mint("Du bekommst ein bischen Stein")
            mänx.inventar["Stein"] += 4
    
        elif 27 <= a <= 54:
            mint("Du bekommst ein wenig Stein")
            mänx.inventar["Stein"] += 5
    
        elif 54 <= a <= 81:
            mint("Du bekommst 6 Steine")
            mänx.inventar["Stein"] += 6
    
        elif 81 <= a <= 90:
            mint("Du bekommst ein bisschen Kohle")
            mänx.inventar["Kohle"] += 3
            mänx.inventar["Stein"] += 1
    
        elif 90 <= a <= 99:
            mint("Du bekommst ein wenig Kohle")
            mänx.inventar["Kohle"] += 4
            mänx.inventar["Stein"] += 1
    
        elif 99 <= a <= 108:
            mint("Du findest eine winzige Kohleader!")
            mänx.inventar["Kohle"] += 5
            mänx.inventar["Stein"] += 1
    
        elif 108 <= a <= 111:
            mint("Du findest zwei Eisenklumpen")
            mänx.inventar["Eisen"] += 2
            mänx.inventar["Stein"] += 1
    
        elif 111 <= a <= 114:
            mint("Du findest drei Eisenklumpen")
            mänx.inventar["Eisen"] += 3
            mänx.inventar["Stein"] += 1
    
        elif 114 <= a <= 117:
            mint("Du findest fünf Eisenklumpen")
            mänx.inventar["Eisen"] += 5
            mänx.inventar["Stein"] += 1
    
        elif a == 118:
            mint(
                "Du arbeitest in der Mine und bautest gerade eine Kohlemine ab, da findest du etwas:")
            mint("Du traust deinen Augen nicht: ",
                 kursiv("ein Diamant!"), "")
            mänx.inventar["Diamant"] += 1
            mänx.inventar["Kohle"] += 20
            mänx.inventar["Stein"] += 1
    
        elif a == 119:
            mint("Plötzlich stößt du auf einen Hohlraum.")
            l = input(
                'Verbreiterst du den Eingang oder fliehst du? (Schreibe "nein" für nein.) ')
            if l == "nein":
                mint("Du fliehst aus der Höhle hinaus.")
                mint("Doch kaum draußen angekommen fällst du in Ohnmacht. "
                     "Wieder aufgewacht, bist du an einem anderen Ort.")
                jaspersteilgeschichte.t2(mänx)
    
            else:
                mint("Du verbreiterst den Durchgang. "
                     "Hinter ihm findest du einen Hohlraum von der Größe eines Sarges. "
                     "Und tatsächlich: in ihm liegt eine moderige Leiche")
                mint("Und da liegt", kursiv("noch"), "etwas!")
                mint("Eine seltsame, blau schimmernde Stahlkugel!")
                print("Sie ist so etwa so groß wie ein Fußball, nur etwas kleiner.")
                mint("Außerdem hast du einen ziemlich prallen Geldbeutel entdeckt.")
                if ja_nein(mänx, "Sammelst du alles ein?"):
                    mänx.inventar["Stern des Vorvgir"] += 1
                    mänx.inventar["Gold"] += 13568
                    mänx.inventar["Eisen"] += 10
                    mänx.inventar["Stein"] += 1
                else:
                    mint("Dann eben nicht. Tja... ")
                    mint("Ich denke du solltest",
                         kursiv("woanders"), "hin...")
                    jaspersteilgeschichte.t2(mänx)
        else:
            print("Du stößt auf eine seltsam schimmernde Mauer.")
            if ja_nein(mänx, "Versuchst du sie zu durchbrechen?"):
                print(
                    "Als deine Spitzhacke die Mauer trifft, splittert sie mit einem hässlichen Kreischen.")
                mint("Aaaaaaaaaaaaaaahhhhhh!!!")
                print("Ein gellender Schrei zerreißt die Stille.")
                mint("Wer schreit denn da?!")
                print("Oh: ", kursiv("du"), "schreist da!")
                print("Die Schmerzen bringen dich um den Verstand.")
                mint("Du bist tot")
                mint("Oder etwa doch nicht?")
                mänx.inventar["Stein"] += 30
                mänx.inventar["Talisman der Schreie"] += 1
                mänx.inventar["Spitzhacke"] -= 1
                jaspersteilgeschichte.t2(mänx)
    
            else:
                print("OK dann eben nicht.")
                mint("Ich denke mal du solltest ",
                     kursiv("verschwinden!"), "")
                mänx.inventar["Stein"] += 30
                jaspersteilgeschichte.t2(mänx)
    
    else:
        mint("OK")

def monster(mänx: Mänx):
    mint("Du hörst ein Klatschen.")
    mint("Es klingt ein wenig so, wie wenn man einen nassen Frosch an eine nasse Wand wirft.")
    mint("Vorsichtig gehst du weiter.")
    a = random.randint(1, 5)
    if a == 1:
        mint("Bis plötzlich vor dir ein F®X↓ŋ auftaucht. "
             "Diese Wesen sehen eigentlich aus wie Frösche."
             "Also, wenn man mal von der Größe, "
             "der lilanen Färbung sowie der großen, haarigen und heraushängenden Zunge absieht.")

    elif a == 2:
        mint("Und hältst inne als vor dir ein Zombie aus der Dunkelheit torkelt.")

    elif a == 3:
        mint("Und bleibst stehen als vor dir das uralte Skelett eines Minotaurus,"
             "offenbar durch böse Magie wiederbelebt,"
             "aus dem Schatten trat und dabei seine anscheinend noch gut erhaltene Steitaxt schwang.")

    elif a == 4:
        mint("Ohne dir Zeit zum Reagieren zu geben,"
             "schlagen dich einige vermummten Gestalten bewusstlos und stecken dich in einen Sack.")

    elif a == 5:
        mint(
            "Vor dir tritt ein bärtiger, nach Alkohol stinkender Mann aus dem Schatten.")

    else:
        mint("Plötzlich fängst du an gewaltige Kompo-schmerzen zu haben."
             "Aber warte mal! Du ", kursiv("hast"), " ja gar keinen Kompo!"
             "Du bist schließlich ein Me, ein Män, ein Mons..."
             "Naja, irgendetwas in der Art halt."
             "Was ", kursiv("machst"), " du hier eigentlich? Du solltest schleunigst verschwinden!")
        mint("Ein Schrei entringt deiner Kehle und dir wird schwarz vor Augen.")
        mint("Als du wieder aufwachst,"
             "liegst du inmitten einer saftigen Wiese aus leuchtendem blauem Gras.")
        print("Nein... Anscheinend befindest du dich in einer Höhle.")
        mint("In einer mit leuchtend blauem Gras bewachsenen Höhle.")
        print("Und noch etwas war seltsam: "
              "Irgendwie fühlst du dich kräftiger, ", kursiv("lebendiger!"), "")
        mint("Unwillkürlich schaust du an dir herunter – Und erstarrst!")
        mint("Keine Haut mehr an deinem Fleisch, "
             "kein Fleisch mehr an deinen Knochen: "
             "Du bist ein Skelett!")
        mänx.rasse = "Skelett"
