"""
Created on 25.07.2021
"""
from __future__ import annotations
import pyparsing as pp
from pyparsing import Combine, Group, Regex, OneOrMore, delimitedList, Suppress,\
    ParseResults, delimitedList

import os
import typing
from typing import Dict, TextIO, Optional as Opt
from karvapedo.main import TextId, Möglichkeiten
import karvapedo

GESCHICHTEN = os.path.join(os.path.dirname(__file__), "..", "geschichten")

stack = [1]
Statement = pp.Forward()
Block = pp.indentedBlock(Statement, stack)
Identifier = Regex(r"\w[\w\d]*")
Pfad = Combine(pp.Opt(".") + delimitedList(Identifier, ".", combine=True))
PythonExpression = Regex(".*")

Tag = Group(Suppress("!") + Identifier + OneOrMore(Statement))
Text = pp.QuotedString(quoteChar='"', escChar="\\") + pp.Opt("n")

FunktionP = Group(Identifier + Suppress("(") +
                 pp.Opt(delimitedList(Identifier)) + Suppress(")"))
AuswahlKopf = Group(
    "+" + (Identifier | pp.QuotedString(quoteChar='"', escChar="\\")) + ":")
Auswahl = AuswahlKopf + Block
Eingabe = OneOrMore(Auswahl)
If = pp.Keyword("if") + PythonExpression + ":" + Block
Sprung = Group("&" + Pfad)
Random = pp.Keyword("random") + pp.Word(pp.nums)("Weight") + ":" + Block

Statement << (Text | FunktionP | Eingabe | If | Random | Sprung)

Geschichte = pp.OneOrMore(Tag)


def _parse_eingabe(tokens):
    return {kopf[1]: [b[0] for b in block] for kopf, block in zip(*([iter(tokens)] * 2))}


Eingabe.setParseAction(_parse_eingabe)

Marken = Dict[TextId, ParseResults]


def get_marken(tokens, root: str) -> Marken:
    """Finde alle Marken im geparsten Input."""
    root = root + "."
    ans: Marken = {}
    for tag in tokens:
        tagname, *block = tag
        tagname = root + tagname
        _marken_in_block(tagname, block, ans)
    return ans


def _marken_in_block(name: TextId, block, ans: Marken):
    ans[name] = block
    for i, stmt in enumerate(block):
        if isinstance(stmt, list) and stmt[0] == "&":
            if i != len(block) - 1:
                print(f"Fehler in {name}: Weitere Befehle nach Sprung &{stmt[i]}")
            break
        elif isinstance(stmt, dict):
            for auswahl, subblock in list(stmt.items()):
                subblock = subblock[:]
                if isinstance(subblock, str):
                    continue
                elif isinstance(subblock[-1], ParseResults) and subblock[-1][0] == "&":
                    if len(subblock) == 1:
                        stmt[auswahl] = subblock[0][1]
                        continue
                else:
                    subblock.extend(block[i+1:])
                blockname = name + "!" + auswahl
                stmt[auswahl] = blockname
                _marken_in_block(blockname, subblock, ans)
            break

class GeladeneGeschichte(karvapedo.main.Geschichte):
    def __init__(self, root: str = GESCHICHTEN):
        self.root = root
        self.geladen: set[str] = set()
        self.marken: Marken = {}

    def save(self, _file: TextIO):
        """Speichert die Geschichte"""
        pass

    @staticmethod
    def load(_file: TextIO) -> GeladeneGeschichte:
        """Lädt die Geschichte aus der Datei. Der Geschichtenname ist
        bereits eingelesen."""
        return GeladeneGeschichte()

    def starts(self) -> Möglichkeiten:
        ans = []
        for dir in os.listdir(self.root):
            if os.path.exists(os.path.join(self.root, dir, "haupt.txt")):
                ans.append((dir, dir + ".haupt.haupt"))
        return ans

    def finde_text(self, textid: TextId) -> karvapedo.main.Text:
        """Führe einen Text aus."""
        self.finde_marke(textid)
        inhalt: list[str] = []
        mgn = self.führe_aus(textid, inhalt)
        return "\n".join(inhalt), mgn or []

    def finde_marke(self, textid: TextId) -> None:
        """Versuche, eine Marke zu importieren."""
        path, __, name = textid.rpartition(".")
        if path not in self.geladen:
            self.marken.update(lade_geschichte(path, self.root))

    def führe_aus(self, marke: TextId, text: list[str]) -> Opt[Möglichkeiten]:
        tokens = self.marken[marke]
        for tok in tokens:
            if isinstance(tok, str):
                text.append(tok)
            elif isinstance(tok, dict):
                return list(tok.items())
            elif isinstance(tok, ParseResults):
                if tok[0] == "&":
                    neue_marke = self.resolve_path(tok[1], base=marke)
                    return self.führe_aus(neue_marke, text)
                else:
                    self.run_func(list(tok))
        return None

    def resolve_path(self, path: str, base: TextId) -> TextId:
        """Löse einen Pfad auf."""
        if path[0] == ".":
            self.finde_marke(path[1:])
            return path[1:]
        while True:
            parent, __, __ = base.rpartition(".")
            if not parent:
                break
            test = parent + "." + path
            self.finde_marke(test)
            if test in self.marken:
                return test
        raise KeyError(f"Unbekannte Sprungmarke: {path}")

    def run_func(self, args: list[str]):
        # raise ValueError("Funktion unbekannt.")
        pass # TODO


def lade_geschichte(datei: str, root: str = GESCHICHTEN) -> Marken:
    """Lade die Geschichte datei, z.B. xwatc.haupt

    :raise: ParseBaseException"""
    stack[:] = [1]
    pfad = os.path.join(root, *datei.split(".")) + ".txt"
    with open(pfad, "r") as file:
        ans = Geschichte.parseString(file.read().expandtabs(4), parseAll=True)
    return get_marken(ans, datei)


if __name__ == '__main__':
    from pprint import pprint
    Auswahl.setDebug(True)
    print(Group("!" + Identifier).parseString("!Popel", True))
    print(Auswahl.parseString("+weiter:\n\t&Papel", True))
    stack[:] = [1]
    try:
        
        geschichte = """
!Popel
"Ohjemine"
"Vor langer Zeit, in einem fernen Land, da starb ein rechter Hundemann."
gebe(Popel)
+weiter:
    &Papel
+nochmal:
    &haupt.Yopel
!Papel
"Hier ist ein totes Ende"
+weiter:
    &.xwatc.jtg.haupt
+"blubb":
    pass()
+banane:
    "Du wählst die Banane"
    +"sicher":
        &Banane
    +dochnicht:
        pass()
"Hinten war noch etwas versteckt."

!waffe_wählen
"Was willst du sein?"
+Mensch:
    "Eine langweilige Entscheidung"
    "Bist du dir sicher?"
    +Ja:
        "Na dann ist ja alles gut"
    +Nein:
        "Jetzt kann ich daran auch nichts mehr ändern"
+"was anderes":
    "Das steht noch nichts zur Verfügung"
        """.expandtabs(4)
        # parsed = (Geschichte.parseString(geschichte, True))
        # print(parsed)
        # pprint(get_marken(parsed, root="popel"))

    except pp.ParseBaseException as exp:
        print(exp.explain(exp))

    print(GeladeneGeschichte().finde_text("xwatc.haupt.waffe_wählen!Mensch"))
