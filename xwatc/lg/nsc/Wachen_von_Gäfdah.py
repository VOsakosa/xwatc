from xwatc.dorf import NSC, NSCOptionen, Rückkehr, Malp
from xwatc.lg.norden.gefängnis_von_gäfdah import gefängnis_von_gäfdah
from xwatc.system import mint, kursiv, Mänx, ja_nein, malp
from xwatc.nsc import Person, StoryChar

WACHEN_INVENTAR = {
    "Schild": 1
}


class SakcaBrauc(NSC):
    def __init__(self):
        super().__init__("Sakca Brauc", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        malp("Als du Anstalten machtest, deine Waffe zu zücken, "
             "schlug Sakca dir mit der Faust ins Gesicht.")
        mint("Als du daraufhin zurücktaumelst, schlägt sie dich bewusstlos.")
        gefängnis_von_gäfdah(mänx)

    def reden(self, mänx: Mänx) -> Rückkehr:
        malp('"Was ist?", fragt dich die Wache.')
        opts = [
            ('"Hallo, Wie heißt du?"', 'heißt', 0),
            ('"Du heißt Maria, oder?"', "maria", 1),
            ('"Wie findest du das Wetter heute?"', "wetter", 2),
            ('"Wie geht es dir?"', "geht", 3)
        ]
        opt = mänx.menu(opts, "Was sagst du?")
        if opt == 0:
            malp("Ich heiße Sakca")

        elif opt == 1:
            malp("Lass mich in Ruhe!")
            if ja_nein(mänx, "Lässt du sie in Ruhe?"):
                mint("Du lässt sie in Ruhe.")
            else:
                mint('Weil du sie anscheinend nicht in Ruhe lassen willst, '
                     'schlägt Sakca dir ins Gesicht und du wist bewusstlos.')
                gefängnis_von_gäfdah(mänx)
        elif opt == 2:
            mint('"schön", sagt Sakca.')
        elif opt == 3:
            mint('"gut", sagte die Wache.')
            malp('Sie scheint nicht allzu gesprächig zu sein.')
        return Rückkehr.WEITER_REDEN

    def main(self, mänx: Mänx) -> None:
        malp("Die Wache steht herum und geht ihrer Arbeit nach.")
        super().main(mänx)


class ThomarcAizenfjäld(NSC):

    def __init__(self):
        super().__init__("Thomarc Aizenfjäld", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        malp("Als du Anstalten machtest, deine Waffe zu zücken, "
             "schlug die Wache dir mit der flachen Seite ihres Schwertes gegen die Schläfe.")
        gefängnis_von_gäfdah(mänx)

    def handeln(self, mänx: Mänx) -> None:
        malp("Die Wache will gerade nicht handeln.")

    def reden(self, mänx: Mänx) -> Rückkehr:
        malp('"Was ist?", fragt die Wache dich.')
        opts = [
            ('"Hallo, Wer bist du?"', 'bist', 0),
            ('"Wie findest du das Wetter heute?"', "wetter", 1),
            ('"Hey, wie geht es dir?"', "geht", 2)
        ]
        opt = mänx.menu(opts, "Was sagst du?")
        if opt == 0:
            malp("Der Wachmann reagiert nicht.")
        elif opt == 1:
            mint('"schön", sagte die Wache mürrisch.')
        elif opt == 2:
            mint('"gut", sagte die Wache.')
            malp('Sie scheint nicht allzu gesprächig zu sein.')
        return Rückkehr.VERLASSEN

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        yield from NSC.optionen(self, mänx)
        yield ("handeln", "handeln", self.handeln)

    def main(self, mänx: Mänx) -> None:
        malp("Die Wache steht herum und geht ernst und dienstbeflissen ihrer Arbeit nach.")
        super().main(mänx)


class OrfGrouundt(NSC):
    def __init__(self):
        super().__init__("Orf Grouundt", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        malp("Als du Anstalten machtest, deine Waffe zu zücken, "
             "gibt der Wachmann dir eine so dicke Kopfnuss, dass du "
             "ohnmächtig auf das Pflaster sinkst.")
        gefängnis_von_gäfdah(mänx)

    def reden(self, mänx: Mänx) -> Rückkehr:
        malp('"Hallo"')
        opts = [
            ('"Wer bist du?"', 'bist', 0),
            ('"Du bist doch ein Panti, oder?"', "panti", 1),
            ('"Wie findest du das Wetter heute?"', "wetter", 2),
            ('"Wie geht es dir?"', "geht", 3)
        ]
        opt = mänx.menu(opts, "Was sagst du?")
        if opt == 0:
            malp('"Hau ab!"')
        elif opt == 1:
            malp("", kursiv("NEIN!"), "")
            mint("Wage es ja nicht wieder mich einen Panti zu nennen!!!")
        elif opt == 2:
            mint('"Hau ab", sagte die Wache mürrisch.')
        elif opt == 3:
            mint('"Hau ab!", sagte die Wache.')
            malp('Sie scheint nicht allzu gesprächig zu sein.')
        return Rückkehr.WEITER_REDEN

    def main(self, mänx: Mänx) -> None:
        malp("Die Wache steht herum und plaudert mit Maria Fischfrisch.")
        super().main(mänx)


mario = StoryChar("nsc:Wachen_von_Gäfdah:MarioWittenpfäld", ("Mario", "Wittenpfäld", "Wache"),
                  Person("m"), WACHEN_INVENTAR,
                  vorstellen_fn=("Die Wache steht herum und geht ernst und dienstbeflissen "
                                 "ihrer Arbeit nach."))


def hallo_mario(_nsc, mänx: Mänx):
    malp("Der Wachmann reagiert nicht.")
    if mänx.ja_nein("Beharrst du auf deine Frage?"):
        mint("Die Wache seufzt. Ich heiße Mario. Mario Wittenpfäld.")
    else:
        mint("Du lässt die Wache in Ruhe.")


mario.dialog("bist", '"Hallo, Wer bist du?"', hallo_mario)
mario.dialog("tom", '"Du heißt Tom, oder?"',
             kursiv("nein!") + "     Ich heiße Mario, Mario Wittenpfäld!")
mario.dialog("wetter", '"Wie findest du das Wetter heute?"',
             [Malp('"schön", sagte die Wache mürrisch.')])
mario.dialog("geht", '"Hey, wie geht es dir?"',
             [Malp('"gut", sagte die Wache.'), Malp('Sie scheint nicht allzu gesprächig zu sein.')])

mario_kampf = ("Als du Anstalten machtest, deine Waffe zu zücken, "
               "schlug die Wache dir mit der flachen Seite ihres Schwertes gegen die Schläfe.")
