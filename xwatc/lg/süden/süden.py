from time import sleep
from xwatc import _, kampf
from xwatc.nsc import StoryChar
from xwatc.system import Mänx, minput, ja_nein, kursiv, mint, malp, Fortsetzung, Spielende
from xwatc.lg.osten import osten
import random
from xwatc.untersystem.person import Person, Rasse
from xwatc.weg import get_eintritt


def süden(mänx: Mänx) -> Fortsetzung:
    malp("Du wanderst durch fruchtbare Wiesen und Täler. Seltsam - warum siedelt hier niemand? ")
    mänx.sleep(1, "")
    malp("Ein Monster beantwortet deine Frage. ")
    mänx.sleep(1, "")
    malp("Es sieht aus wie eine riesige Schnecke. Sie brüllt.")
    mut = minput(mänx, "Kämpfst du oder fliehst du?", ["k", "f"])
    if mut == "k":
        if mänx.hat_item("Speer"):
            malp("Wirfst du deinen Speer oder versuchst du, deinen Speer in sie hineinzubohren?")
            aa = mänx.minput("Fernkampf[f] oder Nahkampf[n]?", ["f", "n"])
            if aa == "f":
                malp("Du wirfst deinen Speer. Die Schnecke brüllte, als der Speer in sie eindrang. "
                     "Doch außer das die Schnecke nun auf dich zuschleimt, hat es nichts bewirkt.")
                mänx.erhalte("Speer", -1)
                mut = minput(mänx, "Rennst du weg oder hebst du schützend "
                             "deine Arme über dem Kopf f/v(flucht/verteidigung)", ["f", "v"])
                if mut == "v":
                    malp("Die Schnecke fraß dich auf, wie eine normale Schnecke Salat")
                    mint("Du bist tot")
                    raise Spielende()
                else:
                    assert mut == "f"
                    malp("Du rennst weg. Zum Glück ist die Schnecke immer noch eine Schnecke "
                         "und du entkommst.")
                    return rückweg
            else:
                malp("Du rennst auf die Schnecke zu und schlitzt sie auf. Du wirfst dich förmlich"
                     " in sie. Die Schnecke kreischt. Dann, schließlich ist sie tot.")
                return duhastüberlebt
        elif mänx.hat_item("Messer"):
            malp("Du hast die Schnecke mit deinem Messer aufgeschlitzt. Du we"
                 "ichst zurück. Wieder und wieder stichst du in die Schnecke"
                 "rein und hüpfst danach gleich wieder zurück. Das tus"
                 "t du solange, bis die Schnecke endlich tot ist.")
            return duhastüberlebt

        elif mänx.hat_item("Spitzhacke"):
            malp("Du tötest die Schnecke mit deiner Spitzhacke")
            return duhastüberlebt

        elif mänx.hat_item("Schwert"):
            malp("Dein Schwert fühlt sich plötzlich sehr, sehr schwer an. "
                 "Als die Schnecke zu dir schleimt kanns"
                 "t du dich irgendwie nicht mehr bewegen. ")
            sleep(1)
            malp("Sie frisst dich")
            raise Spielende()
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
            return rückweg
        else:
            malp("Du hast keine Waffe, die gegen eine Schnecke was ausrichten könnte")
            sleep(3)
            malp("Einige Sekunden später bist du tot")
            raise Spielende()
    else:
        malp("Du rennst und rennst vor"
             "der Schnecke weg, bis du"
             "wieder dort angekommen b"
             "ist, wo alles angefangen"
             "hat")
        return rückweg


def rückweg(mänx: Mänx) -> Fortsetzung:
    intelipopo = minput(mänx, "gehst du den selben Weg wieder zurück oder gehst du einen anderen"
                        "? g/a(gleicher/anderer)", ["g", "a"])
    if intelipopo == "g":
        from xwatc.lg.mitte import MITTE
        return get_eintritt(mänx, (MITTE, "süden"))
    else:
        return osten.osten


def duhastüberlebt(mänx: Mänx) -> Fortsetzung:
    if ja_nein(mänx, "Weidest du die Schnecke aus? "):
        malp("Du bekommst ein paar Dinge.")
        mänx.erhalte("Schneckenschleim", 30)
        mänx.erhalte("Riesenschneckeninnereien", 20)
        mänx.erhalte("Riesenschneckenfleisch", 20)
    mut = minput(mänx, "Gehst du weiter oder kehrst du um?", ["zurück", "weiter"])
    if mut == "zurück":
        from xwatc.lg.mitte import MITTE
        return get_eintritt(mänx, (MITTE, "süden"))
    assert mut == "weiter"
    malp("Du wagst dich tiefer ins Land der Monster.")
    weg = minput(mänx, "Biegst du in Richtung Osten/Westen ab oder gehst du einfach geradeaus?",
                 ["westen", "osten", "gerade"])
    if weg == "westen":
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
                if mänx.hat_item("Mugel des Sprechens"):
                    malp(
                        "Dank deiner Fähigkeit mit Tieren zu reden, schnappst einige Worte auf.")

            elif ark == "um":
                mänx.minput("Immer darauf achtend, dass die 'Flecken' " + kursiv("ganz") +
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
            raise Spielende()
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
    elif weg == "osten":
        malp(_("Ein sehr feindlich dreinblickendes Skelett kommt auf dich zu."))
        malp(_("Können Skelette überhaupt feindlich dreinblicken?"))
        if mänx.menu([("kämpfen", "k", True), ("fliehen", "f", False)],
                     _("Den Kampf kannst du vielleicht gewinnen, aber du könntest noch fliehen")):
            if kampf.start_kampf(mänx, skelett.zu_nsc()) == kampf.Kampfausgang.Niederlage:
                malp(_("Das Skelett lacht dich aus und läuft davon."), warte=True)
            else:
                malp(_("Komisch, denkst du dir."))
        else:
            malp(_("Das Skelett verfolgt dich nicht."))
    raise Spielende()

    # elif mut=="z":


skelett = StoryChar("lg:süden:skelett", "Skelett", Person("m", Rasse.Skelett), {
    "Unterhose": 1
})
