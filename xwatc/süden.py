from time import sleep
from xwatc.system import Mänx, minput, ja_nein, kursiv
from xwatc import osten
from xwatc import norden
from xwatc import westen
import xwatc_Hauptgeschichte as xwatc_haupt
import random


def süden(mänx: Mänx):
    print("Du wanderst durch fruchtbare Wiesen und Täler.Seltsam - warum siedelt hier niemand? "
          "Ein Monster beantwortet deine Frage. ")
    sleep(1)
    print("Es sieht aus wie eine riesige Schnecke.Sie brüllt.")
    mut = minput(mänx, "Kämpfst du oder fliehst du(k/f)", ["k", "f"])
    if mut == "k":
        if mänx.hat_item("Speer"):
            aa = minput(mänx, "Wirfst du deinen Speer oder versuchst du, deinen Speer in sie hineinzubohren?"
                        " f/n(Fernkampf/Nahkampf)", ["f", "n"])
            if aa == "f":
                print("Du wirfst deinen Speer. Die Schnecke brüllte, als der Speer in sie eindrang. "
                      "Doch außer das die Schnecke nun auf dich zuschleimt, hat es nichts bewirkt.")
                mänx.inventar["Speer"] -= 1
                mut = minput(mänx, "rennst du weg oder hebst du schützend "
                             "deine Arme über dem Kopf f/v(flucht/verteidigung)", ["f", "v"])
                if mut == "v":
                    print("Die Schnecke fraß dich auf, wie eine normale Schnecke Salat")
                    o = minput(mänx, "Du bist tot")
                elif mut == "f":
                    print(
                        "Du rennst weg. Zum Glück ist die Schnecke immer noch eine Schnecke und du entkommst.")
                    intelipopo = minput(mänx, "gehst du den selben Weg wieder zurück oder gehst du einen anderen"
                                        "? g/a(gleicher/anderer)", ["g", "a"])
                    if intelipopo == "g":
                        richtung = minput(mänx, "Wohin gehst du jetzt? "
                                          "In Richtung Norden ist das nächste Dorf,im Süden warten "
                                          "Monster auf dich,im Westen liegt das Meer und der "
                                          "Osten ist unentdeckt.", ["norden", "osten", "süden", "westen"])
                        if richtung == "Norden"or richtung == "norden":
                            norden.norden(mänx)
                        elif richtung == "Osten"or richtung == "osten":
                            osten.osten(mänx)
                        elif richtung == "süden":
                            süden(mänx)
                    elif intelipopo == "a":
                        osten.osten(mänx)
            else:
                print("Du rennst auf die Schnecke zu und schlitzt sie auf. Du wirfst dich förmlich"
                      " in sie. Die Schnecke kreischt. Dann, schließlich ist sie tot.")
                duhastüberlebt(mänx)
        elif mänx.hat_item("Messer"):
            print("Du hast die Schnecke mit deinem Messer aufgeschlitzt. Du we"
                  "ichst zurück. Wieder und wieder stichst du in die Schnecke"
                  "rein und hüpfst danach gleich wieder zurück. Das tus"
                  "t du solange, bis die Schnecke endlich tot ist.")
            duhastüberlebt(mänx)

        elif mänx.hat_item("Spitzhacke"):
            print("Du tötest die Schnecke mit deiner Spitzhacke")
            duhastüberlebt(mänx)

        elif mänx.hat_item("Schwert"):
            print("Dein Schwert fühlt sich plötzlich sehr, sehr schwer an. "
                  "Als die Schnecke zu dir schleimt kanns"
                  "t du dich irgendwie nicht mehr bewegen. ")
            sleep(1)
            print("Sie frisst dich")
        elif mänx.hat_item('Schild'):
            while True:
                hähä = minput(mänx, "Die Schnecke greift dich an, du konntest sie"
                              "gerade noch so mit deinem Schild abwehren abwehren."
                              " Hältst du weiter die Stellu"
                              "ng oder fliehst du? v/f (flucht/verteidigung)", ["v", "f"])
                if hähä == "f":
                    break
            print(
                "Du rennst weg. Zum Glück ist die Schnecke immer noch eine Schnecke und du entkommst.")
            intelipopo = minput(mänx, "gehst du den selben Weg wieder zurück oder gehst du einen anderen"
                                "? g/a(gleicher/anderer)", ["g", "a"])
            if intelipopo == "g":
                xwatc_haupt.himmelsrichtungen(mänx)
            else:
                osten.osten(mänx)
        else:
            print("Du hast keine Waffe, die gegen eine Schnecke was ausrichten könnte")
            sleep(3)
            print("Einige Sekunden später bist du tot")
    else:
        print("Du rennst und rennst vor"
              "der Schnecke weg, bis du"
              "wieder dort angekommen b"
              "ist, wo alles angefangen"
              "hat")
        richtung = minput(mänx, "Wohin gehst du jetzt? "
                          "In Richtung Norden ist das nächste Dorf,im Süden warten(Wie du jetzt ja weißt) "
                          "Monster auf dich,im Westen liegt das Meer und der Osten ist unentdeckt.", ["norden", "osten", "süden", "westen"])
        if richtung == "Norden" or richtung == "norden":
            norden.norden(mänx)
        elif richtung == "Osten" or richtung == "osten":
            osten.osten(mänx)
        elif richtung == "süden":
            süden(mänx)
        else:
            westen.westen(mänx)

def duhastüberlebt(mänx):
    if ja_nein(mänx, "Weidest du die Schnecke aus? "):
        print("Du bekommst ein paar Dinge")
        mänx.inventar["Schneckenschleim"] += 30
        mänx.inventar["Riesenschneckeninnereien"] += 20
        mänx.inventar["Riesenschneckenfleisch"] += 20
    mut = minput(mänx, "Gehst du weiter oder kehrst du um? w/z", ["z", "w"])
    if mut == "w":
        print("Du wagst dich tiefer ins Land der Monster.")
        weg = minput(mänx, "Biegst du in Richtung Osten/Westen "
                     "ab oder gehst du einfach geradeaus?     "
                     "w/o/we         ", ["w", "o", "we"])
        if weg == "w":
            a = random.randint(1, 11)
            if a == 1:
                print("Waldschrat (inteligent)")

            elif a == 2:
                print("Du läufst kurz herum, dann fällst du in Ohnmacht. Im Traum spricht eine Stimme zu dir:"
                      "Glückwunsch, du hast gewonnen! Eine gefühlte Ewigkeit später wachst du mit Kopfschmerzen auf.")

            elif a == 3:
                print("Wachsam gehst du weiter.")
                ark = minput(mänx, "Da bemerkst du am Horizont, ganz weit in der Ferne, einige weiß-graue Flecken.\n"
                             "Gehst du darauf zu, versuchst du sie zu umgehen "
                             "oder gehst du einfach hier und jetzt schlafen? (g/um/s)", ["g", "um", "s"])

                if ark == "g":
                    print("Als du näher kommst,"
                          "merkst du, dass es sich bei den 'Flecken' "
                          "um eine Schar pickender und gurrender Tauben handelt. "
                          "Es scheinen ganz normale Tauben zu sein. Also, abgesehen davon, dass sie etwa so groß wie Pferde sind.")
                    if "Mit Tieren reden" in mänx.fähigkeiten:
                        print(
                            "Dank deiner Fähigkeit mit Tieren zu reden, schnappst einige Worte auf.")

                elif ark == "um":
                    input("Immer darauf achtend, dass die 'Flecken' ", kursiv("ganz"),
                          "weit weg von dir blieben, versuchst du sie zu umgehen...")
                    input('Da merkst du plötzlich, dass sich jemand von hinten an dich heranschleicht,'
                          'doch zu spät: Dieser Jemand haut dir auf den Kopf und du wirst ohnmächtig.')

                elif ark == "s":
                    input(
                        "Du suchst dir eine Mulde, kleidest sie mit Blättern aus und schläfst ein.")
                    print(
                        "Als du am nächsten Morgen aufwachst, sind die 'Flecken' nicht mehr zu sehen...")

            elif a == 4:
                print('Du läufst kurz herum, dann fällst du in Ohnmacht. Im Traum spricht eine Stimme zu dir:'
                      'Juhu! du hast gewonnen! Eine gefühlte Ewigkeit später wachst du mit Kopfschmerzen auf.')

            elif a == 5:
                print(kursiv(
                    "Hallo"), "spricht plötzlich eine Stimme in deinem Kopf. Dann ist es wieder still.")

            elif a == 6:
                print('JOEL schlägt zu.'
                      'Tut mir wirklich sehr Leid, '
                      'aber die Superentität JOEL, '
                      'auch genannt böse-böser-Unsinn-Enttität, '
                      'ist zu stark.')
                print("Das Gift der Schneckekommt in deinen Körper.Harharhar!"
                      "lacht das minigehirn der Schnecke Schade, leider bist du tot")

            elif a == 7:
                print("Riesige Spinne")

            elif a == 8:
                print("Plötzlich wird dir kotzübel."
                      "Dir ist als würde eine Stimme zu dir sprechen, bzw. dich anschreien: "
                      "Du hast gewonnen, VERDAMMT!!! LASS MICH in RUHE!!! "
                      "Dann bleibst du alleine und mit Kopfschmerzen zurück.")

            elif a == 9:
                print("Panti-Jäger")

            elif a == 10:
                print("Pferdegroßer Wolf")

            else:
                print("Fleischfressende Pflanze")

    elif mut == "z":
        xwatc_haupt.himmelsrichtungen(mänx)

    # elif mut=="z":
