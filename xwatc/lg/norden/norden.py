from xwatc.effect import TextGeschichte, Einmalig, NurWenn
from xwatc.lg import mitte
from xwatc.lg.norden import gäfdah as gäfdah_module
from xwatc.system import Mänx, minput, ja_nein, malp
from xwatc.weg import Eintritt, Gebiet, gebiet, Gebietsende, Wegpunkt


norden = Eintritt("lg:norden", "süden")


@gebiet("lg:norden")
def erzeuge_norden(mänx: Mänx, gb: Gebiet) -> None:
    gäfdah = gäfdah_module.erzeuge_gäfdah(mänx, gb)
    gb.setze_punkt((1, 1), gäfdah.draußen)
    gäfdah.draußen.verbinde(Gebietsende(
        None, gb, "süden", mitte.MITTE, "norden"), "s")
    gäfdah.draußen.add_beschreibung(TextGeschichte([
        "Du wanderst 9 Tage lang gen Norden, bis du zu einem kleinen Fischerdorf "
        "kommst."], zeit=9.2), nur="s")
    gäfdah.draußen.bschr(nur="s", geschichte=NurWenn(Einmalig("lg:norden:bettler"),
                                                     norden_bettler))  # type: ignore
    gäfdah.draußen.bschr("Du bist in Gäfdah.")


def norden_bettler(mänx: Mänx) -> Wegpunkt | None:
    malp("Du triffst auf einen Bettler.")
    if mänx.hat_item("Gold"):
        malp("Du kannst ihm ein Stück Geld geben oder weitergehen.")
        if ja_nein(mänx, "Gibst du ihm Geld?"):
            mänx.erhalte("Gold", -1)
            malp("Der Bettler blickt dich dankend an.")
            mänx.erhalte("Stein der Bettlerfreundschaft")

    else:
        malp("Du hast leider kein Geld, das du ihm geben könntest.")
    return None

def norden_gassen(mänx: Mänx) -> Wegpunkt | None:
    entscheidung = minput(mänx, "Du wanderst durch das kleine Dorf. Einige Gassenjungen "
                          "folgen dir. Bleibst du im Dorf oder gehst du weiter?", ["bleiben", "w"])
    if entscheidung == "w":
        weg = minput(mänx, "Gehst du in die Richtung aus der du gekommen bist, in eine völlig"
                     " andere oder weiter in Richtung Norden?", ["z", "w", "a"])
        if weg == "z":
            return Eintritt(mitte.MITTE, "norden")(mänx)

        elif weg == "a":
            k = minput(
                mänx, "Gehst du in Richtung Westen oder in Richtung Osten?", ["w", "o"])
            if k == "w":
                malp("Hallo")
                return None
            else:
                malp("")
                return None
        else:
            assert weg == "w"
            malp("Du gehst weiter in Richtung Norden, aus dem Dorf hinaus.")
            return None
    else:
        assert entscheidung == "bleiben"
        return None


if __name__ == '__main__':
    from xwatc import anzeige
    anzeige.main(norden)
