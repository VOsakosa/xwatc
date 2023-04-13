from xwatc import _
from xwatc.system import (Mänx, Spielende, mint, malp)
from xwatc.nsc import StoryChar, Sprich, NSC, Malp, Dialog

# TODO: Als Angestellte dürften sie um ihren Lohn feilschen.

dialog_wetter = Dialog("wetter", '"Wie findest du das Wetter heute?"', [
    "Schön", Malp("Das sagt sie, ohne aufzublicken")])
dialog_gehen = Dialog("geht", '"Wie geht es dir?"', "Was kümnmert dich das?")

MinkajaOrekano = StoryChar("lg:osten:minkaja", ("Minkaja", "Orekano", _("Magd")))
MinkajaOrekano.dialog("geige", '"Stimmt es, dass du Geige spielst?"', "Ja. Warum fragst du?")
MinkajaOrekano.dialoge.append(dialog_gehen)
MinkajaOrekano.dialoge.append(dialog_wetter)
MinkajaOrekano.dialoge.append(Dialog.ansprechen_neu([Sprich("Tag. Was ist?")]))


@MinkajaOrekano.kampf
def minkaja_kampf(_nsc: NSC, _mänx: Mänx) -> None:
    malp("Sie weicht aus.")
    malp("Wer hätte gedacht, dass sie so schnell sein konnte?")
    mint("Dann schnellt ihr Messer vor und du verendest elendig röchelnd.")
    raise Spielende


ThonaTantavan = StoryChar("lg:osten:thona", ("Thona", "Tantavan", "Magd"))
ThonaTantavan.dialog("hallo", '"Hallo, wie heißt du?"', "Hallo, ich heiße Thona.")
MinkajaOrekano.dialoge.append(dialog_gehen)
ThonaTantavan.dialoge.append(dialog_wetter)
