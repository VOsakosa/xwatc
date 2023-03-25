from time import sleep
from xwatc.system import Mänx, minput, ja_nein, kursiv, mint, malp
from xwatc.lg.osten import osten
from xwatc.lg.norden import norden
from xwatc.lg.westen import westen
import xwatc_Hauptgeschichte as xwatc_haupt
import random


def süden(mänx: Mänx):
    malp("Du wanderst durch fruchtbare Wiesen und Täler.Seltsam - warum siedelt hier niemand? "
          "Ein Monster beantwortet deine Frage. ")
    sleep(1)
    malp("Es sieht aus wie eine riesige Schnecke.Sie brüllt.")
    mut = minput(mänx, "Kämpfst du oder fliehst du(k/f)", ["k", "f"])
    if mut == "k":
        if mänx.hat_item("Speer"):
            aa = minput(mänx, "Wirfst du deinen Speer oder versuchst du, deinen Speer in sie hineinzubohren?"
                        " f/n(Fernkampf/Nahkampf)", ["f", "n"])
            if aa == "f":
                malp("Du wirfst deinen Speer. Die Schnecke brüllte, als der Speer in sie eindrang. "
                      "Doch außer das die Schnecke nun auf dich zuschleimt, hat es nichts bewirkt.")
                mänx.inventar["Speer"] -= 1
                mut = minput(mänx, "rennst du weg oder hebst du schützend "
                             "deine Arme über dem Kopf f/v(flucht/verteidigung)", ["f", "v"])
                if mut == "v":
                    malp("Die Schnecke fraß dich auf, wie eine normale Schnecke Salat")
                    mint("Du bist tot")
                elif mut == "f":
                    malp(
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
                malp("Du rennst auf die Schnecke zu und schlitzt sie auf. Du wirfst dich förmlich"
                      " in sie. Die Schnecke kreischt. Dann, schließlich ist sie tot.")
                duhastüberlebt(mänx)
        elif mänx.hat_item("Messer"):
            malp("Du hast die Schnecke mit deinem Messer aufgeschlitzt. Du we"
                  "ichst zurück. Wieder und wieder stichst du in die Schnecke"
                  "rein und hüpfst danach gleich wieder zurück. Das tus"
                  "t du solange, bis die Schnecke endlich tot ist.")
            duhastüberlebt(mänx)

        elif mänx.hat_item("Spitzhacke"):
            malp("Du tötest die Schnecke mit deiner Spitzhacke")
            duhastüberlebt(mänx)

        elif mänx.hat_item("Schwert"):
            malp("Dein Schwert fühlt sich plötzlich sehr, sehr schwer an. "
                  "Als die Schnecke zu dir schleimt kanns"
                  "t du dich irgendwie nicht mehr bewegen. ")
            sleep(1)
            malp("Sie frisst dich")
        elif mänx.hat_item('Schild'):
            while True:
                hähä = minput(mänx, "Die Schnecke greift dich an, du konntest sie"
                              "gerade noch so mit deinem Schild abwehren abwehren."
                              " Hältst du weiter die Stellu"
                              "ng oder fliehst du? v/f (flucht/verteidigung)", ["v", "f"])
                if hähä == "f":
                    break
            malp(
                "Du rennst weg. Zum Glück ist die Schnecke immer noch eine Schnecke und du entkommst.")
            intelipopo = minput(mänx, "gehst du den selben Weg wieder zurück oder gehst du einen anderen"
                                "? g/a(gleicher/anderer)", ["g", "a"])
            if intelipopo == "g":
                xwatc_haupt.himmelsrichtungen(mänx)
            else:
                osten.osten(mänx)
        else:
            malp("Du hast keine Waffe, die gegen eine Schnecke was ausrichten könnte")
            sleep(3)
            malp("Einige Sekunden später bist du tot")
    else:
        malp("Du rennst und rennst vor"
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
        malp("Du bekommst ein paar Dinge")
        mänx.inventar["Schneckenschleim"] += 30
        mänx.inventar["Riesenschneckeninnereien"] += 20
        mänx.inventar["Riesenschneckenfleisch"] += 20
    mut = minput(mänx, "Gehst du weiter oder kehrst du um? w/z", ["z", "w"])
    if mut == "w":
        malp("Du wagst dich tiefer ins Land der Monster.")
        weg = minput(mänx, "Biegst du in Richtung Osten/Westen "
                     "ab oder gehst du einfach geradeaus?     "
                     "w/o/we         ", ["w", "o", "we"])
        if weg == "w":
            a = random.randint(1, 11)
            if a == 1:
                malp("Waldschrat (inteligent)")

            elif a == 2:
                malp("Du läufst kurz herum, dann fällst du in Ohnmacht. Im Traum spricht eine Stimme zu dir:"
                      "Glückwunsch, du hast gewonnen! Eine gefühlte Ewigkeit später wachst du mit Kopfschmerzen auf.")

            elif a == 3:
                malp("Wachsam gehst du weiter.")
                ark = minput(mänx, "Da bemerkst du am Horizont, ganz weit in der Ferne, einige weiß-graue Flecken.\n"
                             "Gehst du darauf zu, versuchst du sie zu umgehen "
                             "oder gehst du einfach hier und jetzt schlafen? (g/um/s)", ["g", "um", "s"])

                if ark == "g":
                    malp("Als du näher kommst,"
                          "merkst du, dass es sich bei den 'Flecken' "
                          "um eine Schar pickender und gurrender Tauben handelt. "
                          "Es scheinen ganz normale Tauben zu sein. Also, abgesehen davon, dass sie etwa so groß wie Pferde sind.")
                    if "Mit Tieren reden" in mänx.fähigkeiten:
                        malp(
                            "Dank deiner Fähigkeit mit Tieren zu reden, schnappst einige Worte auf.")

                elif ark == "um":
                    mänx.minput("Immer darauf achtend, dass die 'Flecken' ", kursiv("ganz"),
                          "weit weg von dir blieben, versuchst du sie zu umgehen...")
                    input('Da merkst du plötzlich, dass sich jemand von hinten an dich heranschleicht,'
                          'doch zu spät: Dieser Jemand haut dir auf den Kopf und du wirst ohnmächtig.')

                elif ark == "s":
                    input(
                        "Du suchst dir eine Mulde, kleidest sie mit Blättern aus und schläfst ein.")
                    malp(
                        "Als du am nächsten Morgen aufwachst, sind die 'Flecken' nicht mehr zu sehen...")

            elif a == 4:
                malp('Du läufst kurz herum, dann fällst du in Ohnmacht. Im Traum spricht eine Stimme zu dir:'
                      'Juhu! du hast gewonnen! Eine gefühlte Ewigkeit später wachst du mit Kopfschmerzen auf.')

            elif a == 5:
                malp(kursiv(
                    "Hallo"), "spricht plötzlich eine Stimme in deinem Kopf. Dann ist es wieder still.")

            elif a == 6:
                malp('JOEL schlägt zu.'
                      'Tut mir wirklich sehr Leid, '
                      'aber die Superentität JOEL, '
                      'auch genannt böse-böser-Unsinn-Entität, '
                      'ist zu stark.')
                mint("Das Gift der Schnecke kommt in deinen Körper.Harharhar!"
                     "lacht das Minigehirn der Schnecke Schade, leider bist du tot")
                mint("Joel hat zugeschlagen.")
                mint("Es tut mir wirklich ", kursiv("sehr"), "leid.")

            elif a == 7:
                malp("Riesige Spinne")

            elif a == 8:
                malp("Plötzlich wird dir kotzübel."
                      "Dir ist als würde eine Stimme zu dir sprechen, bzw. dich anschreien: "
                      "Du hast gewonnen, VERDAMMT!!! LASS MICH in RUHE!!! "
                      "Dann bleibst du alleine und mit Kopfschmerzen zurück.")

            elif a == 9:
                malp("Panti-Jäger")

            elif a == 10:
                malp("Pferdegroßer Wolf")

            else:
                malp("Fleischfressende Pflanze")

    elif mut == "z":
        xwatc_haupt.himmelsrichtungen(mänx)

    # elif mut=="z":
