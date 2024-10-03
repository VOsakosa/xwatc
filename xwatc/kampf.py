"""
Beim Kampfsystem schlagen zwei Leute aufeinander ein.
"""
import random
from typing import Self, TypeAlias, Union, Sequence, List, Tuple

from attrs import define
import xwatc
from xwatc import _
from xwatc.nsc import NSC
from xwatc.system import HatMain, Mänx, Spielende, malp
import enum
__author__ = "jasper"


@define(frozen=True)
class MänxController:
    """Stellt eine Kontroller durch den Spieler dar."""

    def wähle_attacke(self, kampf: 'Kampf', idx: int) -> tuple['Attacke', Sequence['Kämpfer']]:
        kämpfer = kampf.kämpfer[idx]
        att = kampf._mänx.menu([(a.name, a.name.lower(), a) for a in kämpfer.get_attacken()],
                               frage=_("kampf>"))
        gegner = [a for a in kampf.kämpfer if a.seite != kämpfer.seite]
        if att.zieltyp == Zieltyp.Einzel and len(gegner) != 1:
            gegner = [kampf._mänx.menu([(a.name, a.name.lower(), a) for a in gegner],
                                       frage=_("Wen?"))]
        return att, gegner


@define
class AIController:
    """Stellt eine Kontrolle durch den Computer dar."""

    def wähle_attacke(self, kampf: 'Kampf', idx: int) -> tuple['Attacke', Sequence['Kämpfer']]:
        """Wählt die Attacke, die die AI durchführt."""


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
        lp = 100
        return cls(lp=lp, max_lp=lp, seite=1, controller=MänxController(),
                   anzeige=KämpferAnzeige(_("Du")), nsc=mänx)

    @classmethod
    def aus_nsc(cls, nsc: NSC) -> Self:
        """Erzeugt einen Kämpfer auf Basis eines NSCs, als Feind."""
        lp = 100
        return cls(lp=lp, max_lp=lp, seite=2, controller=AIController(),
                   anzeige=KämpferAnzeige(nsc.name), nsc=nsc)

    @classmethod
    def aus_gefährte(cls, nsc: NSC) -> Self:
        """Erzeugt einen Kämpfer auf Basis eines NSCs, als Gefährte."""
        lp = 100
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

    def get_attacken(self) -> Sequence['Attacke']:
        """Gebe die Liste von Attacken aus, die der Kämpfer gerade zur Verfügung hat."""

    @property
    def nsc(self) -> NSC | Mänx:
        """Hole den NSC / Mänx aus der Basis"""
        return self._nsc


class Zieltyp(enum.Enum):
    Alle = enum.auto()
    Einzel = enum.auto()


@define
class Attacke:
    """Eine Art von Angriff, die ein Kämpfer besitzt."""
    name: str  #: z.B. normaler Angriff
    name_kurz: str  # : z.B. normal
    schaden: int  # die Menge an Schaden in LP
    zieltyp: Zieltyp = Zieltyp.Einzel

    def text(self, angreifer: Kämpfer, verteidiger_liste: Sequence[Kämpfer]) -> str:
        """Der Text, wenn die Attacke eingesetzt wird."""
        verteidiger = [(a.name if a.name != "Du" else "dich")
                       for a in verteidiger_liste]
        if len(verteidiger) == 1:
            vers, = verteidiger
        else:
            vers = ", ".join(verteidiger[:-1]) + " und " + verteidiger[-1]

        return (f"{angreifer.name} setzt {self.name} gegen {vers} ein.")


@define
class Kampf(HatMain):
    kämpfer: list[Kämpfer]
    _mänx: Mänx

    @staticmethod
    def neu_gegen(mänx: Mänx, gegner: list[NSC]) -> 'Kampf':
        """Erzeuge einen neuen Kampf vom Mänxen gegen eine Liste von Gegnern, mit seinen
        Gefährten als Allierte."""

    def main(self, mänx: Mänx) -> None:
        self.runde = 0
        while len({a.seite for a in self.kämpfer}) > 2:
            self.runde += 1
            for i, kämpfer in enumerate(self.kämpfer[:]):
                if kämpfer.tot:
                    pass
                attacke = kämpfer.controller.wähle_attacke(self, i)
                self._attacke_ausführen(kämpfer, *attacke)

    def neuer_teilnehmer(self, kämpfer: Kämpfer) -> None:
        self.kämpfer.append(kämpfer)

    def _attacke_ausführen(self, angreifer: Kämpfer,
                           attacke: Attacke, ziele: Sequence['Kämpfer']) -> None:
        for ziel in ziele:
            ziel.schade(attacke.schaden)
        malp(attacke.text(angreifer, ziele))


class Kampfausgang(enum.Enum):
    """Der Ausgang des Kampfes. Man kann fliehen, sterben, gewinnen oder sterben und gewinnen."""
    Flucht = 0
    Sieg = 1
    Niederlage = 2
    Gleichstand = 3


def start_einzel_kampf(
        mänx: Mänx,
        gegner: xwatc.nsc.NSC  # NSC durch KampfEigenschaft oder so ersetzen
) -> Kampfausgang:
    """Führt einen Kampf gegen einen einzigen Gegner aus.
    Die Konsequenzen des Kampfes werden vom Aufrufenden festgelegt, diese Funktion gibt
    also lediglich zurück, wie der Kampf ausgegangen ist.

    :return: Ob der Kampf gewonnen wurde.
    """
    # Platzhalter, bitte durch echten Kampf ersetzen.
    xwatc.system.mint("Du kämpfst.")
    if random.random() < 0.3:
        malp("Du verlierst den Kampf.")
        return False
    else:
        malp("Du gewinnst")
        return True
