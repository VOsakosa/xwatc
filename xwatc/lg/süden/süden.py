from time import sleep
from xwatc import _, kampf
from xwatc.nsc import StoryChar
from xwatc.system import SpielUnfertig, Mänx, minput, ja_nein, kursiv, mint, malp, Fortsetzung, Spielende
from xwatc.lg.osten import osten
import random
from xwatc.untersystem.person import Person, Rasse
from xwatc.weg import get_eintritt


def schnecke(mänx: Mänx) -> Fortsetzung:
    """Der Mänx kämpft gegen die Schnecke."""
    malp("Du wanderst durch fruchtbare Wiesen und Täler. Seltsam - warum siedelt hier niemand? ")
    sleep(1)
    malp("Ein Monster beantwortet deine Frage. ")
    sleep(1)
    malp("Es sieht aus wie eine riesige Schnecke. Sie brüllt.")
    mänx.welt.setze("lg:süden:kennt_schnecke")
    if "f" == mänx.minput("Kämpfst du oder fliehst du?", ["k", "f"], save=schnecke):
        malp("Du rennst und rennst vor der Schnecke weg, bis du wieder dort angekommen bist, wo "
             "alles angefangen hat")
        return rückweg
    if mänx.hat_item("Speer"):
        malp("Wirfst du deinen Speer oder versuchst du, deinen Speer in sie hineinzubohren?")
        if mänx.minput("Fernkampf oder Nahkampf?", ["Fernkampf", "Nahkampf"]) == "Fernkampf":
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
                malp("Deinen Speer bist du aber los.")
                return rückweg
        else:
            malp("Du rennst auf die Schnecke zu und schlitzt sie auf. Du wirfst dich förmlich"
                 " in sie. Die Schnecke kreischt. Dann schließlich ist sie tot.")
            return schnecke_besiegt
    elif mänx.hat_item("Messer"):
        malp("Du hast die Schnecke mit deinem Messer aufgeschlitzt. Du weichst zurück. "
             "Wieder und wieder stichst du in die Schnecke"
             "rein und hüpfst danach gleich wieder zurück. Das tust du solange, bis die Schnecke "
             "endlich tot ist.")
        return schnecke_besiegt

    elif mänx.hat_item("Spitzhacke"):
        malp("Du tötest die Schnecke mit deiner Spitzhacke")
        return schnecke_besiegt

    elif mänx.hat_item("Schwert"):
        malp("Dein Schwert fühlt sich plötzlich sehr, sehr schwer an. "
             "Als die Schnecke zu dir schleimt kanns"
             "t du dich irgendwie nicht mehr bewegen. ")
        sleep(1)
        malp("Sie frisst dich")
        raise Spielende()
    elif mänx.hat_item('Schild'):
        while minput(mänx, "Die Schnecke greift dich an, du konntest sie"
                     "gerade noch so mit deinem Schild abwehren abwehren."
                     " Hältst du weiter die Stellung oder fliehst du?",
                     ["Stellung halten", "Fliehen"]) == "Stellung halten":
            pass
        malp(
            "Du rennst weg. Zum Glück ist die Schnecke immer noch eine Schnecke und du entkommst.")
        return rückweg
    else:
        malp("Du hast keine Waffe, die gegen eine Schnecke was ausrichten könnte")
        sleep(3)
        malp("Einige Sekunden später bist du tot")
        raise Spielende()


def süden(mänx: Mänx) -> Fortsetzung:
    if not mänx.welt.ist("lg:süd:schnecke_tot"):
        return schnecke
    return monsterwellen


def rückweg(mänx: Mänx) -> Fortsetzung:
    if mänx.minput("Gehst du den selben Weg wieder zurück oder gehst du einen anderen?",
                   ["Gleicher Weg", "Anderer Weg"], save=rückweg) == "Gleicher Weg":
        from xwatc.lg.mitte import MITTE
        return get_eintritt(mänx, (MITTE, "süden"))
    else:
        malp("Du biegst leicht nach Osten ab.")
        return osten.osten


def schnecke_besiegt(mänx: Mänx) -> Fortsetzung:
    mänx.welt.setze("lg:süd:schnecke_tot")
    if ja_nein(mänx, "Weidest du die Schnecke aus?", save=schnecke_besiegt):
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
    return monsterwellen


def monsterwellen(mänx: Mänx) -> Fortsetzung:
    weg = minput(mänx, "Biegst du in Richtung Osten/Westen ab oder gehst du einfach geradeaus?",
                 ["westen", "osten", "gerade"], save=monsterwellen)
    if weg == "westen":
        return südwest
    elif weg == "osten":
        return skelett_kampf
    else:
        assert weg == "gerade"
        return salatwald


def südwest(mänx: Mänx) -> Fortsetzung:
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
    raise SpielUnfertig


skelett = StoryChar("lg:süden:skelett", "Skelett", Person("m", Rasse.Skelett), {
    "Unterhose": 1
})


def skelett_kampf(mänx: Mänx) -> Fortsetzung:
    malp(_("Ein sehr feindlich dreinblickendes Skelett kommt auf dich zu."))
    malp(_("Können Skelette überhaupt feindlich dreinblicken?"))
    if mänx.menu([("kämpfen", "k", True), ("fliehen", "f", False)],
                 _("Den Kampf kannst du vielleicht gewinnen, aber du könntest noch fliehen"),
                 save=skelett_kampf):
        if kampf.start_kampf(mänx, skelett.zu_nsc()) == kampf.Kampfausgang.Niederlage:
            malp(_("Das Skelett lacht dich aus und läuft davon."), warte=True)
        else:
            malp(_("Das Skelett fällt in sich zusammen."))
            malp(_("Komisch, denkst du dir."))
    else:
        malp(_("Das Skelett verfolgt dich nicht."))

    raise SpielUnfertig()


def salatwald(mänx: Mänx) -> Fortsetzung:
    """Ein Wald aus Salatblättern voller Schnecken und anderer Monster."""
    malp("Du erklimmst einen kleinen Hang, und findest dich auf der anderen Seite "
         "in einem Wald wieder. Aber was für einem Wald! Ein Wald aus übergroßen Salatblättern.")
    if mänx.welt.ist("lg:süden:kennt_schnecke"):
        malp("Du erwartest, dass hier auch alles voller Schnecken ist.")
    if mänx.ja_nein("Willst du doch lieber umkehren?"):
        malp("Du läufst den Weg zurück")
        return rückweg
    raise SpielUnfertig
