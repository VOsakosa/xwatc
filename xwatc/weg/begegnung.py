"""Untersystem des Wegsystems, dass einem zufällige Monster entgegenschmeißt.

Als Grundidee gelten drei Prototypen:

1. Die Kachel wie in lg.süden. Du triffst eine Menge von Monstern in jedem Punkt und musst dich
durchkämpfen
2. Wege wie in jtg. Wege sind unterschiedlich lang, und je nachdem, wie lange du läufst, triffst du
mehr Monster. Normalerweise triffst du nichts.
3. Dörfer wie Grökrakchöl. Mit einer sehr geringen Chance passiert etwas besonderes.

"""

from enum import Enum
import random
from collections import defaultdict
from typing import Literal, assert_never, Sequence

from attrs import define, field

from xwatc import _, nsc
from xwatc.effect import to_geschichte
from xwatc.system import Inventar, Fortsetzung, Spielende, Mänx, MänxFkt, MänxPrädikat, malp
from xwatc.weg import BeschreibungFn, WegEnde, Wegpunkt


class FluchtT(Enum):
    Flucht = 0


Flucht: Literal[FluchtT.Flucht] = FluchtT.Flucht

BegegnungFn = MänxFkt[WegEnde | Wegpunkt | None | FluchtT]


@define
class Begegnung:
    fn: BegegnungFn
    wenn_fn: MänxPrädikat | None = None
    mit_monsterspiegel: bool = False


def DEFAULT_NIEDERLAGE(*_args):
    raise Spielende


def wrap_rückkehr(ans: 'nsc.Rückkehr' | Fortsetzung) -> WegEnde | Wegpunkt | None | FluchtT:
    match ans:
        case nsc.Rückkehr.VERLASSEN:
            return Flucht
        case nsc.Rückkehr.WEITER_REDEN | nsc.Rückkehr.ZURÜCK:
            return None
        case _:
            return WegEnde.wrap(ans)


@define
class MonsterBegegnungFn(BegegnungFn):
    monster: 'nsc.StoryChar'
    beschreibung: 'nsc.DialogGeschichte'
    niederlage_fn: 'nsc.DialogGeschichte' = DEFAULT_NIEDERLAGE
    beute: Inventar = field(factory=lambda: defaultdict(int))
    kann_fliehen: bool = True
    unique: bool = True

    def __call__(self, mänx: Mänx) -> WegEnde | Wegpunkt | None | FluchtT:
        if self.unique:
            monster = mänx.welt.obj(self.monster)
            if monster.tot:
                return None
        else:
            monster = self.monster.zu_nsc()
        if ans := wrap_rückkehr(monster._call_geschichte(mänx, self.beschreibung)):
            return ans
        if self.kann_fliehen:
            optionen = [("Kämpfen", "k", True), ("Fliehen", "f", False)]
        else:
            optionen = [("Kampf beginnen", "k", True)]
        if not mänx.menu(optionen):
            return Flucht
        match kampf.start_kampf(mänx, monster):
            case kampf.Kampfausgang.Sieg:
                malp(_("Du hast gewonnen!"))
                monster.tot = True
                if mänx.ja_nein(_("Plünderst du den Gegner aus?")):
                    mänx.welt.tick(1 / 24, tag_nachricht=True)
                    monster.plündern(mänx)
                    for item, anzahl in self.beute.items():
                        mänx.erhalte(item, anzahl)
                return None
            case kampf.Kampfausgang.Flucht:
                return Flucht
            case kampf.Kampfausgang.Niederlage | kampf.Kampfausgang.Gleichstand:
                return wrap_rückkehr(monster._call_geschichte(mänx, self.niederlage_fn))
            case other:
                assert_never(other)
        return WegEnde.wrap(monster.main(mänx))


@define
class Begegnungsliste:
    """Eine Liste von Begegnungen, die einen an einem Ort treffen können.
    (wird nicht abgespeichert)"""
    id_: str
    max_monsterspiegel: int
    _begegnungen: list[Begegnung] = field(factory=list)

    def add_begegnung[T: BeschreibungFn | Sequence[str]](self, fn: T,
                                                         wenn: MänxPrädikat | None = None) -> T:
        """Füge eine Begegnung hinzu, die eine Funktion ist."""
        self._begegnungen.append(Begegnung(fn=to_geschichte(fn), wenn_fn=wenn))
        return fn

    def add_monster(self,
                    text: 'nsc.DialogGeschichte',
                    template: "nsc.StoryChar",
                    *,
                    unique: bool = False, wenn: MänxPrädikat | None = None,
                    mit_monsterspiegel: bool = True) -> None:
        """Füge ein Monster hinzu, das dich angreift."""
        self._begegnungen.append(
            Begegnung(MonsterBegegnungFn(template, text, unique=unique), wenn_fn=wenn,
                      mit_monsterspiegel=mit_monsterspiegel))

    @property
    def begegnungen(self) -> Sequence[Begegnung]:
        return self._begegnungen


@define
class Begegnungsausgang:
    """Der Ausgang einer Begegnung, wird zurückgegeben, nachdem eine Begegnung fertig durchgeführt
    wurde."""
    ausgang: WegEnde | Wegpunkt | None | FluchtT


@define(kw_only=True)
class Monstergebiet:
    """Ein Gebiet, in dem Monster spawnen und innerhalb des Gebiets umherziehen.
    (wird abgespeichert)

    Das Besiegen von Monstern innerhalb des Gebiets verringert die Gesamtanzahl von Monstern im
    Gebiet (Monsterpegel)
    """
    begegnungen: Begegnungsliste
    monsterspiegel: int

    def betrete(self, mänx: Mänx) -> None:
        """Betrete das Monstergebiet und regeneriere die Monster."""

    def nächste_begegnung(self, mänx: Mänx) -> Begegnungsausgang | None:
        """Suche eine Begegnung mit einem Monster heraus und führe sie aus."""
        begegnungen = [b for b in self.begegnungen.begegnungen if
                       b.wenn_fn is None or b.wenn_fn(mänx)]
        if not begegnungen:
            return None
        begegnung = random.choice(begegnungen)
        if (begegnung.mit_monsterspiegel and
                random.random() > self.monsterspiegel / self.begegnungen.max_monsterspiegel):
            return None
        return Begegnungsausgang(self.run_begegnung(mänx, begegnung))

    def run_begegnung(self, mänx: Mänx, begegnung: Begegnung) -> WegEnde | Wegpunkt | None | FluchtT:
        """Führe eine Begegnung mit einem Monster aus."""
        return begegnung.fn(mänx)


from xwatc.weg import _kreuzung as kreuzung  # noqa
from xwatc import kampf  # noqa
