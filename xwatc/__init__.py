"""Xwatc ist ein textbasiertes RPG mit Fokus auf Geschichte."""

from pathlib import Path
import gettext as gettext_module

try:
    translations: gettext_module.NullTranslations = gettext_module.translation(
        "xwatc", Path(__file__).parent / "locales",
        # languages=["dari"],
    )
except FileNotFoundError:
    translations = gettext_module.NullTranslations()
_ = translations.gettext

from . import system
from . import weg
from . import dorf
