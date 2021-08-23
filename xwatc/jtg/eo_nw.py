"""
Die Geschichte an der Grenze von EO (nicht passierbar).
Created on 21.10.2020
"""
__author__ = "jasper"
from xwatc.system import mint, Mänx, sprich, kursiv, Spielende, malp
from xwatc.dorf import NSC, Dialog
from . import see
from .. import jtg


def eo_ww_o(mänx: Mänx):
    malp("Der Weg ist gepflastert, aber er wurde lange nicht mehr gepflegt "
          "und genutzt.")
    mint("Immer wieder musst du umgefallenen Baumstämmen ausweichen.")
    mint("Du kommst aus dem Wald in eine spärlich bewachsene Hügellandschaft.")
    malp("Ein schmaler Pfad biegt nach Süden ab.")
    opts = [
        ("Folge dem Weg nach Norden", "norden",  eo_turm),
        ("Kehre um nach Disnayenbum", "umk", jtg.disnayenbum),
        ("Biege auf den Pfad nach Süden ab", "süden", see.zugang_nord),
    ]
    mänx.menu(opts, gucken="Um dich erstreckt sich eine weite Hügellandschaft,"
              " im Norden meinst du einen Turm ausmachen zu können.")(mänx)


def eo_ww_n(mänx: Mänx):
    malp("Ein schmaler Pfad biegt nach Süden ab, der Weg macht eine Biegung "
          "nach Südosten.")
    opts = [
        ("Kehre um.", "umk",  eo_turm),
        ("Folge dem Weg", "südosten", jtg.disnayenbum),
        ("Biege auf den Pfad nach Süden ab", "süden",  see.zugang_nord),
    ]
    mänx.menu(opts, gucken="Um dich erstreckt sich eine weite Hügellandschaft,"
              " im Norden meinst du einen Turm ausmachen zu können.")(mänx)


def eo_turm(mänx: Mänx):
    malp("Der Weg führt geradewegs auf einen Turm zu.")
    mint("Dieser hohe Turm steht auf einem Hügel und kann die ganze Landschaft "
         "überblicken.")
    malp("Am Wegesrand siehst du ein Schild: "
          "\"Hier beginnt TERRITORIUM VON EO \\Betreten verboten\"")
    opts = [
        ("Umgehe den Turm weiträumig in Richtung Norden", "umgehen", eo_umgehen),
        ("Folge dem Weg auf den Turm zu", "turm", eo_turm2),
        ("Gehe zurück", "umkehren", eo_ww_n),
    ]
    mänx.menu(opts, gucken="Der Turm ragt bedrohlich vor dir auf.")(mänx)


def eo_turm2(mänx: Mänx):
    malp("Kaum kommst du in die Nähe des Turms, ruft eine laute Stimme "
          "unfreundlich herab:")
    sprich("Eo-Wache", "Kannst du nicht lesen, hier ist Territorium von Eo!")
    sprich("Eo-Wache", "Kehre um oder wir müssen Gewalt anwenden!")
    opts = [
        ('"Nein, werte Dame, ich kann nicht lesen! Tut mir leid, ich kehre'
         ' um!"', "lesen", eo_ww_n),
        ('"Das ist mir egal, ich will hier durch!"', "egal", eo_turm_kampf),
        ('"Ich habe Papiere!"', "papiere", eo_turm_kampf),
    ]
    mänx.menu(opts, gucken=[
        "Wenn du genau hinsiehst, kannst du Schießscharten "
        "am Turm ausmachen",
        "Und wenn du noch genauer hinsiehst, scheint sich "
        "dahinter etwas zu bewegen."])(mänx)


def eo_turm_kampf(mänx: Mänx):
    mint("Das scheint die Wache nicht zu überzeugen.")
    malp("Sie brüllt laut:")
    sprich("Eo-Wache", "SCHIESSEN!")
    malp("Ungefähr 10 Pfeile werden aus dem Turm abgefeuert.")
    mint("Davon durchbohren dich einige und du stirbst.")
    raise Spielende


def eo_umgehen(mänx: Mänx):
    malp("Du läufst vorsichtig in weitem Abstand um den Turm herum.")
    mint("Immer wieder blickst du dich in Richtung des Turms um.")
    if mänx.rasse == "Lavaschnecke":
        mint("Eine Stimme spricht in deinem Kopf")
        sprich("Gott der Lavaschnecken", "Du bist in Gefahr, fliehe, meine "
               "kleine Lavaschnecke!")
        if mänx.ja_nein("Fliehst du, " + kursiv("kleine Lavaschnecke") + "(LOL)?"):
            eo_flucht(mänx)
            return
    mint("Plötzlich siehst du etwas hinter dir in den Augenwinkeln.")
    mint("Ein Messer steckt in deinem Rücken.")
    sprich("Eo-Magierin", "Du bist hiermit wegen illegalen Eindringens nach "
           "Eo bestraft.")
    malp("Nun, das hast du davon, dass du auf keine Warnung hörst.")
    raise Spielende


def eo_flucht(mänx: Mänx):
    malp("Du drehst dich um, und genau vor dir taucht eine Magierin auf.")
    mänx.welt.get_or_else("jtg:eo:magierin", eo_magierin).main(mänx)
    eo_ww_n(mänx)


def mg_kampf(_nsc, _m):
    mint("Du stürmst auf sie los. Aber ihre Umrisse verzerren sich, und "
         "kaum versiehst du dich, steckt ein Messer von hinten in deiner "
         "Brust.")
    raise Spielende

def _eo_magierin_dlg():
    yield Dialog("hallo", '"Hallo!"', [
             "Nichts da 'Hallo'!", "Was suchst du hier?"])
    yield Dialog("gehe", '"Ich gehe ja schon!"', [
             "Ganz recht so. Komm nie wieder!"])
    yield Dialog("heiße", '"Ich heiße %&"%, wie heißt du?"', [
        "Ich heiße Lisc.", "Mach, dass du wegkommst."
    ])

def eo_magierin() -> NSC:
    return NSC("Lisc Śńeazrm", "Eo-Magierin", mg_kampf, dlg=_eo_magierin_dlg)
