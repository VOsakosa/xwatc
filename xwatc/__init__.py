"""Xwatc ist ein textbasiertes RPG mit Fokus auf Geschichte."""

from pathlib import Path
import gettext as gettext_module

translations = gettext_module.translation(
    "xwatc", Path(__file__).parent / "locales",
    # languages=["dari"],
)
_ = translations.gettext

from . import system
from . import weg
from . import dorf
