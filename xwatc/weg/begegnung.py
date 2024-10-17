"""Untersystem des Wegsystems, dass einem zufällige Monster entgegenschmeißt.

Als Grundidee gelten drei Prototypen:

1. Die Kachel wie in lg.süden. Du triffst eine Menge von Monstern in jedem Punkt und musst dich
durchkämpfen
2. Wege wie in jtg. Wege sind unterschiedlich lang, und je nachdem, wie lange du läufst, triffst du
mehr Monster. Normalerweise triffst du nichts.
3. Dörfer wie Grökrakchöl. Mit einer sehr geringen Chance passiert etwas besonderes.

"""

import random
from typing import Sequence
from attrs import define, field

from xwatc import nsc
from xwatc.effect import to_geschichte
from xwatc.system import Mänx, MänxPrädikat
from xwatc.weg import WegEnde, Wegpunkt, BeschreibungFn


@define
class Begegnung:
    fn: BeschreibungFn
    wenn_fn: MänxPrädikat | None = None
    mit_monsterspiegel: bool = False


@define
class MonsterBegegnungFn(BeschreibungFn):
    monster: 'nsc.StoryChar'
    unique: bool

    def __call__(self, mänx: Mänx) -> WegEnde | Wegpunkt | None:
        if self.unique:
            monster = mänx.welt.obj(self.monster)
            if monster.tot:
                return None
        else:
            monster = self.monster.zu_nsc()
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

    def add_monster(self, template: "nsc.StoryChar", *,
                    unique: bool = False, wenn: MänxPrädikat | None = None,
                    mit_monsterspiegel: bool = True) -> None:
        """Füge ein Monster hinzu."""
        self._begegnungen.append(
            Begegnung(MonsterBegegnungFn(template, unique=unique), wenn_fn=wenn,
                      mit_monsterspiegel=mit_monsterspiegel))

    @property
    def begegnungen(self) -> Sequence[Begegnung]:
        return self._begegnungen


@define
class Begegnungsausgang:
    """Der Ausgang einer Begegnung, wird zurückgegeben, nachdem eine Begegnung fertig durchgeführt
    wurde."""
    ausgang: WegEnde | Wegpunkt | None


@define(kw_only=True)
class Monstergebiet:
    """Ein Gebiet, in dem Monster spawnen und innerhalb des Gebiets umherziehen.
    (wird abgespeichert)

    Das Besiegen von Monstern innerhalb des Gebiets verringert die Gesamtanzahl von Monstern im
    Gebiet (Monsterpegel)
    """
    begegnungen: Begegnungsliste
    monsterspiegel: int
    herkunft: "kreuzung.NachbarKey | None" = None

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

    def run_begegnung(self, mänx: Mänx, begegnung: Begegnung) -> WegEnde | Wegpunkt | None:
        """Führe eine Begegnung mit einem Monster aus."""
        return begegnung.fn(mänx)


from xwatc.weg import _kreuzung as kreuzung  # noqa
