from time import sleep
from xwatc import haendler
from xwatc import scenario
from xwatc.system import Mänx, minput, ja_nein, Spielende, mint, sprich



def t2(mänx: Mänx):
    """Jaspers Teilgeschichte"""
    print("Hinter der Tür ist es warm und sonnig.")
    sleep(1)
    print("Es erwartet dich Vogelgezwitscher")
    sleep(1)
    print("Du befindest sich auf einer Lichtung in einem Wald.")
    print("Ein schmaler Pfad führt nach Norden")
    print("Im Osten ist Dickicht")
    mint("Im Westen und Süden ist nichts besonderes")
    beeren = False
    cont = True
    while cont:
        cont = False
        richtung = minput(mänx, "Gehst du nach Norden, Osten, Westen oder Süden? norden/süden/westen/"
                          "osten", ["osten", "süden", "westen", "norden"])
        if richtung == "norden":
            print("Der kleine Pfad stößt spitz auf einen Weg von links.")
            weiter = minput(
                mänx, "Willst du dem Weg folgen [f] oder scharf links abbiegen?[abb]", ["f", "abb"])
            if weiter == "f":
                t2_norden(mänx)
            else:
                t2_west(mänx)
        elif richtung == "osten":
            if not beeren:
                print("Du findest Beeren")
                mänx.inventar["Beere"] += 10
                print("Aber du kommst hier nicht weiter")
            minput(mänx, "Umkehren?")
            cont = True
            beeren = True
        elif richtung == "süden":
            t2_süd(mänx)
        else:  # Westen
            print("Du triffst auf einen Weg")
            if minput("Rechts oder Links?", ["r", "l"]) == "r":
                t2_norden(mänx)
            else:
                t2_west(mänx)


def t2_norden(mänx):
    """Das Dorf auf dem Weg nach Norden"""
    print("Auf dem Weg kommen dir mehrfach Leute entgegen, und du kommst in ein kleines Dorf")
    mädchen = haendler.Händler("Mädchen", kauft=["Kleidung"], verkauft={
                               "Rose": [1, 1]}, gold=0)

    def vorstellen():
        print("Am Wegesrand siehst du ein Mädchen in Lumpen. Sie scheint zu frieren.")

    def preis(_):
        return 0
    mädchen.vorstellen = vorstellen
    mädchen.get_preis = preis
    if "k" == mädchen.handeln(mänx):
        print("Das Mädchen ist schwach. Niemand hindert dich daran, sie auf offener Straße zu schlagen.")
        print("Sie hat nichts außer ihren Lumpen", end="")
        if mädchen.verkauft["Rose"]:
            print(
                ", die Blume, die sie dir verkaufen wollte, ist beim Kampf zertreten worden.")
        else:
            print(".")
        del mädchen.verkauft["Rose"]
        mädchen.plündern(mänx)
    elif "Mantel" in mädchen.verkauft:
        print("Das Mädchen bedeutet dir, dass sie nur den halben Mantel braucht.")
        print("Du schneidest den Mantel entzwei, und gibst ihr nur die Hälfte.")
        mänx.inventar["halber Mantel"] += 1
        mänx.titel.add("Samariter")
    elif mädchen.verkauft["Rose"][0] == 0:
        print("Das Mädchen ist dankbar für das Stück Gold")
    if "Unterhose" in mädchen.verkauft:
        print(
            "Das Mädchen ist sichtlich verwirrt, dass du ihr eine Unterhose gegeben hast.")
        print("Es hält sie vor sich und mustert sie. Dann sagt sie artig danke.")
        mänx.titel.add("Perversling")
    minput(mänx, "Du kommst im Dorf Disnayenbun an.")
    if "osten" == scenario.lade_scenario(mänx, "disnajenbun"):
        t2_no(mänx)
    else:
        t2_nw(mänx)


def t2_süd(mänx):
    print("Der Wald wird immer dunkler")
    mint("Ein kalter Wind weht. Das Vogelgezwitscher der Lichtung kommt dir nun "
          "wie ein kurzer Traum vor.")
    mint("Es wird immer dunkler")
    print("Plötzlich siehst du ein Licht in der Ferne")
    haus = ja_nein(mänx, "Gehst du zum Licht?")
    if haus:
        print("Es ist eine einsame, einstöckige Hütte, aus der das Licht kam. "
              "Vor dir ist die Rückseite des Hauses, "
              "an der sich Feuerholz stapelt.")
        haus = ja_nein(mänx, "Klopfst du an die Tür?")
    if haus:
        print("Ein junger Mann begrüßt dich an der Tür.")
        aktion = mänx.minput(
            '?: "Ein Wanderer? Komm herein, du siehst ganz durchgefroren aus."[k/r/f]',
            list("krf"))
        if aktion == "f":
            print(
                "Du rennst weg, als hätte der bloße Anblick des jungen Manns dich verschreckt.")
            print('Jetzt denkt der Arme sich bestimmt: "Bin ich so hässlich oder schrecklich, dass Leute auf den '
                  'ersten Blick abhauen?"')
            print("Aber dir ist das egal, die unbekannte Gefahr ist abgewehrt.")
            ende_des_waldes(mänx)
        elif aktion == "k":
            print('?: "Ein/e Inquisitor/in? Dafür musst du früher aufstehen!"')
            hexer_kampf(mänx)
        else:  # "r"
            haus_des_hexers(mänx)
    else:
        print("Dem, der auch immer hinter dem Licht steckt, sollte man nicht "
              "trauen, befindest du und machst "
              "dich weiter "
              "auf den Weg durch den Wald.")
        ende_des_waldes(mänx)


def haus_des_hexers(mänx):
    print("Er bittet dich an den Tisch und gibt dir einen warmen Punsch.")
    leo = 'Leo Berndoc'
    sprich(leo, "Ich bin Leo Berndoc.")
    sprich(leo, "Was suchst du in diesem Wald?")
    antwort = mänx.minput(
        "Halloli! Was mach ich wohl in deinem Haus?[halloli]/ "
        "Ich habe mich hier verirrt.[verirrt]/ "
        "Ich bin nur auf der Durchreise.[durchreise]/ "
        "Die große Liebe![liebe]/ "
        "Ich bin einfach in den Osten ­– weil da keine Menschen sind – gegangen, "
        "und dann war da diese Oase. Da waren zwei Türen. "
        "Ich habe mir ein Herz gefasst, bin durch die Tür gegangen und hier bin ich. Plötzlich.[oase]/ "
        "Das gehst dich doch nichts an![an]",
        ["verirrt", "halloli", "durchreise", "liebe", "oase", "an"])
    if antwort == "halloli":
        print("Er sagt mit einem verschwörischen Tonfall: \"Ich verstehe.\"")
        sprich(leo, "Bleibe ruhig noch die Nacht. Hier werden sie dich nicht finden.")
        print("Du entschließt dich, mitzumachen. Am nächsten Tag verlässt du schnell das Haus, bevor der Schwindel "
              "auffliegt")
        ende_des_waldes(mänx, True)
    elif antwort == "verirrt" or antwort == "an":
        sprich(leo, "Soso.")
        sleep(1)
        sprich(leo, "...")
        sleep(1)
        sprich(leo, "Ich habe ein Gästebett. Da kannst du schlafen.")
        print("Dein erstes Bett in dieser Welt ist schön weich.")
        sleep(3)
        print("Als du am nächsten Morgen aufwachst, fühlst du dich schwach und kalt.")
        print("Leo steht vor dir.")
        sprich(leo, "Du bist jetzt eine wandelne Leiche und gehorchst meinem Willen")
        raise Spielende()
    elif antwort == "durchreise":
        sprich(leo, "Schade. Trotzdem-Schön, dich getroffen zu haben. Im Süden ist ein Dorf, "
               "da kannst du als nächstes hin.")
        sprich(leo, "Du musst einfach immer geradeaus dem schmalen Pfad folgen.")
        ende_des_waldes(mänx)
    elif antwort == "liebe":
        sprich(
            leo, "Glaubst du denn an die wahre Liebe, die, die alle Widrigkeiten überwindet?")
        if ja_nein(mänx, "Ja/Nein"):
            sprich(leo, "Du bist also eine/r von denen!")
            sprich(leo, "Ich schwöre auf meinen Namen, ich werde dich hier auslöschen!")
            sleep(1)
            sprich(leo + "(flüstert)", "Ich werde Lena rächen.")
            hexer_kampf(mänx)
        else:
            sprich(leo, "Und warum nicht?")
            ant = mänx.minput("Weil Liebe Ordnung haben muss. Auch die Liebe kann sich nicht über "
                              "alles hinwegsetzen.[1]/\n"
                              "Dass sie alles Widrigkeiten überwindet, das ist zu optimistisch. Aber "
                              "ich werde nie aufgeben.[2]/\n"
                              "Diese Liebe meine ich nicht. Ich meine die Nächstenliebe, das Gute im "
                              "Menschen und die Güte Gottes. Die habe ich in deiner Gastfreundschaft "
                              "gefunden.[3]")
            if ant == "2":
                sprich(leo, "Du bist also eine/r von denen!")
                sprich(leo, "Du denkst, nur weil du liebst, kann du die Ehre der Berndoc ignorieren und "
                            "mit ihr zusammenkommen!")
                sleep(0.5)
                sprich(
                    leo, "Ich schwöre auf meinen Namen, ich werde dich hier auslöschen!")
                hexer_kampf(mänx)
            else:
                sprich(leo, "Interessant.")
                sprich(leo, "Ich habe ein Gästebett. Da kannst du schlafen.")
                sprich(leo, "Im Süden ist ein Dorf, lauf einfach weiter geradeaus.")
                print("Dein erstes Bett in dieser Welt ist schön weich.")
                sleep(5)
                ende_des_waldes(mänx, True)
    else:  # oase
        sprich(leo, "Interessant.")
        print("Er wirkt sichtlich überfordert.")
        sprich(leo, "Das muss eine Tür der Qual sein..., oder war es Wal der Qual...")
        sleep(0.3)
        sprich(leo, "Aber was hat ein Wal hier zu suchen?")
        print("Du hast ihn sichtlich verwirrt.")
        mint("Er zeigt noch auf ein Gästezimmer, dann geht er vor sich hin brabbelnd in sein Zimmer")
        mint("Im Bett denkst du über deinen heutigen Tag nach. Du sinkst "
              "in einen unruhigen Schlaf.")
        sleep(5)
        print("Früh am Morgen verlässt du eilig das Haus.")
        mint("Aber du siehst noch einen Ring auf dem Tisch.")
        if ja_nein(mänx, "Steckst du ihn ein?"):
            mänx.erhalte("Ring des Berndoc")
        sprich(leo, "Ich hab's! Es ist ein Wahlqualportal!!!")
        ende_des_waldes(mänx, True)


def hexer_kampf(mänx):
    print("Der Mann spricht einen schnellen Zauberspruch. Dir wird unglaublich kalt.")
    if mänx.get_kampfkraft() > 2000:
        print("Aber du bist stärker.")
        print("Du besiegst den Mann und plünderst sein Haus.")
        mänx.erhalte("Gold", 120)
        mänx.erhalte("Mantel", 3)
        mänx.erhalte("Unterhose", 7)
        mänx.erhalte("Banane", 1)
        mänx.erhalte("Menschenskelett", 3)
        print("Du findest einen Ring. In ihm steht eingraviert: "
              "\"Ich hasse dich, Dongmin!\"")
        mänx.erhalte("Ring des Berndoc")
        print("Du entscheidest dich, nach Süden weiterzugehen")
        sleep(2)
    else:
        print("Du kannst dich kaum bewegen. Er tritt auf dich drauf.")
        sleep(0.5)
        print("Dein Rücken tut weh")
        sleep(0.5)
        print("Aber er zeigt Gnade. ", end="")
        if mänx.hat_item("Unterhose"):
            print("Er zieht dich bis auf die Unterhose aus", end="")
        else:
            print("Er zieht dich aus, verzieht das Gesicht, als er sieht, "
                  "dass du keine Unterhose trägst", end="")
        print(" und wirft dich im Süden des Waldes auf den Boden")
        mänx.inventar_leeren()
    ende_des_waldes(mänx)


SÜD_DORF_GENAUER = [
    "Das Dorf besteht aus einer Handvoll Holzhütten sowie zwei Fachwerkhäusern.",
    "Die meisten Dorfbewohner glauben an den Gott des Marschlandes, "
    "wie an den Schnitzereien an den Türrahmen erkennbar",
    "Die Dorfbewohner haben größtenteils schwarze Haare und leicht gebräunte "
    "Haut.",
]


def ende_des_waldes(mänx, morgen=False):
    print("Der Wald wird schnell viel weniger unheimlich")
    if not morgen:
        print("Erschöpft legst du dich auf den Waldboden schlafen.")
        sleep(2)
    print("Im Süden siehst du ein Dorf")
    mänx.genauer(SÜD_DORF_GENAUER)
    pass


def t2_west(mänx):
    pass


def t2_no(mänx):
    pass


def t2_nw(mänx):
    pass
