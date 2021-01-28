"""
Modul für Hilfetexte
Created on 30.10.2020
"""
__author__ = "jasper"

SCENARIO = [
    "Das ist ein Scenario. Du bewegst dich, indem du w, a, s oder d eingibst.",
    "Wenn du gegen einen Menschen läufst, interagierst du mit ihm.",
    "Du beendest das Scenario, indem du aus dem Spielfeldrand läufst.",
    "Und ach ja, dein Charakter ist übrigens das Y bzw. 主."
]

HANDELSMENU = [
    "Das ist das Handelsmenu.",
    "Der Befehl a zeigt eine Auslage, mit 'k [Anzahl] [Item]' kannst du "
    "kaufen und mit 'v [Anzahl] [Item]' verkaufen.",
    "Verlasse den Händler mit 'f'. ",
    "Vergiss nicht, mit ihm normal zu *r*eden!"
]

INVENTAR_ZUGRIFF = [
    "Das ist ein Zugriff auf ein Inventar.",
    "Du kannst Sachen mit 'n' nehmen und mit 'g' (geben) verstauen",
    "Schreibe einfach 'n', wenn du alles nehmen und dann verlassen willst."
]

LEERE = [
    "Wie du vielleicht schon weißt, ein Scherz-Item.",
    "Es hat momentan noch keine Funktion."
]
HILFEN = {
    "scenario": SCENARIO,
    "handel": HANDELSMENU,
    "inventar_zugriff": INVENTAR_ZUGRIFF,
}
ITEM_HILFEN = {
    "leere": LEERE
}
