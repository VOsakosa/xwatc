import pathlib
import pyparsing as pp
from functools import partial
from typing import Callable, Dict
import re

PATH = pathlib.Path(__file__).parent.absolute()


def create_parser():
    def choice(rng, rule):
        if isinstance(rule, str):
            return rule
        else:
            return rule.choice(rng)

    class Or:
        def __init__(self, tokens):
            self.tokens = tokens

        def __str__(self):
            if len(self.tokens) > 1:
                return "Or(" + "|".join(map(str, self.tokens)) + ")"
            else:
                return str(self.tokens[0])

        def __repr__(self):
            return str(self)

        def choice(self, rng):
            return choice(rng, rng.choice(self.tokens))

    class Rule:
        def __init__(self, tokens):
            self.rule = tokens[1]

        def __str__(self):
            return "Rule(" + self.rule + ")"

        def __repr__(self):
            return str(self)

        def choice(self, rng):
            return choice(rng, RULES[self.rule])

    class Add:
        def __init__(self, tokens):
            self.tokens = tokens

        def __str__(self):
            if len(self.tokens) > 1:
                return "Add(" + "+".join(map(str, self.tokens)) + ")"
            else:
                return str(self.tokens[0])

        def __repr__(self):
            return str(self)

        def choice(self, rng):
            return "".join(map(partial(choice, rng), self.tokens))

    class Function:
        def __init__(self, tokens):
            self.fn_name, self.argument = tokens
            if not self.fn_name:
                self.fn = str
            elif self.fn_name in FUNCTIONS:
                self.fn = FUNCTIONS[self.fn_name]
            else:
                raise KeyError("Unbekannte Funktion:", self.fn_name)

        def __str__(self):
            return f"{self.fn_name}({self.argument})"

        def __repr__(self):
            return str(self)

        def choice(self, rng):
            return self.fn(self.argument.choice(rng))

    def keyword(chars):
        return pp.Suppress(pp.Word(chars, exact=1))

    Direct = pp.Regex(r"[\w']+")("Direct") + ~pp.Literal("=")
    OrRule = pp.Forward()
    Quoted = pp.QuotedString('"') | pp.QuotedString("'")
    Function = (pp.Optional(pp.Word(pp.alphanums)) + 
        keyword("(") + OrRule + keyword(")")).addParseAction(Function)
    RuleAtom = (pp.Literal("$") + pp.Word(pp.alphanums)).addParseAction(Rule)
    Atom = (RuleAtom | Quoted | Function | Direct)("Atom")
    Plus = Atom[1, ...]("Plus").addParseAction(Add)
    OrDelim = keyword("|,")
    OrRule <<= (Plus + pp.ZeroOrMore(OrDelim + Plus) + pp.Optional(OrDelim)
              ).addParseAction(Or)
    _Rule = pp.Word(pp.alphanums) + keyword("=") + OrRule
    return pp.ZeroOrMore(_Rule + pp.Suppress(pp.Literal(";")[0, 1]))


Rules = create_parser()
del create_parser


class _DictWithDiagnostics(dict):
    def __missing__(self, key):
        raise KeyError(f"Unbekannte Regel: {key}")


def remove_apostrophe(arg: str) -> str:
    """Remove apostrophes like in an'kan, keeping ones like in "jen'a"."""
    return re.sub("'(?![aeiouyäöüáéíóú]", "", arg,
                  flags=re.RegexFlag.IGNORECASE)

def remove_dot(arg: str) -> str:
    """Remove apostrophes like in an'kan, keeping ones like in "jen'a"."""
    return re.sub(r"\.(?!\S)", "", arg,
                  flags=re.RegexFlag.IGNORECASE)


RULES = _DictWithDiagnostics()
FUNCTIONS: Dict[str, Callable[[str], str]] = {
    "cap": str.capitalize,
    "upper": str.upper,
    "lower": str.lower,
    "apo": remove_apostrophe,
    "dot": remove_dot,
    "nodot": lambda s: s.replace(".", ""),
}
try:
    with open(PATH / "namen.txt") as file:
        parsed_rules = iter(Rules.parseFile(file, True))
        for rule_name, rule_fn in zip(parsed_rules, parsed_rules):
            RULES[rule_name] = rule_fn
except pp.ParseException as err:
    print(err.line)
    print(" " * (err.column - 1) + "^")
    print(err)
    raise



def zufälliger_name(regel: str="FName", rng=None) -> str:
    if rng is None:
        rng = random.Random()
    return RULES[regel].choice(rng)


if __name__ == '__main__':
    from pprint import pprint
    import random
    pprint(RULES)
    rng_ = random.Random()
    for i in range(10):
        print(RULES["Name"].choice(rng_))
