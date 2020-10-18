GÄFDA_NAME = "Gäfda"

def erzeuge_süd_dorf(mänx) -> Dorf:
    d = Dorf(GÄFDA_NAME)
    kirche = Ort("Kirche", [
        "Du bist in einer Kirche.",
    
    ])
    
    schmiede = Ort("Schmiede", [
        "Du kommst in einen warmen, kleinen Raum, der irgendwie gemütlich wirkt und nach Schweiß riecht."
        
        "Hinter der Theke steht ein bulliger Mann und verkauft wohl Waffen, Rüstungen und Anderes."
    
    ])
    
    rathaus = Ort("Rathaus", [
        "Du kommst in ein großes Haus mit Marmorfußboden.",
        
        "Drei Wachen kommen auf dich zu."
        
    
    ])
    
    haus1 = Ort("Haus1", [
        "Du kommst in ein kleines Haus."
    
    ])
    kirche.menschen.append(mänx.welt.get_or_else(
        "jtg:m:tobiac", TobiacBerndoc))
    d.orte.append(kirche)
    kirche.menschen.append(mänx.welt.get_or_else(
        "jtg:m:tobiac", TobiacBerndoc))
    d.orte.append(kirche)
    kirche.menschen.append(mänx.welt.get_or_else(
        "jtg:m:tobiac", TobiacBerndoc))
    d.orte.append(kirche)
    kirche.menschen.append(mänx.welt.get_or_else(
        "jtg:m:tobiac", TobiacBerndoc))
    d.orte.append(kirche)
    for _i in range(randint(2, 5)):
        w = zufälliges_waschweib()
        w.dialoge.extend(SÜD_DORF_DIALOGE)
        d.orte[0].menschen.append(w)
    # TODO weitere Objekte
    return d

mänx.welt.get_or_else("jtg:dorf:süd", erzeuge_süd_dorf, mänx).main(mänx)