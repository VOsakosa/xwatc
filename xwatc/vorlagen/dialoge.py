"""
Vorlagen für Dialoge.

Created on 10.04.2023
"""
from xwatc import _
from xwatc.nsc import Dialog, NSC
__author__ = "Jasper Ischebeck"


def hallo(n: NSC, _m) -> bool:
    n.sprich(_("Hallo, ich bin {name}. "
               "Freut mich, dich kennenzulernen.").format(name=n.name))
    return True


def hallo2(n: NSC, _m) -> bool:
    n.sprich(_("Hallo nochmal!"))
    return True


HalloDialoge = [
    Dialog("hallo", "Hallo", hallo).wiederhole(1),
    Dialog("hallo2", "Hallo", hallo2, "hallo")
]
