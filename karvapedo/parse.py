"""
Created on 25.07.2021
"""
import pyparsing as pp
from pyparsing import Combine, Group, Regex, Optional, OneOrMore, delimitedList

stack = [1]
Statement = pp.Forward()
Block = pp.indentedBlock(Statement, stack)
Identifier = Regex(r"\w[\w\d]*")
PythonExpression = Regex(".*")

Tag = Combine("!" + Identifier) + OneOrMore(Statement)
Text = pp.QuotedString(quoteChar='"', escChar="\\") + Optional("n")

Funktion = Group(Identifier+"("+Optional(delimitedList(Identifier))+")")
AuswahlKopf = "+" + (Identifier|pp.QuotedString(quoteChar='"', escChar="\\")) + ":"
Auswahl = AuswahlKopf + Block
If = pp.Keyword("if") + PythonExpression + ":" + Block
Sprung = "&"+ Identifier
Random = pp.Keyword("random") + pp.Word(pp.nums)("Weight") + ":" + Block

Statement << (Text | Funktion | Auswahl | If | Random | Sprung)

Geschichte = pp.OneOrMore(Tag)

if __name__ == '__main__':
    print(Group("!" + Identifier).parseString("!Popel", True))
    print(Auswahl.parseString("+weiter:\n\t&Papel", True))
    try:
        print(Geschichte.parseString("""
        !Popel
        "Ohjemine"
        "Vor langer Zeit, in einem fernen Land, da starb ein rechter Hundemann."
        gebe(Popel)
        +weiter:
            &Papel
        +nochmal:
            &Yopel
        """, True))
    except pp.ParseBaseException as exp:
        print(exp.explain(exp))