from xwatc.system import Mänx, minput, kursiv, ja_nein, mint, Spielende, malp, Fortsetzung
import random
from xwatc import jtg
from xwatc.weg import gebiet, Gebiet, Gebietsende, WegAdapter, kreuzung
from xwatc.effect import Einmalig, NurWenn, Zufällig, Warten, TextGeschichte, in_folge


@gebiet("lg:osten")
def osten(_mänx: Mänx, gb: Gebiet) -> None:
    treffpunkt = gb.neuer_punkt((0, 1), "treffpunkt")
    treffpunkt.add_beschreibung([
        "Du wanderst lange, lange in Richtung Osten, "
        "dein Proviant ist aufgebraucht, dein Mund trocken und"
        " dein Magen knurrt.",
        "Es ist heiß, höllisch heiß. Im Süden in der Ferne siehst du einen Höhleneingang."
        "In der anderen Richtung"
        " siehst du etwas das wie eine Oase aussieht."
    ], nur="w")
    treffpunkt.verbinde(Gebietsende(
        None, gb, "start", "lg:mitte", "osten"), "w")

    oase = gb.neuer_punkt((0, 0), "Oase")
    oase.add_beschreibung(NurWenn(Einmalig("lg:osten:oase_besucht"), [
        "Du läufst zur Oase, aber als du dort ankommst ist sie weg. An ihrer Stelle "
        "stehen dort zwei Türen.",
        "Eine Inschrift verkündet: Die eine in den Tode führet, "
        "die andre zu nem andren Ort."
    ], [
        "Die beiden Türen sind noch da."
    ]))
    oase.verbinde(WegAdapter(None, t1), "Linke Tür")
    oase.verbinde(WegAdapter(None, t2), "Rechte Tür")

    höhleneingang = gb.neuer_punkt((0, 2), "Höhleneingang")
    höhleneingang.add_beschreibung(
        "Du kommst an einen Höhleneingang.", nur="w")
    höhleneingang.add_beschreibung([
        "Die Höhle ist ein riesiges, dunkles Loch, das sich tief ins Erdreich auszubreiten "
        "scheint."], außer="Höhle")
    höhleneingang.add_beschreibung(
        "Dir schlägt die Hitze von draußen entgegen.", nur="Höhle")

    höhle = kreuzung("Höhlenabzweig")
    höhle - höhleneingang
    höhle.add_beschreibung([
        "In der Höhle ist es dunkel, aber es gibt sauberes Wasser und "
        "hier wachsen essbare Pilze.",
        "Du gehst tiefer und tiefer. Du stehst nun vor einer Abzweigung.",
        "Auf dem Schildchen über dem einen Weg steht \"bergbau\" "
        "und über dem anderen steht \"monster\"."], nur="Höhleneingang")
    höhle.add_beschreibung(
        "Du bist zurück an der Abzweigung.", außer="Höhleneingang")
    höhle.verbinde(WegAdapter(None, monster, "monster", gb), "Monster")

    bergbau = kreuzung("Bergbau", immer_fragen=True)
    bergbau.add_beschreibung(
        NurWenn(Einmalig("lg:osten:bergbau_getan"), TextGeschichte([
            "Du nimmst dir eine Spitzhacke und fängst an, den Stein zu bearbeiten. Warte eine Minute.",
            Warten(61),
            "Du bekommst Zeug."
        ], schatz={"Spitzhacke": 1, "Stein": 4}), in_folge(
            ["Du arbeitest weiter.", Warten(59)], Zufällig.ungleichmäßig(
                (27, TextGeschichte(
                    ["Du bekommst ein bisschen Stein."], schatz={"Stein": 4})),
                (27, TextGeschichte(
                    ["Du bekommst ein wenig Stein."], schatz={"Stein": 5})),
                (27, TextGeschichte(
                    ["Du bekommst ein viel Stein."], schatz={"Stein": 6})),
                (9, TextGeschichte(
                    ["Du bekommst ein bisschen Kohle."], schatz={"Kohle": 3, "Stein": 1})),
                (9, TextGeschichte(
                    ["Du bekommst ein wenig Kohle."], schatz={"Kohle": 4, "Stein": 1})),
                (9, TextGeschichte(
                    ["Du findest eine winzige Kohleader!"], schatz={"Kohle": 5, "Stein": 1})),
                (3, TextGeschichte(
                    ["Du findest zwei Eisenklumpen."], schatz={"Eisen": 2, "Stein": 1})),
                (3, TextGeschichte(
                    ["Du findest drei Eisenklumpen."], schatz={"Eisen": 3, "Stein": 1})),
                (3, TextGeschichte(
                    ["Du findest fünf Eisenklumpen."], schatz={"Eisen": 5, "Stein": 1})),
                (1, TextGeschichte(["Du arbeitest in der Mine und bautest gerade eine Kohlemine "
                                    "ab, da findest du etwas:",
                                    "Du traust deinen Augen nicht: " + kursiv("ein Diamant!")],
                                   schatz={"Diamant": 1, "Kohle": 20, "Stein": 1})
                 ),
                (1, hohlraum),
                (1, schimmernde_mauer),
            ))))
    höhle - bergbau


def hohlraum(mänx: Mänx) -> Fortsetzung | None:
    mint("Plötzlich stößt du auf einen Hohlraum.")
    if not mänx.ja_nein('Verbreiterst du den Eingang oder fliehst du?'):
        mint("Du fliehst aus der Höhle hinaus.")
        mint("Doch kaum draußen angekommen fällst du in Ohnmacht. "
             "Wieder aufgewacht, bist du an einem anderen Ort.")
        # JTG
        return jtg.t2
    else:
        mint("Du verbreiterst den Durchgang. "
             "Hinter ihm findest du einen Hohlraum von der Größe eines Sarges. "
             "Und tatsächlich: in ihm liegt eine moderige Leiche")
        mint("Und da liegt", kursiv("noch"), "etwas!")
        mint("Eine seltsame, blau schimmernde Stahlkugel!")
        malp("Sie ist so etwa so groß wie ein Fußball, nur etwas kleiner.")
        mint("Außerdem hast du einen ziemlich prallen Geldbeutel entdeckt.")
        if ja_nein(mänx, "Sammelst du alles ein?"):
            mänx.inventar["Stern des Vorvgir"] += 1
            mänx.inventar["Gold"] += 13568
            mänx.inventar["Eisen"] += 10
            mänx.inventar["Stein"] += 1
        else:
            mint("Dann eben nicht. Tja... ")
            mint("Ich denke du solltest",
                 kursiv("woanders"), "hin...")
        return None


def schimmernde_mauer(mänx: Mänx) -> None:
    malp("Du stößt auf eine seltsam schimmernde Mauer.")
    if ja_nein(mänx, "Versuchst du sie zu durchbrechen?"):
        malp(
            "Als deine Spitzhacke die Mauer trifft, splittert sie mit einem hässlichen Kreischen.")
        mint("Aaaaaaaaaaaaaaahhhhhh!!!")
        malp("Ein gellender Schrei zerreißt die Stille.")
        mint("Wer schreit denn da?!")
        malp("Oh: ", kursiv("du"), "schreist da!")
        malp("Die Schmerzen bringen dich um den Verstand.")
        mint("Du bist tot")
        mint("Oder etwa doch nicht?")
        mänx.inventar["Stein"] += 30
        mänx.inventar["Talisman der Schreie"] += 1
        mänx.inventar["Spitzhacke"] -= 1

    else:
        malp("OK dann eben nicht.")
        mint("Ich denke mal du solltest ",
             kursiv("verschwinden!"), "")
        mänx.inventar["Stein"] += 30


def t1(_mänx: Mänx):
    malp("Du spürst instinktiv, dass das die falsche Entscheidung war.")
    raise Spielende


def t2(mänx: Mänx) -> Fortsetzung:
    malp("Hinter der Tür ist es warm und sonnig.")
    mänx.sleep(1)
    mänx.welt.setze("jtg:t2")
    return jtg.t2


def osten_alt(mänx: Mänx):
    mint("Du läufst weiter bis du eine Karawane siehst. Ein sonnengebräunter Mann läuft zu dir. ")
    mint("Du hast die Wahl, sagt der Mann. Wenn du mich "
         "tötest, gehört die gesamte Karawane dir. Du kannst aber auch mein Leibdiener werden. "
         "Dann bekommst du täglich Essen und dir wird sogar ein kleiner Lohn, 31 Gold pro "
         "Woche, ausgezahlt. Mit 310 Gold kannst du dich dann freikaufen.")
    Entscheidung = minput(mänx, "Wirst du sein Leibdiener oder kämpfst du gegen ihn?"
                          "leibdiener/kampf/flucht.(l/k/f)", ["l", "k", "f"])

    if Entscheidung == "l":
        malp('"Hurra!", der Mann strahlt. Ich hatte noch nie einen Arak als Diener!')
        mänx.sleep(1)
        mint("Nun beginnt dein Leben als Diener")

    elif Entscheidung == "k":
        mint("")

    else:
        assert Entscheidung == "f"
        mint('Du rennst weg,'
             'doch der Karawanenbesitzer holt dich mit einer übermenschlichen Geschwindigkeit wieder ein '
             'und fasst dich am Kragen: '
             '"Schön hier geblieben." '
             'Dann siehst du beinahe in Zeitlupe eine Klinge herannahen.')

        raise Spielende


def monster(mänx: Mänx):
    mint("Du hörst ein Klatschen.")
    mint("Es klingt ein wenig so, wie wenn man einen nassen Frosch an eine nasse Wand wirft.")
    mint("Vorsichtig gehst du weiter.")
    a = random.randint(1, 5)
    if a == 1:
        mint("Bis plötzlich vor dir ein F®X↓ŋ auftaucht. "
             "Diese Wesen sehen eigentlich aus wie Frösche."
             "Also, wenn man mal von der Größe, "
             "der lilanen Färbung sowie der großen, haarigen und heraushängenden Zunge absieht.")

    elif a == 2:
        mint("Und hältst inne als vor dir ein Zombie aus der Dunkelheit torkelt.")

    elif a == 3:
        mint("Und bleibst stehen als vor dir das uralte Skelett eines Minotaurus,"
             "offenbar durch böse Magie wiederbelebt,"
             "aus dem Schatten trat und dabei seine anscheinend noch gut erhaltene Steitaxt schwang.")

    elif a == 4:
        mint("Ohne dir Zeit zum Reagieren zu geben,"
             "schlagen dich einige vermummten Gestalten bewusstlos und stecken dich in einen Sack.")

    elif a == 5:
        mint(
            "Vor dir tritt ein bärtiger, nach Alkohol stinkender Mann aus dem Schatten.")

    else:
        mint("Plötzlich fängst du an gewaltige Kompo-schmerzen zu haben."
             "Aber warte mal! Du ", kursiv("hast"), " ja gar keinen Kompo!"
             "Du bist schließlich ein Me, ein Män, ein Mons..."
             "Naja, irgendetwas in der Art halt."
             "Was ", kursiv("machst"), " du hier eigentlich? Du solltest schleunigst verschwinden!")
        mint("Ein Schrei entringt deiner Kehle und dir wird schwarz vor Augen.")
        mint("Als du wieder aufwachst,"
             "liegst du inmitten einer saftigen Wiese aus leuchtendem blauem Gras.")
        malp("Nein... Anscheinend befindest du dich in einer Höhle.")
        mint("In einer mit leuchtend blauem Gras bewachsenen Höhle.")
        malp("Und noch etwas war seltsam: "
             "Irgendwie fühlst du dich kräftiger, ", kursiv("lebendiger!"), "")
        mint("Unwillkürlich schaust du an dir herunter – Und erstarrst!")
        mint("Keine Haut mehr an deinem Fleisch, "
             "kein Fleisch mehr an deinen Knochen: "
             "Du bist ein Skelett!")
        mänx.rasse = "Skelett"
