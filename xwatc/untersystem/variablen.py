"""
Klassen für Welt-Variablen. Eine Variable besteht aus einem Namen, einem Typ und
einer Funktion, diese Variable aus dem Rest der Welt zu initialisieren.
"""
from attrs import define
from collections.abc import Callable
from logging import getLogger
from typing import Generic, TypeVar, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from xwatc.system import Welt
__author__ = "jasper"
_logger = getLogger("xwatc.system")

VT = TypeVar("VT")


@define
class WeltVariable(Generic[VT]):
    """Eine Variable der Welt, mit Typ und Factory."""
    name: str
    typ: type[VT]
    erzeuger: Callable[['Welt'], VT]

    def __attrs_post_init__(self):
        if self.name in _WELT_VARIABLEN:
            _logger.warning(f"Welt-Variable {self.name} doppelt registriert.")
        _WELT_VARIABLEN[self.name] = self


def Variable(name: str, default: VT, typ: type[VT] | None = None) -> WeltVariable[VT]:
    """Eine Variable mit festen Default-Wert.

    a = Variable("jtg:see_gesehen", 0)
    def zu_see_kommen(mänx: Mänx):
        mänx.welt.setze(a, mänx.welt.obj(a) + 1)
    """
    return WeltVariable(name, typ or type(default), lambda _welt: default)


def erzeuge_objekt(name: str, typ: type[VT]
                   ) -> Callable[[Callable[['Welt'], VT]], WeltVariable[VT]]:
    """Eine Variable mit einer Erzeuger-Funktion."""
    def wrapper(erzeuger: Callable[[Welt], VT]) -> WeltVariable[VT]:
        return WeltVariable(name, typ, erzeuger)
    return wrapper


TT = TypeVar("TT", bound=type)


def register(name: str) -> Callable[[TT], TT]:
    """Registriere eine Klasse im Objekt-Register.
    Beispiel:
    ..
        from attrs import define
        @register("system.test.banana")
        @define
        class Banane:
            leckerheit: float = 1.2

        def test(mänx: Mänx):
            banane: Banane = mänx.welt.obj(Banane)
    """

    def wrapper(typ: TT) -> TT:
        if hasattr(typ, "erzeuge"):
            erzeuger = getattr(typ, "erzeuge")
        else:
            erzeuger = typ
        setattr(typ, '_variable', WeltVariable(name, typ, erzeuger))
        return typ

    return wrapper


def get_var_typ(name: str) -> type | None:
    if name in _WELT_VARIABLEN:
        return _WELT_VARIABLEN[name].typ
    return None


def get_welt_var(name: str) -> WeltVariable[Any] | None:
    return _WELT_VARIABLEN.get(name)


_WELT_VARIABLEN: dict[str, WeltVariable[Any]] = {}
