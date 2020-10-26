import pathlib
import pyparsing as pp
from functools import partial

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
            return "Or(" + "|".join(map(str, self.tokens)) + ")"

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
            return "Add(" + "+".join(map(str, self.tokens)) + ")"

        def __repr__(self):
            return str(self)

        def choice(self, rng):
            return "".join(map(partial(choice, rng), self.tokens))
    Direct = pp.Regex(r"[\w']+")("Direct")
    Quoted = pp.QuotedString('"') | pp.QuotedString("'")
    RuleAtom = (pp.Literal("$") + pp.Word(pp.alphanums)).addParseAction(Rule)
    Atom = (RuleAtom | Quoted | Direct)("Atom")
    Plus = Atom[1, ...]("Plus").addParseAction(Add)
    OrRule = pp.delimitedList(Plus, "|").addParseAction(Or)
    _Rule = pp.Word(pp.alphanums) + pp.Suppress(pp.Literal("=")) + OrRule
    return pp.ZeroOrMore(_Rule + pp.Suppress(pp.Literal(";")[0, 1]))


Rules = create_parser()
del create_parser


class _DictWithDiagnostics(dict):
    def __missing__(self, key):
        raise KeyError(f"Unbekannte Regel: {key}")


with open(PATH / "namen.txt") as file:
    RULES = _DictWithDiagnostics()
    parsed_rules = iter(Rules.parseFile(file, True))
    for rule_name, rule in zip(parsed_rules, parsed_rules):
        RULES[rule_name] = rule


def zufälliger_name(regel: str="Frauenname", rng=None) -> str:
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
