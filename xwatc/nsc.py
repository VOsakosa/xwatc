"""Ein NSC-System, das das Template (bei Kompilierzeit erstellt, im Code) und den
gespeicherten Teil trennt. Bei Erstellung soll alles einen eindeutigen Namen haben.
"""

from attrs import define, Factory
from enum import Enum
from collections.abc import Mapping
from xwatc.system import Inventar
from xwatc import dorf


class Geschlecht(Enum):
    Weiblich = 0
    Männlich = 1


class Rasse(Enum):
    Mensch = 0
    Munin = 1


@define
class Person:
    """Definiert Eigenschaften, die jedes intelligente Wesen in Xvatc hat."""
    geschlecht: Geschlecht
    rasse: Rasse


@define
class StoryChar:
    """Ein weltweit einzigartiger Charakter, mit eigenen Geschichten."""
    id_: str
    """Eine eindeutige Identifikation, wie jtg:torobiac"""
    name: str
    """Das ist der Ingame-Name, wie "Torobias Berndoc". """
    person: Person
    startinventar: Mapping[str, int]
    direkt_reden: bool = True
    """Ob bei dem NSC-Menu die Rede-Optionen direkt angezeigt werden."""

    def zu_nsc(self) -> 'NSC':
        """Erzeuge den zugehörigen NSC aus dem Template."""
        return NSC(self, dict(self.startinventar))


@define
class RandomChar:
    """Ersetzt bei zufällig generierten NSCs :py:`StoryChar`."""
    name: str
    person: Person
    # TODO unfertig.


NSCTemplate = StoryChar | RandomChar


@define
class NSC:
    """Ein NSC, mit dem der Spieler interagieren kann. Alles konkretes ist in template und
    der Rest der Datenstruktur beschäftigt sich mit dem momentanen Status dieses NSCs in der
    Welt."""
    template: NSCTemplate
    inventar: Inventar
    variablen: set[str] = Factory(set)
    dialog_anzahl: dict[str, int] = Factory(dict)
    kennt_spieler: bool = False
    tot: bool = False
    ort: dorf.Ort | None = None
