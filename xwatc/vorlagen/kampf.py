"""
Kampf-vorlagen
"""
from __future__ import annotations
from typing import Optional as Opt, cast
from xwatc.system import Mänx, mint, Spielende, malp, Fortsetzung, kursiv,\
    malpw
import random
from xwatc.untersystem.verbrechen import Verbrechensart
import time
from xwatc.nsc import NSC


class ausgerüstet:
    """Prüft, ob der Mänx eine Waffe ausgerüstet hat."""

    def __init__(self, *waffe: str, klasse: Opt[str] = None):
        if not (waffe or klasse):
            raise TypeError("Waffe oder Klasse müssen angegeben werden.")
        elif waffe and klasse:
            raise TypeError(
                "Waffe und Klasse können nicht beide gegeben werden.")
        self.waffe = waffe
        self.klasse: str = cast(str, klasse)

    def __call__(self, __, mänx: Mänx) -> bool:
        if self.waffe:
            return any(mänx.hat_item(waffe) for waffe in self.waffe)
        else:
            return bool(mänx.hat_klasse(self.klasse))


def dorfbewohner_kampf(self: NSC, mänx: Mänx) -> Fortsetzung | None:
    # TODO: Dorfbewohner-Kampf Wieder verwenden ?
    from xwatc.lg.norden import gefängnis_von_gäfdah
    self.add_freundlich(-30, -200)
    geschlecht = getattr(self, "geschlecht", False)
    if mänx.hat_klasse("Waffe", "magische Waffe"):
        if ausgerüstet('Dolch')(self, mänx):
            malp("Du streckst den armen Typen mit dem Dolch von hinten nieder.")
            self.tot = True
            malp("Das hat hoffentlich keiner gesehen.")
            if self.ort and random.randint(1, 3) == 1:
                hilfe = None
                # hilfe = self.ort.melde(mänx, Ereignis.MORD, [self])
                if hilfe:
                    malp("Du wurdest bemerkt!")
                    malp("Die anderen Dorfbewohner überwältigen dich.")
                    mänx.add_verbrechen(Verbrechensart.MORD)
                    if random.randint(0, 1):
                        malp(f"{self.name} war im Dorf sehr beliebt.")
                        mint("Die Dorfbewohner bestimmen, dich gleich auf der "
                             "Stelle zu lynchen.")
                        raise Spielende
                    else:
                        malp(f"So beliebt war {self.name} wohl doch nicht.")
                        malp("Du wirst den Wachen ausgeliefert.", warte=True)
                        return gefängnis_von_gäfdah

            malp("Du versteckst schnell die Leiche.")
            self.plündern(mänx)
            return None
        elif self.freundlich > -30:
            if geschlecht:
                malpw("Du stürmst auf den verdutzten Dorfbewohner zu.")
            else:
                malpw("Du stürmst auf die entsetzte Frau zu, die Waffe erhoben.")
            if self.hat_klasse("magische Waffe"):
                malp("Aber", "er" if geschlecht else "sie",
                     "hat eine magische Waffe.")
                malp("Du hast keine Chance.", warte=True)
                raise Spielende
            elif self.hat_klasse("Waffe"):
                malpw("Aber", "er" if geschlecht else "sie", "pariert!")
                malp("Sie ruft um Hilfe, ", end="")
                return _konfrontation(self, mänx)

            else:
                malp("Du bringst", "ihn" if geschlecht else "sie",
                     "in einem Schlag um.")
                # if self.ort and self.ort.melde(mänx, Ereignis.MORD, [self]):
                #     malp("Die Dorfbewohner eilen herbei. Sie sind entsetzt.")
                #     malpw("Du kommst ins Gefängnis.")
                #     mänx.add_verbrechen(Verbrechensart.MORD, versuch=True)
                #     return gefängnis_von_gäfdah
                # else:
                #     malp("Niemand ist mehr da, der die Tat ächten könnte.")
                #     return None
                return None
        else:
            if self.freundlich == -30:
                malp(f"{self.name} war vor dir auf der Hut.")
            else:
                malp(f"{self.name} war dir gegenüber bereits argwöhnisch.")
            if geschlecht:
                if self.hat_klasse("magische Waffe", "Waffe"):
                    malpw(
                        end="Er stellt sich dir entgegen und ruft nach Unterstützung, ")
                    return _konfrontation(self, mänx)
                else:
                    malpw("Er flieht, nach Hilfe schreiend.")
            else:
                malpw("Sie flieht, nach Hilfe schreiend.")
            # Flucht
            ausgang = random.randint(1, 3)
            if ausgang == 1:
                malp(f"{self.name} ist echt schnell auf den Beinen!")
                malpw("Du schaffst es nicht,",
                      "ihn" if geschlecht else "sie", "einzuholen.")
                mänx.add_verbrechen(Verbrechensart.MORD, True)
                return None
            elif ausgang == 2:
                malp(f"Keuchend holst du {self.name} ein.")
                malpw("An einen Kampf ist aber nicht mehr zu denken.")
                mänx.add_verbrechen(Verbrechensart.MORD, True)
                return None
            else:
                malpw(f"Du holst {self.name} ein und bringst",
                      "ihn" if geschlecht else "sie", "um.")
                self.tot = True
                self.plündern(mänx)
                return None

    elif self.hat_klasse("Waffe", "magische Waffe"):
        mint(
            f"Du rennst auf {self.name} zu und schlägst wie wild auf "
            + ("ihn" if geschlecht else "sie") + " ein."
        )
        if self.hat_item("Dolch"):
            if geschlecht:
                mint("Er ist erschrocken, schafft es aber, seinen Dolch "
                     "hervorzuholen und dich zu erstechen.")
            else:
                mint("Aber sie zieht ihren Dolch und sticht dich nieder")
            raise Spielende
        else:
            if geschlecht:
                mint("Aber er wehrt sich tödlich.")
            else:
                mint("Aber sie ist bewaffnet!")
            raise Spielende
    elif random.randint(1, 6) != 1:
        # hilfe = self.ort and self.ort.melde(mänx, Ereignis.KAMPF, [self])
        hilfe = None
        if hilfe:
            malp("Sofort kommen Leute, um dich aufzuhalten.")
            malp("Sie entschließen sich, dich ins Gefängnis zu schmeißen.")
            mänx.add_verbrechen(Verbrechensart.MORD, versuch=True)
            return gefängnis_von_gäfdah
        else:
            malp("Irgendwann ist dein Gegner bewusstlos.")
            self.plündern(mänx)
            if mänx.ja_nein("Schlägst du weiter bis er tot ist oder gehst du weg?"):
                malp("Irgendwann ist der Arme tot. Du bist ein Mörder. "
                     "Kaltblütig hast du dich dafür entschieden einen lebendigen Menschen zu töten."
                     "", kursiv(" zu ermorden. "), "Mörder.")
                self.tot = True
                return None
            else:
                malp("Du gehst weg.")
                return None

    else:
        malp("Diesmal bist du es, der unterliegt.")
        a = random.randint(1, 10)
        if a != 1:
            mint("Als du wieder aufwachst, bist du woanders.")
            mänx.add_verbrechen(Verbrechensart.MORD, versuch=True)
            return gefängnis_von_gäfdah
        else:
            mint("Er hat dich einfach liegen lassen und nicht ausgeliefert.")
            return None


def _konfrontation(self: NSC, mänx: Mänx) -> Opt[Fortsetzung]:
    from xwatc.lg.norden import gefängnis_von_gäfdah
    # hilfe = self.ort and self.ort.melde(mänx, Ereignis.KAMPF, [self])
    hilfe = None
    if hilfe:
        malp("und die kommt.")
        if mänx.hat_item("Schwert"):
            self.tot = True
            malp("Dein Schwert hat Blut geschmeckt.")
            malpw("Du richtest ein furchtbares Massaker an.")
            # TODO: Die Hilfen umbringen
            return None
        else:
            malp("Du bist zahlenmäßig unterlegen und verlierst den "
                 "Kampf.")
            malp(f"{self.name} ist aufgebracht und will dich auf "
                 "der Stelle umbringen.")
            if mänx.welt.is_nacht():
                malpw("Du wirst noch am nächsten Morgen hingerichtet.")
            else:
                malpw("Du wirst noch an diesem Abend")
            raise Spielende
    else:
        malpw("aber sie kommt nicht.")
        malp("Ihr liefert euch einen Kampf auf Leben und Tod,")
        time.sleep(1.1)
        if random.randint(0, 1):
            malp("den du verlierst.")
            raise Spielende
        else:
            malp("aber du gewinnst.")
            self.tot = True
            self.plündern(mänx)
            return None
