from time import sleep
from xwatc.system import Mänx, minput, ja_nein, Spielende, mint, malp, Fortsetzung, _
from xwatc.weg import get_eintritt, Eintritt, Gebiet
from xwatc import weg
from xwatc.nsc import StoryChar, Zeitpunkt, Dialog, NSC, Rückkehr

eingang_osten = Eintritt("lg:westen", "mitte")

@weg.gebiet("lg:westen")
def erzeuge_westen(mänx: Mänx, gb: Gebiet) -> None:
    """Erzeugt das Gebiet Westen."""
    from xwatc.lg import mitte
    huhn_p = gb.neuer_punkt((3, 1), "Huhnort", immer_fragen=True)
    huhn_p.bschr([
        "Mit einer kühlen, entgegenkommenden Meeresbrise wanderst du in Richtung Westen."], "o")
    
    huhn_p.verbinde(gb.ende(eingang_osten, mitte.Eintritt_West), "o")
    huhn_p.add_char(mänx.welt, Huhn)
    gb.neuer_punkt((2,1), "Meereskreuzung").bschr([
        _("Du erreichst das Meer. Sanft schlagen die Wellen an den Strand."),
        _("Da du kein Boot hast, musst du hier wohl abbiegen."),
        _("Ein markanter, großer Findling steht hier am Strand.")
    ], nur="o").add_option("Am Strand spielen", "strand", [
        _("Du spielst mit dem Sand."),
        _("Er eignet sich perfekt für Sandburgen.")
    ]).bschr([
        _("Du siehst einen markanten Findling."),
        _("Vielleicht ist das eine gute Stelle, um in Richtung Inland zu laufen.")
    ], außer="o")
    gb.neuer_punkt((2,0), "Hexenhütte").bschr([
        _("Eine mittelgroße Hütte mit geschlossenen Läden steht am Strand."),
    ]).add_option("Anklopfen", "anklopfen", [
        _("Es scheint niemand zu Hause zu sein.")
    ])
    gb.neuer_punkt((2,2), "Küstenende")

def kampf_huhn(nsc: NSC, mänx: Mänx) -> Rückkehr:
    malp("Du tötest das Huhn und es ist als wäre ein Bann von dir abgefallen. "
         "Plötzlich bist du wieder vergnügt und entspannt.")
    if ja_nein(mänx, "Durchsuchst du das Huhn?"):
        mänx.erhalte("Hühnerfleisch", 5)
        mänx.erhalte("Stein der aussieht wie ein Hühnerei")
        mänx.erhalte("Mugel des Sprechens")
    nsc.tot = True
    return Rückkehr.VERLASSEN

def weiter_huhn(_n: NSC, _mänx: Mänx) -> Rückkehr:
    malp("Du gehst einfach geradeaus. Du bemerkst erst, dass du den Atem angehalten hast, "
             "als du in sicherem Abstand zum Huhn ausatmest.")
    mint()
    malp("Du gehst einfach weiter, aber das Huhn springt dich von hinten an, "
         "bohrt seinen Schnabel in deinen Rücken.")
    mint("Du stirbst.")
    raise Spielende()

def flucht_huhn(nsc: NSC, mänx: Mänx) -> Fortsetzung:
    from xwatc.lg import mitte
    malp("Du entkommst dem Huhn mühelos.")
    malp("Nach einer Weile kommst du wieder dort an wo du losgelaufen bist.")
    mint()
    return mitte.Eintritt_West


Huhn = StoryChar("lg:westen:huhn", ("Huhn", "Huhn"), dialoge=[
    Dialog("k", "Angreifen", kampf_huhn, zeitpunkt=Zeitpunkt.Option),
    Dialog("w", "Weitergehen", weiter_huhn, zeitpunkt=Zeitpunkt.Option),
    Dialog("f", "Fliehen", flucht_huhn, zeitpunkt=Zeitpunkt.Option)
])


def westen(mänx: Mänx) -> Fortsetzung:
    malp("Da begegnete dir eine Henne, die auf einem Stein hockt.")



def reden(mänx: Mänx) -> Fortsetzung:
    malp("Erstaunlicherweise kann das Huhn sprechen.")
    malp('"Hallo", sagt das Huhn. Sie dir mein schönes Eierchen an!')
    malp('Du siehst dir das "Ei" an. Und bemerkst, das es einfach nur ein Stein ist. ')
    mint()
    malp("Was sagst du?")
    malp("1: Ahäm. Das ist kein Ei")
    malp("2: Plopp. Ich bin ein hässliches kleines Fischibischi (Kbörg)")
    malp("3: Tut mir wirklich sehr leid, Monsieur Henne, a"
         "ber das ist lediglich ein hässliches Ei!")
    malp("4:OOOkay! Tschüss")
    malp("5:Bye")
    malp("6:Ja, es ist wirklich sehr schön.")
    malp("7:Reden wir über etwas anderes. Bitte.")
    malp("8:Tut mir wirklich sehr leid, Monsieur Henne, aber das ist lediglich ein "
         "hässlicher Stein")
    malp("9:Tut mir wirklich sehr leid, Madam "
         "Henne, aber das ist lediglich ein "
         "hässliches Ei!")
    malp("10:Tut mir wirklich sehr leid, Madam "
         "Henne, aber das ist lediglich ein"
         "hässlicher Stein!")
    nett = minput(mänx, "Was sagst du? 1/2/3/4/5/6/7/8/9/10",
                  ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])

    if nett == "1":
        malp('Die Henne starrt dich an.'
             '"Wie kannst du es wagen!", kreischt sie.'
             'Für einen Augenblick sieht sie sehr, sehr wütend aus.'
             'Dann verschwindet sie in einer Wolke aus Federn und Staub.')

    if nett == "2":
        malp('"Hä?" Einen Augenblick guckt die Henne dich nur verständnislos an.'
             'Dann sagt sie feierlich: "Du bist würdig."'
             ', und gibt dir eine seltsame Kugel, "das Hühnerei" und etwas Geld.'
             'Danach krähte und gackerte sie noch etwas,'
             'doch du konntest sie nicht mehr verstehen. ')
        mänx.erhalte("Stein der aussieht wie ein Hühnerei")
        mänx.erhalte("Mugel des Sprechens")
        mänx.erhalte("Gold", 50)

    if nett == "3":
        malp(
            "Die Züge der Henne froren ein. Die Henne war die Ausdruckslosigkeit in Pers... Huhn.")
        malp("Das Huhn guckt dich an.")
        sleep(1)
        malp("Das Huhn guckt dir tief in die Augen.")
        sleep(3)
        malp("Das Huhn guckt dir sehr tief in die Augen.")
        sleep(5)
        malp("sehr, sehr tief")
        sleep(6)
        leben = minput(mänx, "Langsam wird dir übel."
                       "Kotzt du einfach hemmungslos oder hältst du es zurück?"
                       "(ko/z)", ["ko", "z"])
        if leben == "ko":
            malp("Du erbrichst dich über dem Huhn, brichst den Bann und fliehst.")
        elif leben == "z":
            malp(
                "Das Huhn dringt durch die Augen in dich ein und ... verändert dort etwas.")
            malp("Plötzlich wird dir klar, dass du ein Wurm bist. ")
            sleep(3)
            malp("Das Huhn pickt")
            sleep(3)
            malp("aua")
            raise Spielende

    if nett == "4":
        malp("Den Blick des Huhns auf dir spürend, machst du dich von dannen.")

    elif nett == "5":
        malp("Du beachtest den verwirrten Blick des Huhns nicht und gehst du davon.")

    elif nett == "6":
        malp(
            '"Ja, findest du nicht auch?" Mit geschwellter Brust watschelt das Huhn davon')

    elif nett == "7":
        malp('Verwirrt betrachtet dich das Huhn noch einmal eingehend.'
             '"Ja, worüber willst du denn reden?", fragt es.')
        malp("1. Wo liegt die nächste menschliche Ansiedlung?")
        malp("2. Wie findest du das Wetter?")
        malp("3. Kannst du mir irgentetwas beibringen? ")
        malp("4. Wie kommt es, dass du sprechen kannst?")
        cmal = minput(mänx, "1/2/3/4", ["1", "2", "3", "4"])
        if cmal == "1":
            malp("Plötzlich wirkt das Huhn sehr verlegen."
                 "Statt dir zu antworten, "
                 "springt es ins Gebüsch und verschwindet.")
        elif cmal == "2":
            malp('"sehr schön, sehr schön...", murmelt die Henne.'
                 'Dann springt sie plötzlich auf und schreit in die Welt hinaus:'
                 '"Bei gutem Wetter sollte man auf Wanderschaft gehen.'
                 'Kreischend packt sie ihr "Ei" und rennt davon."')
        elif cmal == "3":
            malp('"Ja, das kann ich", sprach die Henne.'
                 'Sie wirkte plötzlich sehr ernst und weise.'
                 '"Aber dann musst du mich mit Meisterin Kraagkargk ansprechen.')
            ja = minput(mänx, "Ja Meisterin Kraagkargk/Nein Meis"
                        "terin Kraagkargk/Ja/nein (jm/nm/j/n)",
                        ['jm', 'nm', 'n', 'j'])
            if ja == 'jm':
                mint('"Gut", sagte Meisterin Kraagkargk')
                malp("Du musst jetzt leider eine Minute warten.")
                sleep(60)
                malp("Meisterin Kraagkargk huscht in die Nacht davon "
                     "und du schlägst auf einer Wiese in der Nähe dein Lager auf.")
                sleep(3)
                malp('Info: Du hast hast "verrückter Schrei" gelernt!')
                malp('Jeder der ihn hört, reagiert anders.')
                malp(
                    'Manche weinen, manche lachen, manche wiederum erbrechen sich.–')
                malp(
                    'Auf jeden Fall verschafft es dir einige Minuten der Ablenkung!')
            elif ja == 'nm':
                malp('Meisterin Kraagkargk wurde wütend.'
                     '"So gehe doch", rief sie theatralisch und ging selbst.')
            elif ja == 'n':
                malp("Meisterin Kraagkargk guckt dich kurz an und ging dann.")
            elif ja == 'j':
                malp(
                    'Meisterin Kraagkargk schnaubte und stolzierte beleidigt davon.')

            elif cmal == "4":
                malp('"Das liegt an meinem Mugel des Sprechens", '
                     'sagte die Hühnerdame und lief durch deine "dumme" Frage empört davon.')

        elif nett == "8":
            malp(
                "Die Züge der Henne wurden starr. Die Henne wurde die Ausdruckslosigkeit in Pers.. Huhn.")
            malp("Und sie guckt dich an.")
            sleep(1)
            malp("Guckt dir tief in die Augen.")
            sleep(3)
            malp("tiefer")
            sleep(5)
            malp("noch tiefer")
            sleep(6)
            leben = minput(mänx, "Dir wird übel."
                           "Erbrichst du dich du einfach hemmungslos oder hältst du es zurück?"
                           "(er/z)", ['er', 'z'])
            if leben == "er":
                malp(
                    "Du erbrichst dich über dem Huhn, brichst den Bann und fliehst.")
            elif leben == "z":
                malp(
                    "Das Huhn kriecht durch deine Augen in dich ein und ... verändert dort etwas.")
                malp("Plötzlich wird dir klar, dass du ein Wurm bist. ")
                sleep(3)
                malp("Das Huhn pickt")
                sleep(3)
                malp("aua")
                raise Spielende

    elif nett == "9":
        malp("Die Henne kreischt.")
        malp("lauter als ein Löwe,")
        malp("schriller als ein Adler,")
        mint("todbringender als eine Banshee.")
        raise Spielende

    elif nett == "10":
        malp("Erst blickt dich das Huhn wütend an, dann verschwindet es.")
