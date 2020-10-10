from xwatc.scenario import ScenarioEnde, Weg

def baum(mänx, obj, scen):
    obj = obj.replace("Baum", "", 1).strip()
    if obj:
        print(f"Du schlägst dem Baum ein {obj} ab")
        mänx.inventar[obj] += 10
    if mänx.hat_item("Axt"):
        print("Du fällst den Baum. +10 Holz")
        mänx.inventar["Holz"] += 10
        return Weg()
    else:
        if not obj:
            print("Du hast nichts, mit dem du diesen Baum fällen könntest.")
        return Weg(wird_zu="Baum")

def o_t2_d2(mänx, scen):
    print("Nachdem du den Mann angegriffen hast, kommt ein anderer von hinten und spaltet dich mit "
          "seiner Axt entzwei")
    return ScenarioEnde(tot=True)

def o_t2_d1(mänx, scen):
    print("Der Mann ist wachsam, so als hätte er deinen Angriff geahnt.")
    print("Im Gegensatz zu dir hat dieser Mann viel Kampferfahrung und er hat keinerlei Skrupel, einen "
          "aggressiven Fremden zu töten.")
    return ScenarioEnde(tot=True)
    

KÄMPFEN = {
    "O:T2:D1": o_t2_d1,
    "O:T2:D2": o_t2_d2,
}

def kämpfen(mänx, obj, scen):
    if obj.startswith("Baum"):
        return baum(mänx, obj, scen)
    elif obj in KÄMPFEN:
        return KÄMPFEN[obj](mänx, scen)
    raise ValueError(obj, "hat noch keine Geschichte")