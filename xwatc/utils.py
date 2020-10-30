"""
Generelles
Created on 23.10.2020
"""
__author__ = "jasper"


def uartikel(geschlecht: str, fall: int = 1):
    """Der unbestimmte Artikel"""
    if geschlecht == "p":
        return ""
    elif geschlecht == "n" or geschlecht == "m":
        return ["einem", "ein", "eines"][fall % 3]
    elif fall == 1 or fall == 4:
        return "eine"
    else:
        return "einer"

def bartikel(geschlecht: str, fall: int = 1):
    if geschlecht == "n":
        return ["dem", "das", "des"][fall % 3]
    elif geschlecht == "m":
        return ["den", "der", "des", "dem"][fall % 4]
    elif fall == 1 or fall == 4:
        return "die"
    elif fall == 2 or fall==3 and geschlecht == "f":
        return "der"
    else:
        return "den"