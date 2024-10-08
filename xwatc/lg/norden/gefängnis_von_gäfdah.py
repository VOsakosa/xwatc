import random
from collections import Counter
from attrs import define
from xwatc.system import (_, mint, register, Mänx, malp, Fortsetzung,
                          sprich, StoryObject, MethodSave)

from xwatc.untersystem.verbrechen import Verbrechensart
from xwatc.weg import Eintritt

# TODO Gefängnis
# - Der korrekte Ausgang
# - Mint mit Speichern


@register("lg:gefängnis_von_gäfdah")
@define
class GefängnisGäfdah(StoryObject):
    war_drinnen: bool = False
    war_sauber: bool = False
    sauber: bool = False
    absitzen_dauer: int = 0
    ausgang: Eintritt | None = None

    def main(self, _mänx: Mänx) -> Fortsetzung:
        self.sauber = random.randint(1, 10) <= 6
        self.beschreibung()
        if not self.war_drinnen and random.randint(0, 1):
            ans = self.morgen
        else:
            malp("Du wartest in der Zelle, doch zunächst passiert nichts.")
            ans = self.vor_strafe

        self.war_sauber = self.sauber
        self.war_drinnen = True
        return ans

    def morgen(self, mänx: Mänx) -> Fortsetzung:
        mint("Ein Zettel verkündet: Gefichtsverfahren, mogen.")
        malp('Seltsamerweise fehlte das r, '
             'vom "Gefichtsverfahren" ganz zu schweigen. ')
        mänx.sleep(20, 'o')
        mint()
        malp("Irgendwann öffnen sich deine Zellentüren und eine Wache tritt ein.")
        if mänx.ja_nein("Versuchst du zu fliehen", save=MethodSave(self.morgen)):
            malp("Du versuchst die Wache anzugreifen, "
                 "stolperst jedoch über deine Fesseln und stürzt.", warte=True)
            mänx.add_verbrechen(Verbrechensart.AUSBRUCH, True)
            mint("Die Wache ignoriert deinen Fluchtversuch und zerrt "
                 "dich aus der Zelle.")
            return self.gerichtsverfahren
        elif random.randint(1, 30) == 1:
            mint("Die Wache bedeutet dir, ihr zu folgen.")
            return self.gerichtsverfahren
        else:
            return self.vor_strafe

    def beschreibung(self) -> None:
        if self.war_drinnen:
            malp("Du bist nun ein weiteres Mal im Gefängnis.")
            mint("Es ist noch genauso, wie du es in Erinnerung hast.")
            if self.sauber:
                if self.war_sauber:
                    malp("Die selben sterilen Zellen, wie letztes Mal.")
                else:
                    malp("Aber seltsam, die Zelle, in der du dieses Mal bist, "
                         "ist sauber, ganz anders als die vom letzten Mal.")
            else:
                if self.war_sauber:
                    malp("Diese Zelle ist aber ekelhaft dreckig. "
                         "Der Boden unter deinen Füßen fühlt sich rau an.")
                    malp("Wasser tropft von der Decke und "
                         "die Luft riecht so abgestanden, dass dir deine "
                         "letzte Mahlzeit hochkommmt.", warte=True)
                    malp("Nun ist die Zelle noch dreckiger als zuvor.")
                else:
                    malp("An diesem ekelhaften Gestank kann man sich einfach "
                         "nicht gewöhnen.")
        else:

            if self.sauber:
                malp("Du bist in einer sauberen, ja gar sterilen Kammer eingesperrt.")
            else:
                malp("Du bist in einer dunklen und feuchten Zelle eingesperrt.")
                malp("Der Boden unter dir besteht aus unbearbeitetem Stein "
                     "und Essensreste liegen in der Ecke herum.")
                malp("Ein Brechreiz überkommt dich angesichts der stinkenden "
                     "Luft.")

    def vor_strafe(self, mänx: Mänx) -> Fortsetzung:
        while True:
            if random.randint(1, 5) == 1:
                # Gerichtsverfahren
                return self.gerichtsverfahren
            else:
                if ans := self.wache_kommt(mänx):
                    return ans

    def wache_kommt(self, mänx: Mänx) -> Fortsetzung | None:
        """Du kannst mit der Wache reden oder kämpfen oder sie ignorieren."""
        malp("Du wartest auf die Wache.")
        mänx.sleep(20, ">")
        malp("Die Wache kommt nach dir schauen.")
        mänx.menu([(_("nichts tun"), _("nichts tun"), "n")], save=MethodSave(
            self.vor_strafe if self.absitzen_dauer == 0 else self.absitzen))
        return None

    def gerichtsverfahren(self, mänx: Mänx) -> Fortsetzung:
        """Dein Strafmaß (*dauer*) wird festgelegt"""
        malp("Du wirst in einen großen Gerichtssaal geführt.")
        malp("Die Wände werden von Ritterstatuen geziert.")
        if "Respektloser" in mänx.titel:
            malp("Der Richter glubscht dich erstmal lange an.", warte=True)
        else:
            malp("Der Richter blickt dich lange an.")
            malp("Seine Miene strotzt nur so vor Weisheit und Edelmut.", warte=True)
        malp("Der Richter blickt auf ein Stück Papier und liest laut deine "
             "Verbrechen auf:")
        dauer = 0
        for verbrechen, anzahl in Counter(mänx.verbrechen).items():
            zeile = verbrechen.art.name.capitalize()
            if verbrechen.versuch:
                zeile += " (versucht)"
            if anzahl > 1:
                zeile += f" ({anzahl}x)"
            malp(zeile)
            dauer += anzahl
        mint()
        sprich("Richter", f"Deine Haftstrafe liegt bei -kzzt-")
        malp("Plötzlich nimmst die Welt nur noch gedämpft war.")
        malp("Da dröhnt in deinem Kopf eine Stimme:")
        sprich("Unbekannte Stimme",
               "Deine Haftstrafe liegt bei {:g} RL-Minuten.".format(dauer / 2), warte=True)
        self.absitzen_dauer = dauer
        return self.absitzen

    def absitzen(self, mänx: Mänx) -> Fortsetzung:
        if self.absitzen_dauer:
            if ans := self.wache_kommt(mänx):
                return ans
            self.absitzen_dauer -= 1
        return self.fertig_abgesessen

    def fertig_abgesessen(self, mänx: Mänx) -> Fortsetzung:
        malp("Du hast deine Strafe abgesessen.")
        if self.sauber:
            malp("Ein Wächter holt dich aus deiner Zelle und führt dich einen "
                 "langen, weißen Korridor entlang, bis du schließlich zu einem kleinen Raum mit "
                 "mehreren Knöpfen an der Wand kommst.", warte=True)
        else:
            malp("Ein Wächter holt dich aus deiner Zelle und führt dich einen "
                 "langen, dunklen Korridor entlang, bis du schließlich zu einem kleinen Raum mit "
                 "mehreren Knöpfen an der Wand kommst.", warte=True)
        malp("Der Wächter drückt einen der Knöpfe und eine Sekunde lang hast "
             "du das "
             "Gefühl, als wärst du unendlich schwer.")
        malp("Dann öffnet der Wächter eine Tür ins Freie.", warte=True)
        mänx.verbrechen.clear()
        ausgang = self.ausgang
        if not ausgang:
            from xwatc.lg.norden.norden import gäfdah
            ausgang = gäfdah
        return ausgang


def gefängnis_von_gäfdah(mänx: Mänx, ausgang: Eintritt | None = None) -> Fortsetzung:
    """Führe das Gefängnis aus. Der Parameter ausgang gibt an, wohin der Mensch zurückkommt."""
    gf = mänx.welt.obj(GefängnisGäfdah)
    gf.ausgang = ausgang
    return gf


if __name__ == '__main__':
    from xwatc.anzeige import main
    from unittest.mock import patch

    class NonSlotsMänx(Mänx):
        pass
    with patch("xwatc.system.Mänx", NonSlotsMänx):

        def ständig_gäfdah(mänx):
            mänx.sleep = lambda zeit, zeichen=None: malp(f"Schlafe({zeit}, {zeichen})")
            mänx.add_verbrechen(Verbrechensart.DIEBSTAHL)
            return gefängnis_von_gäfdah
        main(ständig_gäfdah)
