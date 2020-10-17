from time import sleep
import xwatc_Hauptgeschichte as xwatc
from xwatc.system import Mänx, minput, Gefährte, ja_nein, Spielende
from xwatc.lg.norden.Fischerfrau_Massaker import fischerfraumassaker


def norden(mänx):
    print("Du wanderst 9 Tage lang gen Norden, bis du zu einem kleinen Fischerdorf "
          "kommst.")

    while True:
        antwort = minput(mänx, "Willst du handeln, reden, sie angreifen oder einfach weitergehen? (h/r/a/w)",
                         ["h", "a", "w", "r"])
        if antwort == "h":
            if mänx.inventar["Gold"] >= 5:
                fisch = minput(mänx, "Du kannst eine Scholle, eine Sardine oder einen Hering kaufen. "
                               "abbrechen/Scholle/Sardine/Hering", ["abbrechen", "scholle", "sardine", "hering"])
                if fisch != "abbrechen":
                    mänx.inventar[fisch.capitalize()] += 1
                    mänx.inventar["Gold"] -= 5
            else:
                print("Du hast nicht genug Geld dafür")
        else:
            break
    if antwort == "w":
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

        entscheidung = minput(mänx, "Du wanderst durch das kleine Dorf. Einige Gassenjungen "
                              "folgen dir. Bleibst du im Dorf oder gehst du weiter? "
                              "bleiben/w", ["bleiben", "w"])
        if entscheidung == "w":
            weg = minput(mänx, "Gehst du in die R"
                         "ichtung aus der du gekom"
                         "men bist, in eine völlig"
                         " andere oder weiter in Ri"
                         "chtung Norden? z/a/w"
                         "zurück/anders/weiter", ["z", "w", "a"])
            if weg == "z":
                xwatc.himmelsrichtungen(mänx)

            if weg == "a":
                k = minput(
                    mänx, "Gehst du in Richtung Westen oder in Richtung Osten? (w/o", ["w", "o"])
                if k == "w":
                    print("Hallo")

            if weg == "w":
                print("Du gehst weiter in Richtung Norden")

        elif entscheidung == "bleiben":
            pass

    elif antwort == "a":
        fischerfraumassaker(mänx)

        # mänx.inventar_leeren()

        # waffe_wählen(mänx)
