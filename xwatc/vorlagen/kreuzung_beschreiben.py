"""
Texte, um Kreuzungen anhand ihrer Struktur automatisch zu beschreiben. Wir ohnehin kaum
genutzt und wird deshalb ausgelagert.
Created on 02.04.2023
"""
from xwatc.weg import Wegkreuzung, Richtung, Himmelsrichtung, Wegtyp, HIMMELSRICHTUNGEN, cap
from xwatc.system import malp
import random
__author__ = "Jasper Ischebeck"


def slice_richtung(kreuzung: Wegkreuzung, richtung: int = 0) -> list[Richtung | None]:
    """Gebe die Richtungen der Kreuzung, von richtung betrachtet, aus."""
    return [kreuzung.nachbarn.get(Himmelsrichtung.from_nr(hri % 8)) for hri in
            range(richtung, richtung + 8)]


def _finde_texte(kreuzung: Wegkreuzung, richtung: int) -> list[str]:
    """Finde die Beschreibungstexte, die auf die Kreuzung passen."""
    rs = slice_richtung(kreuzung, richtung)
    ans: list[str] = []
    min_arten = 8
    for flt, txt in WEGPUNKTE_TEXTE:
        typen: dict[int, Wegtyp] = {}
        art_count = 0
        for stp, tp in zip(rs, flt):
            if tp == 0 and stp is None:
                continue
            elif tp != 0 and stp is not None:
                if tp in typen:
                    if typen[tp] != stp.typ:
                        break
                else:
                    art_count += 1
                    typen[tp] = stp.typ
            else:
                break
        else:
            if art_count < min_arten:
                ans.clear()
            elif art_count > min_arten:
                continue
            ans.append(txt.format(w=typen))
    return ans


def beschreibe_kreuzung(kreuzung: Wegkreuzung, richtung: int | None):  # pylint: disable=unused-argument
    """Beschreibe die Kreuzung anhand ihrer Form."""
    rs = slice_richtung(kreuzung)
    if richtung is not None:
        texte = _finde_texte(kreuzung, richtung)
        if texte:
            malp(random.choice(texte))
        else:
            malp("Du kommst an eine Kreuzung.")
            for i, ri in enumerate(rs):
                if ri and i != richtung:
                    malp(cap(ri.typ.text(False, 1)), "führt nach",
                         HIMMELSRICHTUNGEN[i] + ".")

    else:
        malp("Du kommst auf eine Wegkreuzung.")
        for i, ri in enumerate(rs):
            if ri:
                malp(cap(ri.typ.text(False, 1)), " führt nach ",
                     HIMMELSRICHTUNGEN[i] + ".")


WEGPUNKTE_TEXTE: list[tuple[list[int], str]] = [

    ([1, 0, 0, 0, 2, 0, 0, 0], "{w[1]:111} wird zu {w[2]:03}"),
    # Kurven
    ([1, 1, 0, 0, 0, 0, 0, 0],
     "{w[1]:111} macht eine scharfe Biegung nach links."),
    ([1, 0, 1, 0, 0, 0, 0, 0],
     "{w[1]:111} biegt nach links ab."),
    ([1, 0, 1, 0, 0, 0, 0, 0],
     "Du biegst nach links ab."),
    ([1, 0, 0, 1, 0, 0, 0, 0],
     "{w[1]:111} macht eine leichte Biegung nach links."),
    ([1, 0, 0, 0, 1, 0, 0, 0], "{w[1]:111} führt weiter geradeaus."),
    ([1, 0, 0, 0, 0, 1, 0, 0],
     "{w[1]:111} macht eine leichte Biegung nach rechts."),
    ([1, 0, 0, 0, 0, 0, 1, 0],
     "{w[1]:111} biegt nach rechts ab."),
    ([1, 0, 0, 0, 0, 0, 0, 1],
     "{w[1]:111} macht eine scharfe Biegung nach rechts."),
    # T-Kreuzungen
    ([1, 0, 2, 0, 0, 0, 2, 0], "{w[1]:111} endet orthogonal an {w[2]:03}."),
    ([1, 2, 0, 0, 0, 2, 0, 0], "{w[1]:111} mündet in {w[2]:04}, {w[2]:g1} von "
     "scharf links nach rechts führt."),
    ([1, 2, 0, 0, 2, 0, 0, 0], "{w[1]:111} vereinigt sich mit {w[2]:03}, der geradeaus "
     "weiterführt."),
    ([1, 0, 2, 0, 1, 0, 2, 0], "{w[2]:011} kreuzt senkrecht."),
    ([1, 0, 0, 0, 0, 0, 0, 0], "Eine Sackgasse.")
]
