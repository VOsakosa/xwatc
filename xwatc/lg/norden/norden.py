from xwatc.system import Mänx, minput, ja_nein, malp, Fortsetzung
from xwatc.lg.norden import gäfdah as gäfdah_module
from xwatc.weg import Eintritt, Gebiet, gebiet, Gebietsende
from xwatc.lg import mitte


norden = Eintritt("lg:norden", "süden")


@gebiet("lg:norden")
def erzeuge_norden(mänx: Mänx, gb: Gebiet) -> None:
    gäfdah = mänx.welt.get_or_else(
        "Gäfdah", gäfdah_module.erzeuge_Gäfdah, mänx)
    gb.setze_punkt((1, 1), gäfdah.draußen)
    gäfdah.draußen.verbinde(Gebietsende(
        None, gb, "süden", mitte.MITTE, "norden"), "s")
    gäfdah.draußen.add_beschreibung([
        "Du wanderst 9 Tage lang gen Norden, bis du zu einem kleinen Fischerdorf "
        "kommst."], nur="s")


def norden_alt(mänx: Mänx) -> Fortsetzung | None:
    # TODO Den Bettler wieder einbauen
    malp("Du gehst weiter und triffst auf einen Bettler.")
    if mänx.hat_item("Gold"):
        malp("Du kannst ihm ein Stück Geld geben oder weitergehen.")
        if ja_nein(mänx, "Gibst du ihm Geld?"):
            mänx.inventar["Gold"] -= 1
            malp("Der Bettler blickt dich dankend an.")
            mänx.erhalte("Stein der Bettlerfreundschaft")

    else:
        malp("Du hast leider kein Geld.")

    entscheidung = minput(mänx, "Du wanderst durch das kleine Dorf. Einige Gassenjungen "
                          "folgen dir. Bleibst du im Dorf oder gehst du weiter?", ["bleiben", "w"])
    if entscheidung == "w":
        weg = minput(mänx, "Gehst du in die Richtung aus der du gekommen bist, in eine völlig"
                     " andere oder weiter in Richtung Norden?", ["z", "w", "a"])
        if weg == "z":
            return Eintritt(mitte.MITTE, "norden")

        if weg == "a":
            k = minput(
                mänx, "Gehst du in Richtung Westen oder in Richtung Osten?", ["w", "o"])
            if k == "w":
                malp("Hallo")

        if weg == "w":
            malp("Du gehst weiter in Richtung Norden")

    elif entscheidung == "bleiben":
        pass
    return None


if __name__ == '__main__':
    from xwatc import anzeige
    anzeige.main(norden)
