from xwatc import haendler
from xwatc.system import Mänx, malp
from xwatc.lg.norden import Fischerfrau_Massaker
from xwatc.nsc import StoryChar, Person, NSC
from xwatc.lg.norden import gäfdah


frau = StoryChar("lg:norden:Maria_Fischfrisch:maria_fischfrisch",
                 ("Maria", "Fischfrisch", "Fischerfrau"),
                 Person("w"),
                 gäfdah.STANDARDKLEIDUNG | {
                     "Unterhose": 0,
                     "Brokat-Unterhose": 1},
                 vorstellen_fn="Die Fischerfrau verkauft Fische.")
haendler.mache_händler(frau, kauft=["Blume"], gold=200, verkauft={
    "Hering": (4, 6),
    "Sardelle": (13, 5),
    "Lachs": (4, 8)})


@frau.kampf
def kampf(nsc: NSC, mänx: Mänx) -> None:
    Fischerfrau_Massaker.fischerfraumassaker(mänx)
    nsc.tot = True


@frau.dialog_deco('bist', '"Hallo, Wer bist du?"')
def reden_bist(nsc: NSC, mänx: Mänx) -> None:
    malp('(freundlich) "Ich heiße Maria. Und du?"')
    if "tot" not in mänx.minput(': '):
        malp('"Das ist aber ein schöner Name."')
    else:
        malp('"Tod?"')


frau.dialog("wetter", '"Wie findest du das Wetter heute?"',
            "Schön, mein Kind.")


@frau.dialog_deco("geht", '"Wie geht es dir?"')
def reden_geht(nsc, _):
    nsc.sprich("Mir geht es gut. Wie geht es dir?")
    k = input("")
    if k == "gut" or "sehr gut" or "super gut" or "wirklich gut" or "wirklich sehr gut":
        nsc.sprich("Das ist aber schön.")
    else:
        nsc.sprich("oh")
    # TODO: Hing, als hier Rückkehr.WEITER_REDEN stand
