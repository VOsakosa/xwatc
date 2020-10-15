"""
Die große Feste von Grökrakchöl mitsamt umliegender Landschaft und See.
Created on 15.10.2020
"""
__author__ = "jasper"
from xwatc.system import mint, Mänx

GENAUER = [
    "Hinter der Festung fangen Felder an.",
    "In vier Richtungen führen Wege weg, nach Norden, Nordosten, Südosten "
    "und nach Westen. Der Weg nach Norden ist aber nur ein Pfad.",
    "In den vier Ecken der Festung stehen Türme, dabei ist der im Südosten "
    "besonders groß.",
    "Um den Kern der Festung gibt es noch eine zweite Mauer. Zwischen den "
    "Mauern sind wohl die Häuser der normalen Bevölkerung."
]

def zugang_ost(mänx: Mänx):
    """Zugang zu Grökrak aus dem Osten"""
    mint("Der Weg führt das Südwesten aus dem Wald heraus.")
    if mänx.welt.ist("kennt:grökrakchöl"):
        mint("Vor dir siehst du Grökrakchöl.")
    else:
        print("Vor dir bietet sich ein erfurchterregender Anblick:")
        mint("In der Mitte einer weiten Ebene ragt eine hohe quadratische "
             "Festung hervor.")
    mänx.genauer(GENAUER)
    grökrak(mänx)

def zugang_südost(mänx: Mänx):
    """Zugang aus Scherenfeld"""
    print("Du folgst dem Weg. Auf der linken Seite sind Felder.")
    mint("Du kommst in eine Streuobstwiese.")
    print("Du siehst Äpfel, Zwetschgen und Aprikosen.")
    if mänx.ja_nein("Willst du einige pflücken?"):
        mänx.erhalte("Aprikose", 14)
        mänx.erhalte("Apfel", 5)
        mänx.erhalte("Zwetschge", 31)
        print("Niemand hat dich gesehen.")
    print("Der Weg überquert mit einer Brücke einen Bach. Am Bach stehen Bäume,"
          " die "
         "dir die Aussicht auf ", end="")
    if mänx.welt.ist("kennt:grökrakchöl"):
        mint("Grökrakhöl verbargen.")
    else:
        mint("eine große quadratische Festung verbargen.")
    mänx.genauer(GENAUER)
    grökrak(mänx)

def grökrak(mänx: Mänx):
    if mänx.ja_nein("Willst du die Festung betreten?"):
        gkrak = mänx.welt.get_or_else("jgt:dorf:grökrakchöl", erzeuge_grökrak)
        gkrak.main()
    
    
        
def erzeuge_grökrak():
    """"""