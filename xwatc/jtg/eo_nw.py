"""
Die Geschichte an der Grenze von EO (nicht passierbar).
Created on 21.10.2020
"""
from xwatc import jtg
from xwatc.jtg import see, nord
from xwatc.nsc import StoryChar
from xwatc.system import mint, Mänx, sprich, kursiv, Spielende, malp, MenuOption
from xwatc.untersystem.person import Rasse
from xwatc.weg import gebiet, Gebiet, WegAdapter, Eintritt

from typing import NoReturn


__author__ = "Jasper Ischebeck"

eo_nw_ost = Eintritt(("jtg:eo_nw", "eo_nw"))

@gebiet("jtg:eo_nw")
def eo_nw(mänx: Mänx, gb: Gebiet) -> None:
    ww = gb.neuer_punkt((2, 3), "kreuzung")
    ww.verbinde(gb.ende(eo_nw_ost, nord.eintritt_west), "so", "Disnayenbum")
    ww.add_beschreibung([
        "Der Weg ist gepflastert, aber er wurde lange nicht mehr gepflegt "
        "und genutzt.",
        "Immer wieder musst du umgefallenen Baumstämmen ausweichen.",
        "Du kommst aus dem Wald in eine spärlich bewachsene Hügellandschaft."
        "Ein schmaler Pfad biegt nach Süden ab."
    ], nur="so")
    ww.add_beschreibung([
        "Ein schmaler Pfad biegt nach Süden ab, der Weg macht eine Biegung "
        "nach Südosten."
    ], nur="n")
    ww.add_beschreibung(
        "Dein Pfad stößt auf einen Weg von Norden nach Südosten."
    )
    ww.add_option("Gucken", "gucken", "Um dich erstreckt sich eine weite Hügellandschaft, "
                  "im Norden meinst du einen Turm ausmachen zu können.")
    schild = gb.neuer_punkt((2, 2), "warnschild")
    schild.add_beschreibung([
        "Der Weg führt geradewegs auf einen Turm zu.",
        "Dieser hohe Turm steht auf einem Hügel und kann die ganze Landschaft überblicken."
    ], nur="s")
    schild.add_beschreibung(
        "Am Wegesrand siehst du ein Schild: "
        "\"Hier beginnt TERRITORIUM VON EO \\Betreten verboten\"")
    schild.add_beschreibung(
        "Es scheint einen Weg rechts am Turm vorbei zu geben.")
    schild.add_beschreibung("Der Turm ragt bedrohlich vor dir auf.")
    gb.neuer_punkt((3, 2), "Bogen", immer_fragen=False)
    gb.neuer_punkt((3, 1), "Umgehung").add_beschreibung(eo_umgehen)
    turm = gb.neuer_punkt((2, 1), "vor_turm")
    turm.add_beschreibung(eo_turm)

    zu_see = gb.neuer_punkt((0, 3), "zu_see", immer_fragen=False)
    zu_see.verbinde(WegAdapter(see.zugang_nord, "see", gb), "w")
    zu_see.add_beschreibung("Der Pfad windet sich durch die Hügellandschaft.")


def eo_turm(mänx: Mänx) -> None:
    malp("Kaum kommst du in die Nähe des Turms, ruft eine laute Stimme "
         "unfreundlich herab:")
    sprich("Eo-Wache", "Kannst du nicht lesen, hier ist Territorium von Eo!")
    sprich("Eo-Wache", "Kehre um oder wir müssen Gewalt anwenden!")
    ans = 0
    while not ans:
        opts: list[MenuOption[int]] = [
            ('"Nein, werte Dame, ich kann nicht lesen! Tut mir leid, ich kehre'
             ' um!"', "lesen", 1),
            ('"Das ist mir egal, ich will hier durch!"', "egal", 2),
            ('"Ich habe Papiere!"', "papiere", 2),
            ("Gucken", "gucken", 0),
        ]
        ans = mänx.menu(opts)
        if ans == 0:
            malp("Wenn du genau hinsiehst, kannst du Schießscharten am Turm ausmachen")
            malp("Und wenn du noch genauer hinsiehst, scheint sich "
                 "dahinter etwas zu bewegen.")
    if ans == 2:
        eo_turm_kampf(mänx)


def eo_turm_kampf(_mänx: Mänx) -> NoReturn:
    mint("Das scheint die Wache nicht zu überzeugen.")
    malp("Sie brüllt laut:")
    sprich("Eo-Wache", "SCHIESSEN!")
    malp("Ungefähr 10 Pfeile werden aus dem Turm abgefeuert.")
    mint("Davon durchbohren dich einige und du stirbst.")
    raise Spielende


def eo_umgehen(mänx: Mänx) -> None:
    malp("Du läufst vorsichtig in weitem Abstand um den Turm herum.")
    mint("Immer wieder blickst du dich in Richtung des Turms um.")
    if mänx.rasse == Rasse.Lavaschnecke:
        mint("Eine Stimme spricht in deinem Kopf")
        sprich("Gott der Lavaschnecken", "Du bist in Gefahr, fliehe, meine "
               "kleine Lavaschnecke!")
        if mänx.ja_nein("Fliehst du, " + kursiv("kleine Lavaschnecke") + "(LOL)?"):
            malp("Du drehst dich um, und genau vor dir taucht eine Magierin auf.")
            mänx.welt.obj("jtg:eo:magierin").main(mänx)
            return None
    mint("Plötzlich siehst du etwas hinter dir in den Augenwinkeln.")
    mint("Ein Messer steckt in deinem Rücken.")
    sprich("Eo-Magierin", "Du bist hiermit wegen illegalen Eindringens nach "
           "Eo bestraft.")
    malp("Nun, das hast du davon, dass du auf keine Warnung hörst.")
    raise Spielende


magierin = StoryChar("jtg:eo:magierin", ("Liść", "Śńeazrm", "Eo-Magierin"))


@magierin.kampf
def mg_kampf(_nsc, _m) -> NoReturn:
    mint("Du stürmst auf sie los. Aber ihre Umrisse verzerren sich, und "
         "kaum versiehst du dich, steckt ein Messer von hinten in deiner "
         "Brust.")
    raise Spielende


magierin.dialog("hallo", '"Hallo!"', [
    "Nichts da 'Hallo'!", "Was suchst du hier?"])
magierin.dialog("gehe", '"Ich gehe ja schon!"', [
    "Ganz recht so. Komm nie wieder!"], "hallo")
magierin.dialog("heiße", '"Ich heiße %&"%, wie heißt du?"', [
    "Ich heiße Liść.", "Mach, dass du wegkommst."
])

if __name__ == '__main__':
    from xwatc.anzeige import main
    main(eo_nw_ost)
