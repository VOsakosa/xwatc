"""
Beim Kampfsystem schlagen zwei Leute aufeinander ein.
"""
import enum
import random
from typing import Self, Sequence, TypeAlias

from attrs import define

from xwatc import _
from xwatc.nsc import NSC
from xwatc.system import Mänx, get_classes, malp
from xwatc.untersystem.attacken import Fertigkeit, Schadenstyp
from xwatc.untersystem.attacken import Zieltyp

__author__ = "jasper"


@define(frozen=True)
class MänxController:
    """Stellt eine Kontroller durch den Spieler dar."""

    def wähle_attacke(self, kampf: 'Kampf', idx: int) -> tuple['Fertigkeit', Sequence['Kämpfer']]:
        kämpfer = kampf.kämpfer[idx]
        att = kampf._mänx.menu([(a.name, a.name_kurz, a) for a in kämpfer.get_attacken()],
                               frage=_("kampf>"))
        gegner = [a for a in kampf.kämpfer if a.seite != kämpfer.seite]
        if att.zieltyp == Zieltyp.Einzel and len(gegner) != 1:
            gegner = [kampf._mänx.menu([(a.name, a.name.lower(), a) for a in gegner],
                                       frage=_("Wen?"))]
        return att, gegner


@define
class AIController:
    """Stellt eine Kontrolle durch den Computer dar."""

    def wähle_attacke(self, kampf: 'Kampf', idx: int) -> tuple['Fertigkeit', Sequence['Kämpfer']]:
        """Wählt die Attacke, die die AI durchführt."""
        # Stand jetzt rein zufällig.
        kämpfer = kampf.kämpfer[idx]
        att = random.choice(kämpfer.get_attacken())
        gegner = [a for a in kampf.kämpfer if a.seite != kämpfer.seite]
        if att.zieltyp == Zieltyp.Einzel and len(gegner) != 1:
            gegner = [random.choice(gegner)]
        return att, gegner


Controller: TypeAlias = MänxController | AIController


@define
class KämpferAnzeige:
    """Die Anzeigedaten eines Kämpfers, sein Bild etc."""
    name: str


@define
class Kämpfer:
    """Ein Teilnehmer des Kampfes, mit LP."""
    lp: int
    max_lp: int
    seite: int
    controller: Controller
    anzeige: KämpferAnzeige
    _nsc: NSC | Mänx

    @classmethod
    def aus_mänx(cls, mänx: Mänx) -> Self:
        """Erzeugt einen Kämpfer auf Basis des Spielers."""
        lp = mänx.kampfwerte.max_lp
        return cls(lp=lp, max_lp=lp, seite=1, controller=MänxController(),
                   anzeige=KämpferAnzeige(_("Du")), nsc=mänx)

    @classmethod
    def aus_nsc(cls, nsc: NSC) -> Self:
        """Erzeugt einen Kämpfer auf Basis eines NSCs, als Feind."""
        lp = nsc.kampfwerte.max_lp
        return cls(lp=lp, max_lp=lp, seite=2, controller=AIController(),
                   anzeige=KämpferAnzeige(nsc.name), nsc=nsc)

    @classmethod
    def aus_gefährte(cls, nsc: NSC) -> Self:
        """Erzeugt einen Kämpfer auf Basis eines NSCs, als Gefährte."""
        lp = nsc.kampfwerte.max_lp
        return cls(lp=lp, max_lp=lp, seite=1, controller=MänxController(),
                   anzeige=KämpferAnzeige(nsc.name), nsc=nsc)

    @property
    def name(self) -> str:
        return self.anzeige.name

    @property
    def tot(self) -> bool:
        return not self.lp

    def schade(self, schaden: float) -> None:
        """Füge dem Kämpfer `schaden` an Schaden zu."""
        self.lp -= round(schaden)
        if self.lp < 0:
            self.lp = 0
        if self.lp > self.max_lp:
            self.lp = self.max_lp
        # TODO Notification event!

    def get_attacken(self) -> Sequence['Fertigkeit']:
        """Gebe die Liste von Attacken aus, die der Kämpfer gerade zur Verfügung hat."""
        fertigkeiten = [
            f for f in self.nsc.kampfwerte.fertigkeiten if self.kann_attacke(f)
        ]
        if not any(self._nsc.get_waffen()) and self._nsc.kampfwerte.nutze_std_fertigkeiten:
            fertigkeiten.append(Fertigkeit("Faustschlag", "faust", 6, [Schadenstyp.Wucht]))
        return fertigkeiten

    def kann_attacke(self, attacke: Fertigkeit) -> bool:
        """Prüfe, ob die Fertigkeit für einen Kämpfer zur Verfügung steht (wenn er sie hat).

        Also Cooldown, Waffe etc.
        """
        if attacke.waffe:
            for waffe in self._nsc.get_waffen():
                if waffe.name == attacke.waffe:
                    break
                for klasse in waffe.item_typ:
                    if klasse.name == attacke.waffe:
                        break
            else:
                return False
        return True

    @property
    def nsc(self) -> NSC | Mänx:
        """Hole den NSC / Mänx aus der Basis"""
        return self._nsc

    def __str__(self) -> str:
        return self.anzeige.name


@define
class Kampf:
    kämpfer: list[Kämpfer]
    _mänx: Mänx
    runde: int = 0

    @staticmethod
    def neu_gegen(mänx: Mänx, gegner: Sequence[NSC]) -> 'Kampf':
        """Erzeuge einen neuen Kampf vom Mänxen gegen eine Liste von Gegnern, mit seinen
        Gefährten als Allierte."""
        kämpfer = [Kämpfer.aus_mänx(mänx)]
        for gefährte in mänx.gefährten:
            kämpfer.append(Kämpfer.aus_gefährte(gefährte))
        for n_gegner in gegner:
            kämpfer.append(Kämpfer.aus_nsc(n_gegner))
        return Kampf(kämpfer, mänx)

    def main(self, mänx: Mänx) -> 'Kampfausgang':
        self.runde = 0
        while len({a.seite for a in self.kämpfer if not a.tot}) >= 2:
            self.runde += 1
            for i, kämpfer in enumerate(self.kämpfer[:]):
                if kämpfer.tot:
                    pass
                attacke = kämpfer.controller.wähle_attacke(self, i)
                self._attacke_ausführen(kämpfer, *attacke)
        alive = {a.seite for a in self.kämpfer if not a.tot}
        if 1 in alive:
            return Kampfausgang.Sieg
        if 2 in alive:
            return Kampfausgang.Niederlage
        else:
            return Kampfausgang.Gleichstand

    def neuer_teilnehmer(self, kämpfer: Kämpfer) -> None:
        self.kämpfer.append(kämpfer)

    def _attacke_ausführen(self, angreifer: Kämpfer,
                           attacke: Fertigkeit, ziele: Sequence['Kämpfer']) -> None:
        if attacke.zieltyp == Zieltyp.Einzel:
            assert len(ziele) == 1
        else:
            assert ziele
        malp(attacke.text(angreifer, ziele))
        for ziel in ziele:
            ziel.schade(attacke.schaden)
            if isinstance(angreifer.nsc, Mänx):
                malp(_("Du machst {} Schaden an {}").format(attacke.schaden, ziel))
            elif isinstance(ziel.nsc, Mänx):
                malp(_("{} macht {} Schaden an dir").format(angreifer, attacke.schaden))
            else:
                malp(_("{} macht {} Schaden an {}").format(angreifer, attacke.schaden, ziel))


class Kampfausgang(enum.Enum):
    """Der Ausgang des Kampfes. Man kann fliehen, sterben, gewinnen oder sterben und gewinnen."""
    Flucht = 0
    Sieg = 1
    Niederlage = 2
    Gleichstand = 3


def start_kampf(
        mänx: Mänx,
        gegner: NSC | Sequence[NSC]
) -> Kampfausgang:
    """Führt einen Kampf gegen einen einzigen Gegner aus.
    Die Konsequenzen des Kampfes werden vom Aufrufenden festgelegt, diese Funktion gibt
    also lediglich zurück, wie der Kampf ausgegangen ist.

    :return: Ob der Kampf gewonnen wurde.
    """
    if isinstance(gegner, NSC):
        gegner = [gegner]
    return Kampf.neu_gegen(mänx, gegner).main(mänx)
