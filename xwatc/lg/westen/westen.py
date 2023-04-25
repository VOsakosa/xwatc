from time import sleep
from xwatc import weg
from xwatc.effect import NurWenn, in_folge
from xwatc.nsc import StoryChar, Zeitpunkt, Dialog, NSC, Rückkehr, Malp, DialogFn, Kennt, AmLeben,\
    Bewege, Sprich
from xwatc.system import Mänx, minput, ja_nein, Spielende, mint, malp, Fortsetzung, _
from xwatc.untersystem.menus import Option
from xwatc.untersystem.person import Person
from xwatc.weg import Eintritt, Gebiet


eingang_osten = Eintritt("lg:westen", "mitte")


@weg.gebiet("lg:westen")
def erzeuge_westen(mänx: Mänx, gb: Gebiet) -> None:
    """Erzeugt das Gebiet Westen."""
    from xwatc.lg import mitte
    huhn_p = gb.neuer_punkt((3, 1), "Huhnort", immer_fragen=False)
    huhn_p.bschr([
        "Mit einer kühlen, entgegenkommenden Meeresbrise wanderst du in Richtung Westen."], "o")
    huhn_p.add_sofort_reden(Huhn)
    huhn_p.verbinde(gb.ende(eingang_osten, mitte.Eintritt_West), "o")
    huhn_p.add_char(mänx.welt, Huhn)
    gb.neuer_punkt((2, 1), "Meereskreuzung").bschr([
        _("Du erreichst das Meer. Sanft schlagen die Wellen an den Strand."),
        _("Da du kein Boot hast, musst du hier wohl abbiegen."),
        _("Ein markanter, großer Findling steht hier am Strand.")
    ], nur="o").add_option("Am Strand spielen[strand]", "strand", [
        _("Du spielst mit dem Sand."),
        _("Er eignet sich perfekt für Sandburgen.")
    ]).bschr([
        _("Du siehst einen markanten Findling."),
        _("Vielleicht ist das eine gute Stelle, um in Richtung Inland zu laufen.")
    ], außer="o")
    gb.neuer_punkt((2, 0), "Hexenhütte").bschr([
        _("Eine mittelgroße Hütte mit geschlossenen Läden steht am Strand."),
    ]).add_option("Anklopfen", "anklopfen", NurWenn(
        AmLeben(Butler),
        in_folge([  # type: ignore
            _("Ein schlecht gelaunter Hausdiener öffnet dir die Tür.")
        ], Bewege(Butler, (gb.name, "Hexenhütte"))),
        [
            _("Es scheint niemand zu Hause zu sein.")
        ])
    ).add_option("Steine werfen", "steine", steine_werfen).wenn(
        "steine", Kennt(Butler)
    )
    mänx.welt.obj(Butler)
    gb.neuer_punkt((2, 2), "Küstenende").bschr([
        _("Hier gibt es nichts zu sehen, und du bist diese Küste müde."),
        _("Du solltest umkehren.")
    ])


def kampf_huhn(nsc: NSC, mänx: Mänx) -> Rückkehr:
    malp("Du tötest das Huhn und es ist als wäre ein Bann von dir abgefallen. "
         "Plötzlich bist du wieder vergnügt und entspannt.")
    if ja_nein(mänx, "Durchsuchst du das Huhn?"):
        mänx.erhalte("Hühnerfleisch", 5)
        mänx.erhalte("Stein der aussieht wie ein Hühnerei")
        mänx.erhalte("Mugel des Sprechens")
    nsc.tot = True
    nsc.ort = None
    return Rückkehr.VERLASSEN


def weiter_huhn(_n: NSC, _mänx: Mänx) -> Rückkehr:
    malp("Du gehst einfach geradeaus. Du bemerkst erst, dass du den Atem angehalten hast, "
         "als du in sicherem Abstand zum Huhn ausatmest.")
    mint()
    malp("Du gehst einfach weiter, aber das Huhn springt dich von hinten an, "
         "bohrt seinen Schnabel in deinen Rücken.")
    mint("Du stirbst.")
    raise Spielende()


def flucht_huhn(_nsc: NSC, _mänx: Mänx) -> Fortsetzung:
    from xwatc.lg import mitte
    malp("Du entkommst dem Huhn mühelos.")
    malp("Nach einer Weile kommst du wieder dort an wo du losgelaufen bist.")
    mint()
    return mitte.Eintritt_West


def vergraulen(text: list[str]) -> DialogFn:
    def reden(nsc: NSC, _m: Mänx) -> Rückkehr:
        malp(*text, sep="\n")
        mint()
        nsc.ort = None
        return Rückkehr.VERLASSEN
    return reden


def reden_monsieur(nsc: NSC, mänx: Mänx) -> Rückkehr:
    malp("Die Züge der Henne froren ein. Die Henne war die Ausdruckslosigkeit in Pers... Huhn.")
    malp("Das Huhn guckt dich an.")
    mänx.sleep(1)
    malp("Das Huhn guckt dir tief in die Augen.")
    mänx.sleep(3)
    malp("Das Huhn guckt dir sehr tief in die Augen.")
    mänx.sleep(5)
    malp("sehr, sehr tief")
    mänx.sleep(6)
    malp("Langsam wird dir übel. Kotzt du einfach hemmungslos oder hältst du es zurück?")
    leben = mänx.menu([Option("Kotzen", "k"), Option("fliehen", "z")])
    if leben == "ko":
        malp("Du erbrichst dich über dem Huhn, brichst den Bann und fliehst.")
        return Rückkehr.VERLASSEN
    else:
        assert leben == "z"
        malp(
            "Das Huhn dringt durch die Augen in dich ein und ... verändert dort etwas.")
        malp("Plötzlich wird dir klar, dass du ein Wurm bist. ")
        sleep(3)
        malp("Das Huhn pickt")
        sleep(3)
        malp("aua")
        raise Spielende


Huhn = StoryChar("lg:westen:huhn", ("Huhn", "Huhn"), direkt_reden=False, dialoge=[
    Dialog("k", "Angreifen", kampf_huhn, zeitpunkt=Zeitpunkt.Option),
    Dialog("w", "Weitergehen", weiter_huhn, zeitpunkt=Zeitpunkt.Option),
    Dialog("f", "Fliehen", flucht_huhn, zeitpunkt=Zeitpunkt.Option),
    Dialog("aufstein", "Vorstellen", [
        Malp("Da begegnete dir eine Henne, die auf einem Stein hockt.")
    ], zeitpunkt=Zeitpunkt.Vorstellen),
    Dialog.ansprechen_neu([
        Malp("Erstaunlicherweise kann das Huhn sprechen."),
        Malp('"Hallo", sagt das Huhn. Sie dir mein schönes Eierchen an!'),
        Malp('Du siehst dir das "Ei" an. Und bemerkst, das es einfach nur ein Stein ist.'),
        Malp("Du spürst das Verlangen, das Huhn darauf hinzuweisen.")
    ]),
    Dialog("ei", "Ahäm. Das ist kein Ei", vergraulen([
        'Die Henne starrt dich an.',
        '"Wie kannst du es wagen!", kreischt sie.',
        'Für einen Augenblick sieht sie sehr, sehr wütend aus.',
        'Dann verschwindet sie in einer Wolke aus Federn und Staub.'
    ])),
    Dialog("schön", "Ja, es ist wirklich sehr schön.", vergraulen([
        '"Ja, findest du nicht auch?" Mit geschwellter Brust watschelt das Huhn davon',
    ])),
    Dialog("mad_stein", "Tut mir wirklich sehr leid, Madam "
           "Henne, aber das ist lediglich ein hässlicher Stein!", vergraulen([
               "Erst blickt dich das Huhn wütend an, dann verschwindet es.",
           ])),
    Dialog("mon_ei", _("Tut mir wirklich sehr leid, Monsieur Henne, aber das ist "
                       "lediglich ein hässliches Ei!"), reden_monsieur),
    Dialog("mon_stein", _("Tut mir wirklich sehr leid, Monsieur Henne, aber das ist "
                          "lediglich ein hässlicher Stein!"), reden_monsieur),


])


@Huhn.dialog_deco("fischibischi", "Plopp. Ich bin ein hässliches kleines Fischibischi (Kbörg)")
def reden_fischibischi(nsc: NSC, mänx: Mänx) -> Rückkehr:
    malp('"Hä?" Einen Augenblick guckt die Henne dich nur verständnislos an.'
         'Dann sagt sie feierlich: "Du bist würdig."'
         ', und gibt dir eine seltsame Kugel, "das Hühnerei" und etwas Geld.'
         'Danach krähte und gackerte sie noch etwas,'
         'doch du konntest sie nicht mehr verstehen. ')
    mänx.erhalte("Stein der aussieht wie ein Hühnerei")
    mänx.erhalte("Mugel des Sprechens")
    mänx.erhalte("Gold", 50)
    nsc.tot = True
    nsc.ort = None
    mint()
    return Rückkehr.VERLASSEN


@Huhn.dialog_deco("anderes", "Reden wir über etwas anderes. Bitte.")
def wirklich_reden(nsc: NSC, mänx: Mänx) -> Rückkehr | Fortsetzung:
    malp('Verwirrt betrachtet dich das Huhn noch einmal eingehend.'
         '"Ja, worüber willst du denn reden?", fragt es.')
    cmal = mänx.menu([
        Option("Wo liegt die nächste menschliche Ansiedlung?[wo]", 1),
        Option("Wie findest du das Wetter?[wetter]", 2),
        Option("Kannst du mir irgentetwas beibringen?[beibringen]", 3),
        Option("Wie kommt es, dass du sprechen kannst?[sprechen]", 4),
    ], save=nsc)
    if cmal == 1:
        malp("Plötzlich wirkt das Huhn sehr verlegen."
             "Statt dir zu antworten, "
             "springt es ins Gebüsch und verschwindet.")
        nsc.ort = None
        return Rückkehr.VERLASSEN
    elif cmal == 2:
        malp('"sehr schön, sehr schön...", murmelt die Henne.'
             'Dann springt sie plötzlich auf und schreit in die Welt hinaus:'
             '"Bei gutem Wetter sollte man auf Wanderschaft gehen.'
             'Kreischend packt sie ihr "Ei" und rennt davon."')
        return Rückkehr.VERLASSEN
    elif cmal == 3:
        malp('"Ja, das kann ich", sprach die Henne.'
             'Sie wirkte plötzlich sehr ernst und weise.'
             '"Aber dann musst du mich mit Meisterin Kraagkargk ansprechen.')
        ja = minput(mänx, "Ja Meisterin Kraagkargk/Nein Meis"
                    "terin Kraagkargk/Ja/nein (jm/nm/j/n)",
                    ['jm', 'nm', 'n', 'j'], save=nsc)
        if ja == 'jm':
            mint('"Gut", sagte Meisterin Kraagkargk')
            malp("Du musst jetzt leider eine Minute warten.")
            mänx.sleep(60)
            malp("Meisterin Kraagkargk huscht in die Nacht davon "
                 "und du schlägst auf einer Wiese in der Nähe dein Lager auf.")
            sleep(3)
            mint()
            malp('Info: Du hast hast "verrückter Schrei" gelernt!')
            malp('Jeder der ihn hört, reagiert anders.')
            malp(
                'Manche weinen, manche lachen, manche wiederum erbrechen sich.–')
            malp(
                'Auf jeden Fall verschafft es dir einige Minuten der Ablenkung!')
            return Rückkehr.VERLASSEN

        elif ja == 'nm':
            malp('Meisterin Kraagkargk wurde wütend.'
                 '"So gehe doch", rief sie theatralisch und ging selbst.')
            nsc.ort = None
            return Rückkehr.VERLASSEN
        elif ja == 'n':
            malp("Meisterin Kraagkargk guckt dich kurz an und ging dann.")
            nsc.ort = None
            return Rückkehr.VERLASSEN
        elif ja == 'j':
            malp(
                'Meisterin Kraagkargk schnaubte und stolzierte beleidigt davon.')
            nsc.ort = None
            return Rückkehr.VERLASSEN
        else:
            assert False

    elif cmal == 4:
        malp('"Das liegt an meinem Mugel des Sprechens", '
             'sagte die Hühnerdame und lief durch deine "dumme" Frage empört davon.')
        nsc.ort = None
        return Rückkehr.VERLASSEN
    else:
        assert False


@Huhn.dialog_deco("tschüss", "OOOkay! Tschüss")
def reden_tschüss(_nsc, _mänx) -> Rückkehr:
    malp("Den Blick des Huhns auf dir spürend, machst du dich von dannen.")
    return Rückkehr.VERLASSEN


@Huhn.dialog_deco("bye", "Bye")
def reden_bye(_nsc, _mänx) -> Rückkehr:
    malp("Du beachtest den verwirrten Blick des Huhns nicht und gehst du davon.")
    return Rückkehr.VERLASSEN


@Huhn.dialog_deco("mad_ei", "Tut mir wirklich sehr leid, Madam "
                  "Henne, aber das ist lediglich ein hässliches Ei!")
def reden_mad_ei(_nsc, _mänx) -> Rückkehr:
    malp("Die Henne kreischt.")
    malp("lauter als ein Löwe,")
    malp("schriller als ein Adler,")
    mint("todbringender als eine Banshee.")
    raise Spielende


def steine_werfen(mänx: Mänx) -> None:
    malp("Du nimmst dir einen großen Stein und wirfst ihn gegen eine der Fensterläden.")
    malp("Es macht einen Riesenlärm.")
    mänx.welt.obj(Butler).sprich("Lassen Sie das!", wie="wütend")
    mänx.welt.obj(Butler).sprich(
        "Sie können nicht einfach Steine gegen das Haus werfen!", wie="wütend")


def tür_zu(nsc: NSC, mänx: Mänx) -> Rückkehr:
    nsc.ort = None
    return Rückkehr.VERLASSEN


Butler = StoryChar("lg:westen:butler", ("Weɐnɐ", "Fri:drɪɕ", "Hausdiener"), Person("m"), dialoge=[
    Dialog("herrin", "Ist die Herrin da?", [
        Sprich("Nein."),
        Malp("Der Hausdiener schließt die Tür."),
    ], effekt=tür_zu),
    Dialog("termin", "Ich habe einen Termin", _(
           "Nee-nee-nee.\n"
           "Das kann nicht sein.\n"
           "Ich verwalte alle Termine meiner Herrin und für Sie habe ich keinen eingetragen."),
           "herrin", effekt=tür_zu),
    Dialog("wiener", "Sie Wiener Würstchen!", [
           _("Weɐnɐ, ich heiße Weɐnɐ! Nicht Wiener!")], "termin"),
    Dialog("sohn", "Sie Sohn einer Mutter!", [_("Wage es ja nicht, meine Mutter zu beleidigen!")],
           "termin"),
])
