"""
Hält die Converter-Klasse, die zum Serialisieren der Daten dient.
Created on 24.03.2023
"""
from xwatc.untersystem.person import Rasse
from xwatc.untersystem.variablen import get_var_typ, MethodSave

from attrs import define
import cattrs.preconf.pyyaml
from typing_extensions import assert_never

from importlib import import_module
from logging import getLogger
from types import FunctionType
from typing import Any, Final, TYPE_CHECKING


if TYPE_CHECKING:
    from xwatc import system, weg, nsc  # @UnusedImport

__author__ = "jasper"
# Der unfertige Converter.
converter: Final = cattrs.preconf.pyyaml.make_converter()
_functions_added = False
_logger: Final = getLogger("xwatc.serialize")

# Stellt sicher, dass der Converter fertig ist


def mache_converter() -> cattrs.preconf.pyyaml.PyyamlConverter:
    """Hole den Converter, mit allen Dump-Funktionen bereit."""
    global _functions_added
    if not _functions_added:
        _add_fns()
    return converter


def _add_fns() -> None:
    """Fügt die Converter-Funktionen dem Converter hinzu."""
    from xwatc.system import Mänx, Welt
    from xwatc.nsc import NSC
    from xwatc.weg import Wegkreuzung
    from xwatc import system  # @Reimport
    omit = cattrs.gen.override(omit=True)

    def kreuzung_un(kreuzung: Wegkreuzung) -> list[str]:
        return [kreuzung.gebiet.name, kreuzung.name]

    converter.register_unstructure_hook(Wegkreuzung, kreuzung_un)

    def _welt_unstructure(welt: Welt) -> dict:
        base = _welt_unstructure_base(welt)
        objekte: dict[str, Any] = {}
        for key, obj in welt._objekte.items():
            typ = get_var_typ(key)
            match obj:
                case float() | int():
                    objekte[key] = obj
                case NSC():
                    if type(obj) != NSC:
                        _logger.warning("Unterklasse von NSC kann nicht richtig gespeichert werden"
                                        f": {type(obj)}")
                    objekte[key] = converter.unstructure(obj, NSC)
                case [*_]:
                    objekte[key] = converter.unstructure(obj, list[NSC])
                case _ if typ:
                    objekte[key] = converter.unstructure(obj, typ)
                case _:
                    _logger.warn(f"Unbekannte Art Objekt bei {key}({type(obj)}) kann nicht "
                                 "gespeichert werden.")
                    objekte[key] = None

        base["objekte"] = objekte
        return base

    converter.register_unstructure_hook(Welt, _welt_unstructure)

    _mänx_unstructure_base = cattrs.gen.make_dict_unstructure_fn(
        Mänx, converter,
        gefährten=omit,
        _geladen_von=omit,
        ausgabe=omit,
        context=omit,
        speicherdatei_name=omit)
    _mänx_structure_base = cattrs.gen.make_dict_structure_fn(Mänx, converter)
    _welt_unstructure_base = cattrs.gen.make_dict_unstructure_fn(
        Welt, converter,
        _objekte=omit,
        _gebiete=omit,
    )

    def _mänx_unstructure(m: Mänx) -> dict:
        base = _mänx_unstructure_base(m)
        base["gefährten"] = [gefährte.template.id_ for gefährte in m.gefährten]
        return base

    def _mänx_structure(dict_: dict, _typ: type) -> Mänx:
        mänx = _mänx_structure_base(dict_, Mänx)
        mänx.ausgabe = system.ausgabe
        conv2 = mache_strukturierer(mänx)
        if "rasse" in dict_:
            mänx.person.rasse = Rasse(dict_["rasse"])
        # Objekte
        key: str
        for key, value in dict_["welt"]["objekte"].items():
            try:
                match value:
                    case _ if typ := get_var_typ(key):
                        mänx.welt.setze_objekt(key, conv2.structure(value, typ))
                    case None:  # Gebiet oder aus Register @UnusedVariable
                        mänx.welt.obj(key)
                    case float() | int():
                        mänx.welt.setze_objekt(key, value)
                    case []:
                        mänx.welt.setze_objekt(
                            key, conv2.structure(value, list[NSC]))
                    case {"template": str()}:
                        mänx.welt.setze_objekt(
                            key, conv2.structure(value, NSC))
            except cattrs.errors.ClassValidationError as cve:
                missing_ids, rest = cve.split(system.MissingIDError)
                if missing_ids:
                    for exc in missing_ids.exceptions:
                        if isinstance(exc, system.MissingIDError):
                            _logger.error(
                                f"Missing ID while loading: {exc.id_}")
                if rest:
                    raise rest from None
            except system.MissingIDError as err:
                _logger.error(f"Missing ID while loading: {err.id_}")
            except system.MissingID as exc:
                _logger.exception(exc)
        mänx._geladen_von = structure_punkt(dict_["punkt"], mänx)
        return mänx

    converter.register_unstructure_hook(Mänx, _mänx_unstructure)
    converter.register_structure_hook(Mänx, _mänx_structure)


def mache_strukturierer(mänx: 'system.Mänx') -> cattrs.Converter:
    """Mache einen Strukturierer, der an den Mänxen gebunden ist und damit
    die Erzeugerfunktionen bedienen kann."""
    from xwatc.weg import Gebiet, Wegkreuzung, finde_punkt, get_gebiet

    conv = converter.copy()

    def gebiet_st(in_: str, _typ) -> Gebiet:
        return get_gebiet(mänx, in_)

    def kreuzung_st(in_: list[str], _typ) -> Wegkreuzung:
        gebiet, name = in_
        ans = finde_punkt(mänx, gebiet, name)
        assert isinstance(ans, Wegkreuzung)
        return ans

    conv.register_structure_hook(Gebiet, gebiet_st)
    conv.register_structure_hook(Wegkreuzung, kreuzung_st)
    return conv


def unstructure_punkt(punkt: 'system.Speicherpunkt') -> Any:
    from xwatc import weg, nsc, scenario  # @Reimport
    match punkt:
        case weg.Wegkreuzung(gebiet=gebiet, name=name):
            return {"gebiet": gebiet.name, "ort": name}
        case FunctionType(__qualname__=name, __module__=module):
            assert "." not in name, "Nur Top-Level-Funktionen können Speicherpunkte sein."
            return {"fn": module + "." + name}
        case MethodSave(method=method, obj=obj):
            return {"obj": obj, "method": method}
        case nsc.NSC(ort=weg.Wegkreuzung(gebiet=gebiet, name=name), template=nsc.StoryChar(id_=id_)):
            return {"nsc": id_, "gebiet": gebiet.name, "ort": name}
        case nsc.NSC():  # @UnusedVariable
            raise ValueError("NSC außerhalb eines Ortes kann nicht gespeichert werden.")
        case scenario.ScenarioWegpunkt():
            return {"gebiet": punkt.gebiet.name, "ort": punkt.name}
        case _ if callable(punkt):
            raise TypeError("Savepunkt ist zwar callable, aber keine Funktion mit Namen.")
        case _:
            assert_never(punkt)


def structure_punkt(punkt: Any, mänx: 'system.Mänx') -> 'system.Fortsetzung':
    from xwatc.weg import finde_punkt, Wegkreuzung
    match punkt:
        case [str(gebiet), str(name)]:
            return finde_punkt(mänx, gebiet, name)
        case {"gebiet": str(gebiet), "ort": str(name)}:
            return finde_punkt(mänx, gebiet, name)
        case {"nsc": str(id_), "gebiet": str(gebiet), "ort": str(name)}:
            ort = finde_punkt(mänx, gebiet, name)
            assert isinstance(ort, Wegkreuzung)
            return BesucheNSC(mänx.welt.obj(id_), ort)
        case {"fn": str(function_name)}:
            package, __, fun = function_name.rpartition(".")
            ans = getattr(import_module(package), fun)
            assert callable(ans)
            return ans
        case {"obj": str(objekt_name), "method": str(methoden_name)}:
            return getattr(mänx.welt.obj(objekt_name), methoden_name)
        case _:
            raise ValueError("Unbekanntes Format für Speicherpunkt.")


@define
class BesucheNSC:
    nsc: 'nsc.NSC'
    kreuzung: 'weg.Wegkreuzung'

    def __str__(self) -> str:
        return f"BesucheNSC({self.nsc.name}, {self.kreuzung})"

    def main(self, mänx: 'system.Mänx') -> 'system.Fortsetzung':
        if ans := self.nsc.main(mänx):
            return ans
        return self.kreuzung
