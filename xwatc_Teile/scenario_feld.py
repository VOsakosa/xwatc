from xwatc.scenario import ScenarioEnde

def osten(mänx, scenario):
    return ScenarioEnde(ergebnis="osten")

def westen(mänx, scenario):
    return ScenarioEnde(ergebnis="westen")

TREFFE = {
    "Osten": osten,
    "Westen": westen,
}

def treffe(mänx, feld, scenario):
    if feld in TREFFE:
        return TREFFE[feld](mänx, scenario)
    return None