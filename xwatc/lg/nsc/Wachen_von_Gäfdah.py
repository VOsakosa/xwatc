from xwatc import _
from xwatc.lg.norden.gefängnis_von_gäfdah import gefängnis_von_gäfdah
from xwatc.system import mint, kursiv, Mänx, ja_nein, malp, Fortsetzung
from xwatc.nsc import Person, StoryChar, Sprich, Rückkehr, Malp, NSC, Dialog, Zeitpunkt

WACHEN_INVENTAR = {
    "Schild": 1
}


def sakca_nerven(nsc: NSC, mänx: Mänx) -> Fortsetzung | Rückkehr:
    nsc.sprich(_("Lass mich in Ruhe!"))
    if ja_nein(mänx, "Lässt du sie in Ruhe?"):
        mint("Du lässt sie in Ruhe.")
        return Rückkehr.VERLASSEN
    else:
        mint('Weil du sie anscheinend nicht in Ruhe lassen willst, '
             'schlägt Sakca dir ins Gesicht und du wist bewusstlos.')
        return gefängnis_von_gäfdah


SakcaBrauc = StoryChar(
    "nsc:Wachen_von_Gäfdah:SakcaBrauc",
    ("Sakca", "Brauc", _("Wache")),
    vorstellen_fn=_("Die Wache steht herum und geht ihrer Arbeit nach."),
    dialoge=[
        Dialog.ansprechen_neu('"Was ist?", fragt dich die Wache.'),
        Dialog("heißt", _("Hallo, wie heißt du?"), _("Ich heiße Sakca")),
        Dialog("maria", _('"Du heißt Maria, oder?"'), _("Lass mich in Ruhe")),
        Dialog("geht", _('"Wie geht es dir?"'), [_("Gut"),
               Malp(_("Sie scheint nicht allzu gesprächig zu sein."))])
    ]
)


@SakcaBrauc.kampf
def kampf(_nsc: NSC, mänx: Mänx) -> Fortsetzung:
    malp("Als du Anstalten machtest, deine Waffe zu zücken, "
         "schlug Sakca dir mit der Faust ins Gesicht.")
    mint("Als du daraufhin zurücktaumelst, schlägt sie dich bewusstlos.")
    return gefängnis_von_gäfdah


ThomarcAizenfjäld = StoryChar(
    "nsc:Wachen_von_Gäfdah:ThomarcAizenfjäld",
    ("Thomarc", "Aizenfjäld", "Wache"), dialoge=[
        Dialog("handeln", _("Handeln"), [
            Malp(_("Die Wache will gerade nicht handeln."))], zeitpunkt=Zeitpunkt.Option),
        Dialog('bist', '"Hallo, Wer bist du?"', [
               Malp("Der Wachmann reagiert nicht.")]),
        Dialog("wetter", '"Wie findest du das Wetter heute?"', [
            Malp('"schön", sagte die Wache mürrisch.')]),
        Dialog("geht", '"Hey, wie geht es dir?"', [
            Malp('"gut", sagte die Wache.'), Malp('Sie scheint nicht allzu gesprächig zu sein.')])
    ],
    vorstellen_fn="Die Wache steht herum und geht ernst und dienstbeflissen ihrer Arbeit nach.")


@ThomarcAizenfjäld.kampf
def ThomarcAizenfjäld_kampf(__: NSC, _m: Mänx) -> Fortsetzung:
    malp("Als du Anstalten machtest, deine Waffe zu zücken, "
         "schlug die Wache dir mit der flachen Seite ihres Schwertes gegen die Schläfe.")
    return gefängnis_von_gäfdah


OrfGrouundt = StoryChar(
    "nsc:Wachen_von_Gäfdah:OrfGrouundt",
    ("Orf", "Grouundt", "Wache"), dialoge=[
        Dialog.ansprechen_neu([Sprich("Hallo")]),
        Dialog('bist', '"Wer bist du?"', "Hau ab!"),
        Dialog("panti", '"Du bist doch ein Panti, oder?"', [
            kursiv("NEIN!"), "Wage es ja nicht wieder mich einen Panti zu nennen!!!"]),
        Dialog("wetter", '"Wie findest du das Wetter heute?"',
               Malp('"Hau ab", sagte die Wache mürrisch.')),
        Dialog("geht", '"Wie geht es dir?"', [
            Malp('"gut", sagte die Wache.'), Malp('Sie scheint nicht allzu gesprächig zu sein.')])
    ],
    vorstellen_fn=_("Die Wache steht herum und plaudert mit Maria Fischfrisch."))


@OrfGrouundt.kampf
def OrfGrouundt_kampf(_nsc, _mänx) -> Fortsetzung:
    malp("Als du Anstalten machtest, deine Waffe zu zücken, "
         "gibt der Wachmann dir eine so dicke Kopfnuss, dass du "
         "ohnmächtig auf das Pflaster sinkst.")
    return gefängnis_von_gäfdah


mario = StoryChar("nsc:Wachen_von_Gäfdah:MarioWittenpfäld", ("Mario", "Wittenpfäld", "Wache"),
                  Person("m"), WACHEN_INVENTAR,
                  vorstellen_fn=_("Die Wache steht herum und geht ernst und dienstbeflissen "
                                  "ihrer Arbeit nach."))


def hallo_mario(_nsc, mänx: Mänx):
    malp("Der Wachmann reagiert nicht.")
    if mänx.ja_nein("Beharrst du auf deine Frage?"):
        mint("Die Wache seufzt. Ich heiße Mario. Mario Wittenpfäld.")
    else:
        mint("Du lässt die Wache in Ruhe.")


mario.dialog("bist", 'Hallo, wer bist du?', hallo_mario)
mario.dialog("tom", 'Du heißt Tom, oder?',
             (kursiv("Nein!"), "Ich heiße Mario, Mario Wittenpfäld!"))
mario.dialog("wetter", 'Wie findest du das Wetter heute?',
             [Malp('"schön", sagte die Wache mürrisch.')])
mario.dialog("geht", "Hey, wie geht es dir?",
             [Malp('"gut", sagte die Wache.'), Malp('Sie scheint nicht allzu gesprächig zu sein.')])
mario.dialog("mürrisch", "Warum bist du so mürrisch?", [
    "Ich habe gerade keine Lust auf die Arbeit"
], "geht", wiederhole=1)
mario.dialog("machen", "Was würdest du denn lieber machen?", [
    "Ich würde jetzt liebend gerne fischen gehen.",
    "Die Ruhe und die Wellen genießen."
], "mürrisch", wiederhole=1)
mario.dialog("ruhe", "Dann gebe ich dir besser Ruhe.", ["Ja, mach das."], "machen")
mario.dialog("angeln", "Ich will auch mal angeln", [
    _("Ach ja."),
    _("Angeln ist wirklich sehr schön. Ich freue mich für jeden, der meine Leidenschaft teilt."),
    _("Du hast noch keine Angelrute? Ich gebe dir eine alte."),
    _("Über schon einmal für mich."),
], "machen", effekt=lambda n, m: m.erhalte("Angel"), wiederhole=1)

mario_kampf = ("Als du Anstalten machtest, deine Waffe zu zücken, "
               "schlug die Wache dir mit der flachen Seite ihres Schwertes gegen die Schläfe.")
