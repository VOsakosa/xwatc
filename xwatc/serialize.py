"""
Hält die Converter-Klasse, die zum Serialisieren der Daten dient.
Created on 24.03.2023
"""
from typing import Any, Final, TYPE_CHECKING
import cattrs.preconf.pyyaml
from logging import getLogger

if TYPE_CHECKING:
    from xwatc import system

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
    from xwatc.weg import Gebiet, Wegkreuzung
    omit = cattrs.gen.override(omit=True)
    
    def kreuzung_un(kreuzung: Wegkreuzung) -> list[str]:
        return [kreuzung.gebiet.name, kreuzung.name]
    
    converter.register_unstructure_hook(Wegkreuzung, kreuzung_un)
    
    
    def _welt_unstructure(welt: Welt) -> dict:
        base = _welt_unstructure_base(welt)
        objekte: dict[str, Any] = {}
        for key, obj in welt._objekte.items():
            match obj:
                case float() | int():
                    objekte[key] = obj
                case NSC():
                    if type(obj) != NSC:
                        _logger.warn("Unterklasse von NSC kann nicht richtig gespeichert werden"
                                     f": {type(obj)}")
                    objekte[key] = converter.unstructure(obj, NSC)
                case Gebiet():
                    objekte[key] = None
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

    def _mänx_unstructure(m: Mänx) -> dict:
        base = _mänx_unstructure_base(m)
        base["gefährten"] = [gefährte.template.id_ for gefährte in m.gefährten]
        return base

    converter.register_unstructure_hook(Mänx, _mänx_unstructure)

    _welt_unstructure_base = cattrs.gen.make_dict_unstructure_fn(
        Welt, converter,
        _objekte=omit,
    )

def mache_strukturierer(mänx: 'system.Mänx'):
    """Mache einen Strukturierer, der an den Mänxen gebunden ist und damit
    die Erzeugerfunktionen bedienen kann."""
    from xwatc.weg import Gebiet, Wegkreuzung, finde_kreuzung, get_gebiet
    
    conv = converter.copy()
    
    def gebiet_st(in_: str, _typ) -> Gebiet:
        return get_gebiet(mänx, in_)

    def kreuzung_st(in_: list[str], _typ) -> Wegkreuzung:
        gebiet, name = in_
        return finde_kreuzung(mänx, gebiet, name)

    conv.register_structure_hook(Gebiet, gebiet_st)
    conv.register_structure_hook(Wegkreuzung, kreuzung_st)

    
