from xwatc.dorf import Dorf, NSC, Ort, NSCOptionen, Dorfbewohner, Rückkehr
from xwatc.lg.norden.gefängnis_von_gäfdah import gefängnis_von_gäfdah
from xwatc.system import mint, kursiv, Mänx, ja_nein

class SakcaBrauc(NSC):
    def __init__(self):
        super().__init__("Sakca Brauc", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        print("Als du Anstalten machtest, deine Waffe zu zücken, "
              "schlug Sakca dir mit der Faust ins Gesicht.")
        mint("Als du daraufhin zurücktaumelst, schlägt sie dich bewusstlos.")
        gefängnis_von_gäfdah(mänx)

    def reden(self, mänx: Mänx) -> Rückkehr:
        print('"Was ist?", fragt dich die Wache.')
        opts = [
            ('"Hallo, Wie heißt du?"', 'heißt', 0),
            ('"Du heißt Maria, oder?"', "maria", 1),
            ('"Wie findest du das Wetter heute?"', "wetter", 2),
            ('"Wie geht es dir?"', "geht", 3)
        ]
        opt = mänx.menu(opts, "Was sagst du?")
        if opt == 0:
            print("Ich heiße Sakca")

        elif opt == 1:
            print("Lass mich in Ruhe!")
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
            print('Sie scheint nicht allzu gesprächig zu sein.')
        return Rückkehr.WEITER_REDEN

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und geht ihrer Arbeit nach.")
        super().main(mänx)


class ThomarcAizenfjäld(NSC):

    def __init__(self):
        super().__init__("Thomarc Aizenfjäld", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        print("Als du Anstalten machtest, deine Waffe zu zücken, "
              "schlug die Wache dir mit der flachen Seite ihres Schwertes gegen die Schläfe.")
        gefängnis_von_gäfdah(mänx)
            
    def handeln(self, mänx: Mänx) -> None:
        print("Die Wache will gerade nicht handeln.")

    def reden(self, mänx: Mänx) -> Rückkehr:
        print('"Was ist?", fragt die Wache dich.')
        opts = [
            ('"Hallo, Wer bist du?"', 'bist', 0),
            ('"Wie findest du das Wetter heute?"', "wetter", 1),
            ('"Hey, wie geht es dir?"', "geht", 2)
        ]
        opt = mänx.menu(opts, "Was sagst du?")
        if opt == 0:
            print("Der Wachmann reagiert nicht.")
        elif opt == 1:
            mint('"schön", sagte die Wache mürrisch.')
        elif opt == 2:
            mint('"gut", sagte die Wache.')
            print('Sie scheint nicht allzu gesprächig zu sein.')
        return Rückkehr.VERLASSEN

    def optionen(self, mänx: Mänx) -> NSCOptionen:
        yield from NSC.optionen(self, mänx)
        yield ("handeln", "handeln", self.handeln)

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und geht ernst und dienstbeflissen ihrer Arbeit nach.")
        super().main(mänx)


class OrfGrouundt(NSC):
    def __init__(self):
        super().__init__("Orf Grouundt", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        print("Als du Anstalten machtest, deine Waffe zu zücken, "
              "gibt der Wachmann dir eine so dicke Kopfnuss, dass du "
              "ohnmächtig auf das Pflaster sinkst.")
        gefängnis_von_gäfdah(mänx)


    def reden(self, mänx: Mänx) -> Rückkehr:
        print('"Hallo"')
        opts = [
            ('"Wer bist du?"', 'bist', 0),
            ('"Du bist doch ein Panti, oder?"', "panti", 1),
            ('"Wie findest du das Wetter heute?"', "wetter", 2),
            ('"Wie geht es dir?"', "geht", 3)
        ]
        opt = mänx.menu(opts, "Was sagst du?")
        if opt == 0:
            print('"Hau ab!"')
        elif opt == 1:
            print("", kursiv("NEIN!"), "")
            mint("Wage es ja nicht wieder mich einen Panti zu nennen!!!")
        elif opt == 2:
            mint('"Hau ab", sagte die Wache mürrisch.')
        elif opt == 3:
            mint('"Hau ab!", sagte die Wache.')
            print('Sie scheint nicht allzu gesprächig zu sein.')
        return Rückkehr.WEITER_REDEN

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und plaudert mit Maria Fischfrisch.")
        super().main(mänx)


class MarioWittenpfäld(NSC):
    def __init__(self):
        super().__init__("Mario Wittenpfäld", "Wache")

    def kampf(self, mänx: Mänx) -> None:
        print("Als du Anstalten machtest, deine Waffe zu zücken, "
              "schlug die Wache dir mit der flachen Seite ihres Schwertes gegen die Schläfe.")
        gefängnis_von_gäfdah(mänx)

    def reden(self, mänx: Mänx) -> Rückkehr:
        print('"Was ist?", fragt die Wache dich.')
        opts = [
            ('"Hallo, Wer bist du?"', 'bist', 0),
            ('"Du heißt Tom, oder?"', "tom", 1),
            ('"Wie findest du das Wetter heute?"', "wetter", 2),
            ('"Hey, wie geht es dir?"', "geht", 3)
        ]
        opt = mänx.menu(opts, "Was sagst du?")
        if opt == 0:
            print("Der Wachmann reagiert nicht.")
            if ja_nein(mänx, " Beharrst du auf deine Frage?"):
                mint("Die Wache seufzt. Ich heiße Mario. Mario Wittenpfäld.")
            else:
                mint(self.name, "Du lässt die Wache in Ruhe.")
        elif opt == 1:
            print("", kursiv("nein!"), "     Ich heiße Mario, Mario Wittenpfäld!")
        elif opt == 2:
            mint('"schön", sagte die Wache mürrisch.')
        elif opt == 3:
            mint('"gut", sagte die Wache.')
            print('Sie scheint nicht allzu gesprächig zu sein.')
        return Rückkehr.WEITER_REDEN

    def main(self, mänx: Mänx) -> None:
        print("Die Wache steht herum und geht ernst und dienstbeflissen ihrer Arbeit nach.")
        super().main(mänx)
