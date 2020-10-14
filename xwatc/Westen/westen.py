from time import sleep
import xwatc_Hauptgeschichte as xwatc
from xwatc.system import Mänx, minput, Gefährte, ja_nein

def westen(mänx):
    print("Mit einer kühlen, entgegenkommenden Meeresbrise wanderst du in Richtung Westen.")
    sleep(1)
    print("Da begegnete dir eine Henne"
          ", die auf einem Stein hockt.")
    moral=minput(mänx, "f/w/k/r (fliehen/weiter/kämpfen/reden)", ["f","w","k","r"])
    
    if moral=="w":
        print("Du gehst einfach g"
              "erade heraus. Du b"
              "emerkst erst das d"
              "u den Atem angehal"
              "ten hast, als du i"
              "n sicherem Abstand"
              "zum Huhn ausatmest.")
        
    elif moral=="k":
        print("Du tötest das Huhn"
              " und es ist als wä"
              "re ein Bann von di"
              "r abgefallen. Plöt"
              "zlich bist du wied"
              "er vergnügt und en"
              "tspannt.")
        if ja_nein(mänx, "durchsuchst du das Huhn?   "):
            mänx.inventar["Hühnerfleisch"] += 5
            mänx.inventar["Stein der aussieht wie ein Hühnerei"] += 1
            mänx.inventar["Mugel des Sprechens"] += 1
            mänx.inventar["Verfluchtes Gold"] += 50
            
    elif moral=="r":
         mänx.fähigkeiten.add("Mit Tieren reden")
         print("Erstaunlicherweise kann das Huhn sprechen.")
         print('"Hallo", sagt das Huhn. Sie dir mein schönes Eierchen an!')
         sleep(1)
         print('Du siehst dir das "Ei" an. Und bemerkst, das es einfach nur ein Stein ist. ')
         sleep(1)
         print("Was sagst du?")
         sleep(1)
         print("1: Ahäm. Das ist kein Ei")
         sleep(1)
         print("2: Plopp. Ich bin ein hässliches kleines Fischibischi (Kbörg)")
         sleep(1)
         print("3: Tut mir wirklich sehr leid, missiör Henne, a"
               "ber das ist lediglich ein hässliches Ei!")
         sleep(1)
         print("4:OOOkay! Tschüss")
         sleep(1)
         print("5:Bye")
         sleep(1)
         print("6:Ja, es ist wirklich sehr schön.")
         sleep(1)
         print("7:Reden wir über etwas anderes. Bitte.")
         sleep(1)
         print("8:Tut mir wirklich sehr leid, mi"
               "ssiör(Monsieur) Henne, aber das "
               "ist lediglich ein hässlicher Stein")
         sleep(1)
         print("9:Tut mir wirklich sehr leid, Madam "
                "Henne, aber das ist lediglich ein "
                "hässliches Ei!")
         sleep(1)
         print("10:Tut mir wirklich sehr leid, Madam "
               "Henne, aber das ist lediglich ein"
                "hässlicher Stein!")
         sleep(1)
         nett=minput(mänx, "Was sagst du? 1/2/3/4/5/6/7/8/9/10",
                     ["1","2","3","4","5","6","7","8","9","10"])
                     
         if nett=="1":
             print('Die Henne starrt dich an.'
                       '"Wie kannst du es wagen!", kreischt sie.'
                       'Für einen Augenblick sieht sie sehr, sehr wütend aus.'
                       'Dann verschwindet sie in einer Wolke aus Federn und Staub.')
                 
             
         if nett=="2":
             print('"Hä?" Einen Augenblick guckt die Henne dich nur verständnislos an.'
                       'Dann sagt sie feierlich: "Du bist würdig."'
                       ', und gibt dir eine seltsame Kugel, "das Hühnerei" und etwas Geld.'
                       'Danach krähte und gackerte sie noch etwas,'
                       'doch du konntest sie nicht mehr verstehen. ')
             mänx.inventar["Stein der aussieht wie ein Hühnerei"] += 1
             mänx.inventar["Mugel des Sprechens"] += 1
             mänx.inventar["Gold"] += 50
                 
             
         if nett=="3":
             print("Die Züge der Henne froren ein. Die Henne war die Ausdruckslosigkeit in Pers... Huhn.")
             print("Das Huhn guckt dich an.")
             sleep(1)
             print("Das Huhn guckt dir tief in die Augen.")
             sleep(3)
             print("Das Huhn guckt dir sehr tief in die Augen.")
             sleep(5)
             print("sehr, sehr tief")
             sleep(6)
             leben=minput(mänx, "Langsam wird dir übel."
                              "Kotzt du einfach hemmungslos oder hältst du es zurück?"
                              "(ko/z)", ["ko","z"])
             if leben=="ko":
                 print("Du erbrichst dich über dem Huhn, brichst den Bann und fliehst.")
             elif leben=="z":
                 print("Das Huhn dringt durch die Augen in dich ein und ... verändert dort etwas.")
                 print("Plötzlich wird dir klar, dass du ein Wurm bist. ")
                 sleep(3)
                 print("Das Huhn pickt")
                 sleep(3)
                 print("aua")
                 raise Spielende
                 
                            
                 
         if nett=="4":
             print("Den Blick des Huhns auf dir spürend, machst du dich von dannen.")
                 
                 
         elif nett=="5":
             print("Du beachtest den verwirrten Blick des Huhns nicht und gehst du davon.")
                 
                 
         elif nett=="6":
             print('"Ja, findest du nicht auch?" Mit geschwellter Brust watschelt das Huhn davon')
                 
                 
         elif nett=="7":
             print( 'Verwirrt betrachtet dich das Huhn noch einmal eingehend.'
                    '"Ja, worüber willst du denn reden?", fragt es.')
             print("1. Wo liegt die nächste menschliche Ansiedlung?")
             print("2. Wie findest du das Wetter?")
             print("3. Kannst du mir irgentetwas beibringen? ")
             print("4. Wie kommt es, dass du sprechen kannst?")
             cmal=minput(mänx, "1/2/3/4",["1","2","3","4"])
             if cmal=="1":
                 print("Plötzlich wirkt das Huhn sehr verlegen."
                       "Statt dir zu antworten, "
                       "springt es ins Gebüsch und verschwindet.")
             elif cmal=="2":
                 print('"sehr schön, sehr schön...", murmelt die Henne.'
                       'Dann springt sie plötzlich auf und schreit in die Welt hinaus:'
                       '"Bei gutem Wetter sollte man auf Wanderschaft gehen.'
                       'Kreischend packt sie ihr "Ei" und rennt davon."')
             elif cmal=="3":
                 print('"Ja, das kann ich", sprach die Henne.'
                       'Sie wirkte plötzlich sehr ernst und weise.'
                       '"Aber dann musst du mich mit Meisterin Kraagkargk ansprechen.')
                 ja=minput ( mänx, "Ja Meisterin Kraagkargk/Nein Meis"
                             "terin Kraagkargk/Ja/nein (jm/nm/j/n)", [jm,nm,n,j])
                 if ja==jm:
                     mint('"Gut", sagte Meisterin Kraagkargk')
                     print("Du musst jetzt leider eine Minute warten.")
                     sleep(60)
                     print("Meisterin Kraagkargk huscht in die Nacht davon "
                           "und du schlägst auf einer Wiese in der Nähe dein Lager auf.")
                     sleep(3)
                     print('Info: Du hast hast "verrückter Schrei" gelernt!')
                     print('Jeder der ihn hört, reagiert anders.')
                     print('Manche weinen, manche lachen, manche wiederum erbrechen sich.–')
                     print('Auf jeden Fall verschafft es dir einige Minuten der Ablenkung!')
                 if ja==nm:
                     print('Meisterin Kraagkargk wurde wütend.'
                           '"So gehe doch", rief sie theatralisch und ging selbst.')
                 if ja==n:
                     print("Meisterin Kraagkargk guckt dich kurz an und ging dann.")
                 if ja==j:
                     print('Meisterin Kraagkargk schnaubte und stolzierte beleidigt davon.')
                             
                     
                 elif cmal=="4":
                     print('"Das liegt an meinem Mugel des Sprechens", '
                           'sagte die Hühnerdame und lief durch deine "dumme" Frage empört davon.')
                 
                 
                 
             elif nett=="8":
                 print("Die Züge der Henne wurden starr. Die Henne wurde die Ausdruckslosigkeit in Pers.. Huhn.")
                 print("Und sie guckt dich an.")
                 sleep(1)
                 print("Guckt dir tief in die Augen.")
                 sleep(3)
                 print("tiefer")
                 sleep(5)
                 print("noch tiefer")
                 sleep(6)
                 leben=minput(mänx, "Dir wird übel."
                              "Erbrichst du dich du einfach hemmungslos oder hältst du es zurück?"
                              "(er/z)", [er,z])
                 if leben=="er":
                     print("Du erbrichst dich über dem Huhn, brichst den Bann und fliehst.")
                 elif leben=="z":
                     print("Das Huhn kriecht durch deine Augen in dich ein und ... verändert dort etwas.")
                     print("Plötzlich wird dir klar, dass du ein Wurm bist. ")
                     sleep(3)
                     print("Das Huhn pickt")
                     sleep(3)
                     print("aua")
                     raise Spielende
                            
                 
         elif nett=="9":
                 print("Die Henne kreischt.")
                 print("lauter als ein Löwe,")
                 print("schriller als ein Adler,")
                 mint("totbringender als eine Banshee.")
                 raise Spielende
                
         elif nett=="10":
                 print("Erst blickt dich das Huhn wütend an, dann verschwindet es.")
         
    elif moral=="f":
        print("Du entkommst dem Huhn mühelos.")
        sleep(1)
        print("Nach einer Weile kommst du wieder dort an wo du losgelaufen bist.")
        xwatc.himmelsrichtungen(mänx)
            