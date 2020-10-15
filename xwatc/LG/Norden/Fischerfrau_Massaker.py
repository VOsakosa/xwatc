"""Der Teil von Norden, wo Waffen getestet werden. Hauptsächlich an einer Fischerfrau in einem Dorf im Binnenland."""
from xwatc.system import minput, Mänx, Spielende, mint


def fischerfraumassaker(mänx: Mänx) -> None:
    if mänx.hat_item("Speer"):
        Kampf = minput(mänx, "Du bohrst der Alten deinen Speer in den Rücken, worauf sie mit entsetzten Augen "
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
        Kamf = minput(mänx, "parierenundstechen/fliehen/parieren (ps/f/p")
    elif mänx.hat_item("Schwert"):
        schwert_massaker(mänx)
    elif mänx.hat_item("Spitzhacke"):
        print("Du tötest die arme Frau mit einem einzigen wohlplazierten Schlag deiner Spitzhacke")
        mänx.welt.setze("Fischerfrautot")

    else:  # Leere
        print("Du stürzt dich auf die alte Frau und schlägst auf sie ein."
              "Sie kreischt und - stößt dir ein Messer in den Bauch. Du starrst entsetzt auf die Wunde"
              ", Blut rinnt aus ihr. Ein paar Sekunden später bist du tot.")
        mänx.welt.setze("Fischerfraugewarnt")
        raise Spielende()


def schwert_massaker(mänx: Mänx) -> None:
    from xwatc_Hauptgeschichte import himmelsrichtungen
    print("Du streckst die Alte mit deinem Schwert nieder, worauf es dunkelrot "
          "zu pulsieren anfängt. Du lachst bösartig wärend "
          "sich über dir Gewitterwolken sammeln. Die Wachen weichen angsterfüllt zurück.")
    massaker = minput(mänx, "Greifst du sie an, gehst du weg oder raubst du die Fischverkäuferin aus?a/w/au "
                      "(angreifen/weggehen/ausrauben)", ["a", "w", "au"])
    mänx.welt.setze("Fischerfrauschwerttot")

    if massaker == "a":
        print("Ein Blitz fährt herab und streckt einen Wächter "
              "nieder. Der andere will fliehen, doch dein Schwe"
              "rt fliegt dir aus der Hand und steckt nun in sei"
              "ner Brust.")
        a = minput(mänx, "Raubst du erst einmal alles aus,"
                   "bringst du die anderen Leute im Dorf u"
                   "m oder gehst du weg?r/u/w (räubern/umb"
                   "ringen/weggehen)", ["r", "w", "u"])
        if a == "r":
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
        elif a == "w":
            print("Du bist wieder dort wo "
                  "alles anfing. Nun stehs"
                  "t du vor einer Lebensve"
                  "rändernden Entscheidung.")
            weg = minput(
                mänx, "Schmeißt du das Schwert weg oder nicht?j/n", ["j", "n"])

            if weg == "j":
                print("Es ist als würde eine schwere Last von dir abfallen.")

                mänx.inventar["Schwert"] -= 1
                himmelsrichtungen(mänx)
            else:  # elif weg=="n":
                print("Du grinst. Und eine Stimme meldet sich "
                      "in den Tiefen von dir. Du spürst wie et"
                      "was dein Gewissen auffrisst. Die Stimme"
                      "fängt an zu lachen. Dieses Lachen... wa"
                      "r eindeutig böse und skrupellos. Und du"
                      "... stimmst in das Lachen ein.")
                himmelsrichtungen(mänx)

    elif massaker == "au":
        print("Du bekommst eine Menge Zeug")
        mänx.inventar["Hering"] += 4
        mänx.inventar["Scholle"] += 5
        mänx.inventar["Sardine"] += 6
        mänx.inventar["Messer"] += 1
        mint("Eine mutige Wache sticht dir in den Rücken und du stirbst.")
        mint("Tja... Pass in Zukunft auf, anstatt dir feindlich gesinnten Wachen den Rücken zu zeigen...")
        raise Spielende

    elif massaker == "w":
        print("Du bist wieder dort wo "
              "alles anfing. Nun stehs"
              "t du vor einer Lebensve"
              "rändernden Entscheidung.")
        weg = minput(
            mänx, "Schmeißt du das Schwert weg oder nicht?j/n", ["j", "n"])

        if weg == "j":
            print("Es ist als würde eine schwere Last von dir abfallen.")

            mänx.inventar["Schwert"] -= 1
            himmelsrichtungen(mänx)
        else:  # elif weg=="n":
            print("Du grinst. Und eine Stimme meldet sich "
                  "in den Tiefen von dir. Du spürst wie et"
                  "was dein Gewissen auffrisst. Die Stimme"
                  "fängt an zu lachen. Dieses Lachen wa"
                  "r eindeutig böse und skrupellos. Und du"
                  " stimmst in das Lachen ein.")
            himmelsrichtungen(mänx)
