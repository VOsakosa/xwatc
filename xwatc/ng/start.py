"""Der Start in das Spiel, mit Wahl der Waffe etc."""
from typing import Any
from xwatc.system import Mänx, malp

Fortsetzung = tuple[str, str]

punkt: Any = None


def Option(name, kurz, val):
    return name, kurz, val


@punkt("ng:start")  # das definiert einen Wegpunkt, bekannt unter einem Namen.
def neuer_start(mänx: Mänx, _richtung: str) -> Fortsetzung:
    """Das ist der Anfang. Es ist eine Geschichtsfunktion. Sie erhält drei Parameter:
    `mänx`, um mit dem System zu interagieren und `richtung`, die Richtung aus der
    dieser Punkt erreicht wurde."""
    # Mit malp wird dem Spieler Text mitgeteilt.
    malp("Hallo! Ich bin die Erzählerin und werde dir helfen, deinen Charakter zu wählen.")
    # Mit minput und dem mächtigeren menu fragst du den Spieler
    waffe = mänx.minput("Wähle zunächst aus drei Waffen: Schwert, Speer und Schild. "
                        "Welche passt am besten zu dir?", ["Schwert", "Speer", "Schild"])
    mänx.erhalte(waffe, 1)
    malp("Jetzt bist du gut gerüstet, um in den Kampf zu ziehen!")
    # malp("Jetzt musst du noch lernen, sie anzulegen!")
    # TODO Waffe anlegen
    malp("Du wachst auf, völlig allein, in einem fremden Körper und ohne Erinnerung.")
    # Jetzt geht es weiter nach Gäfdah, aus Richtung 's'. 's' steht generell für Süden.
    # der Ort heißt eigentlich ng:tal, aber es wird lokal gesucht.
    return "tal", "s"


@punkt("ng:tal")
def tal(mänx: Mänx, richtung: str) -> Fortsetzung:
    if richtung == "s":
        malp("Du stehst in einem schmalen Tal mit steilen Wänden, zu steil, um sie zu erklimmen.")
    else:  # Hier kannst du zum ersten Mal aus der anderen Richtung kommen.
        malp("Du gehst wieder zurück in das Tal")
    return mänx.menu([
        Option("Tiefer ins Tal", kurz="tiefer", val=("talende","s")),
        Option("Aus dem Tal hinaus", kurz="hinaus", val=("gäfdah", "n")),
    ], "Wohin gehst du?")

@punkt("ng:talende")
def talende(_m, _ri) -> Fortsetzung:
    malp("Das Tal ist abrupt zu Ende. Mit einem kleinen Wasserfall stürzt ein Bach hinab.")
    malp("Alle Seiten des Tals sind zu steil. Du kannst nur zurückgehen.")
    return "ng:tal", "n"