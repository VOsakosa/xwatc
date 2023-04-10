"""
Hält die Converter-Klasse, die zum Serialisieren der Daten dient.
Created on 24.03.2023
"""
from typing import Final
import cattrs.preconf.pyyaml

__author__ = "jasper"
# Der unfertige Converter.
converter: Final = cattrs.preconf.pyyaml.make_converter()
_functions_added = False

# Stellt sicher, dass der Converter fertig ist


def mache_converter() -> cattrs.preconf.pyyaml.PyyamlConverter:
    """Hole den Converter, mit allen Dump-Funktionen bereit."""
    global _functions_added
    if not _functions_added:
        _add_fns()
    return converter


def _add_fns() -> None:
    """Fügt die Converter-Funktionen dem Converter hinzu."""
    from xwatc.system import Mänx
    omit = cattrs.gen.override(omit=True)

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
