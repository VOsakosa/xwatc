"""
Das Dorf zwischen der Lichtung und dem Disnayenbum.

Treffen auf Elen und Quest nach Ehering.

Ehering
-------

Die Holzfällerin Saxa hat beim Kräutersammeln im Wald westlich von Mitose
ihren Ehering verloren. Sie glaubt, dass der Ring ihr und ihrem Mann
Glück gebracht hat und sorgt sich. Der Ehering ist bei den Kräutern.
Links abbiegen führt zu Kiri-Wölfen=> Kampf

"""
from xwatc.system import Mänx, register
from xwatc.dorf import NSC
__author__ = "jasper"


@register("jtg:saxa")
def erzeuge_saxa():
    n = NSC("Saxa Kautohoa", "Holzfällerin",
            startinventar={
                "Unterhose": 1,
                "Hemd": 1,
                "Strumpfhose": 1,
                "Socke": 1,
                "BH": 1,
                "Kappe": 1,
                "Hose": 1,
                "Gold": 14,
            }, vorstellen="Eine Holzfällerin von ungefähr 40 Jahren steht vor dir.")
    n.dialog("hallo", "Hallo", "Hallo, ich bin Saxa.")
    n.dialog("bedrückt", "Bedrückt dich etwas?",
             [
                 "Ich habe beim Kräutersammeln meinen Ehering im Wald verloren.",
                 "Er hat uns beiden immer Glück gebracht.",
                 "Du bist doch ein Abenteurer, kannst du den Ring finden?"
             ])
    # Dialog für Ehering-Suche
    return n
