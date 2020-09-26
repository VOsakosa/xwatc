from xwatc.scenario import ScenarioEnde

def baum(mänx):
    print("Der Baum antwortet nicht. Warum auch?")

def o_t2_d2(mänx, scen):
    print("Fred:", "Willkommen in Disnajenbun! Ich bin der Dorfvorsteher Fred.")
    print("Fred:", "Ruhe dich ruhig in unserem bescheidenen Dorf aus.")

def o_t2_d1(mänx, scen):
    print("Ein grimmiger Dorfbewohner mit Axt steht vor dir.")
    print("Olaf:", "..")
    

REDEN = {
    "O:T2:D1": o_t2_d1,
    "O:T2:D2": o_t2_d2,
}

def reden(mänx, obj, scen):
    if obj.startswith("Baum"):
        return baum(mänx)
    elif obj in REDEN:
        return REDEN[obj](mänx, scen)
    raise ValueError(obj, "hat noch keine Geschichte")