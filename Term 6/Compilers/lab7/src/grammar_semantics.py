from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from grammar_parser import TokenType
from predictive_parser import ParseNode, Token


class GrammarError(Exception):
    pass


@dataclass
class GrammarSymbol:
    name: str
    is_terminal: bool
    line: int
    column: int

    def __str__(self) -> str:
        if self.is_terminal:
            return f'"{self.name}"'
        return self.name


@dataclass
class Production:
    left: str
    right: List[GrammarSymbol]
    line: int
    column: int

    def right_as_tuple(self) -> Tuple[Tuple[str, bool], ...]:
        return tuple((symbol.name, symbol.is_terminal) for symbol in self.right)

    def right_as_text(self) -> str:
        if not self.right:
            return "ε"
        return " ".join(str(symbol) for symbol in self.right)


@dataclass
class GrammarSpec:
    axiom: str
    productions: Dict[str, List[Production]] = field(default_factory=dict)
    nonterminals: Set[str] = field(default_factory=set)
    terminals: Set[str] = field(default_factory=set)


@dataclass
class RawRule:
    left: str
    alternatives: List[Production]
    is_axiom: bool
    line: int
    column: int


class GrammarTreeBuilder:
    def __init__(self, root: ParseNode):
        self.root = root
        self.rules: List[RawRule] = []

    @staticmethod
    def node_token(node: ParseNode) -> Token:
        if node.token is None:
            raise GrammarError(f"Internal error: node {node.label!r} has no token")
        return node.token

    def build(self) -> GrammarSpec:
        if self.root.label != "Start":
            raise GrammarError("Internal error: root is not Start")

        grammar_node = self.root.children[0]
        self.read_grammar(grammar_node)

        axiom_rules = [rule for rule in self.rules if rule.is_axiom]
        if not axiom_rules:
            raise GrammarError("No axiom in grammar at 1:1")
        if len(axiom_rules) > 1:
            rule = axiom_rules[1]
            raise GrammarError(f"More than one axiom in grammar at {rule.line}:{rule.column}")

        productions: Dict[str, List[Production]] = {}
        nonterminals: Set[str] = set()
        terminals: Set[str] = set()

        for rule in self.rules:
            nonterminals.add(rule.left)
            productions.setdefault(rule.left, [])
            productions[rule.left].extend(rule.alternatives)

        for left_productions in productions.values():
            for production in left_productions:
                for symbol in production.right:
                    if symbol.is_terminal:
                        terminals.add(symbol.name)
                    else:
                        if symbol.name not in nonterminals:
                            raise GrammarError(
                                f"Undefined nonterminal {symbol.name!r} at {symbol.line}:{symbol.column}"
                            )

        return GrammarSpec(
            axiom=axiom_rules[0].left,
            productions=productions,
            nonterminals=nonterminals,
            terminals=terminals,
        )

    def read_grammar(self, node: ParseNode) -> None:
        # Grammar ::= Rule GrammarTail
        rule = self.read_rule(node.children[0])
        self.rules.append(rule)
        self.read_grammar_tail(node.children[1])

    def read_grammar_tail(self, node: ParseNode) -> None:
        # GrammarTail ::= Rule GrammarTail | ε
        if len(node.children) == 1 and node.children[0].label == "ε":
            return
        rule = self.read_rule(node.children[0])
        self.rules.append(rule)
        self.read_grammar_tail(node.children[1])

    def read_rule(self, node: ParseNode) -> RawRule:
        # Rule ::= NtermRule | AxiomRule
        child = node.children[0]
        if child.label == "NtermRule":
            return self.read_nterm_rule(child)
        if child.label == "AxiomRule":
            return self.read_axiom_rule(child)
        raise GrammarError(f"Internal error: unexpected rule child {child.label!r}")

    def read_nterm_rule(self, node: ParseNode) -> RawRule:
        # NtermRule ::= NONTERM IS Expr END
        left_token = self.node_token(node.children[0])
        alternatives = self.read_expr(node.children[2], left_token.value, left_token.line, left_token.column)
        return RawRule(
            left=left_token.value,
            alternatives=alternatives,
            is_axiom=False,
            line=left_token.line,
            column=left_token.column,
        )

    def read_axiom_rule(self, node: ParseNode) -> RawRule:
        # AxiomRule ::= AXIOM NONTERM IS Expr END
        axiom_token = self.node_token(node.children[0])
        left_token = self.node_token(node.children[1])
        alternatives = self.read_expr(node.children[3], left_token.value, left_token.line, left_token.column)
        return RawRule(
            left=left_token.value,
            alternatives=alternatives,
            is_axiom=True,
            line=axiom_token.line,
            column=axiom_token.column,
        )

    def read_expr(self, node: ParseNode, left: str, line: int, column: int) -> List[Production]:
        # Expr ::= Alternative ExprTail
        alternatives = [self.read_alternative(node.children[0], left, line, column)]
        alternatives.extend(self.read_expr_tail(node.children[1], left, line, column))
        return alternatives

    def read_expr_tail(self, node: ParseNode, left: str, line: int, column: int) -> List[Production]:
        # ExprTail ::= OR Alternative ExprTail | ε
        if len(node.children) == 1 and node.children[0].label == "ε":
            return []
        alternatives = [self.read_alternative(node.children[1], left, line, column)]
        alternatives.extend(self.read_expr_tail(node.children[2], left, line, column))
        return alternatives

    def read_alternative(self, node: ParseNode, left: str, line: int, column: int) -> Production:
        # Alternative ::= EPSILON | SymbolList
        child = node.children[0]
        if child.token is not None and child.token.type == TokenType.EPSILON:
            return Production(left=left, right=[], line=child.token.line, column=child.token.column)
        return Production(
            left=left,
            right=self.read_symbol_list(child),
            line=line,
            column=column,
        )

    def read_symbol_list(self, node: ParseNode) -> List[GrammarSymbol]:
        # SymbolList ::= Symbol SymbolListTail
        symbols = [self.read_symbol(node.children[0])]
        symbols.extend(self.read_symbol_list_tail(node.children[1]))
        return symbols

    def read_symbol_list_tail(self, node: ParseNode) -> List[GrammarSymbol]:
        # SymbolListTail ::= Symbol SymbolListTail | ε
        if len(node.children) == 1 and node.children[0].label == "ε":
            return []
        symbols = [self.read_symbol(node.children[0])]
        symbols.extend(self.read_symbol_list_tail(node.children[1]))
        return symbols

    def read_symbol(self, node: ParseNode) -> GrammarSymbol:
        # Symbol ::= NONTERM | TERM
        token = self.node_token(node.children[0])
        if token.type == TokenType.NONTERM:
            return GrammarSymbol(token.value, False, token.line, token.column)
        if token.type == TokenType.TERM:
            return GrammarSymbol(token.value, True, token.line, token.column)
        raise GrammarError(f"Internal error: unexpected symbol token {token.type}")


def build_grammar_spec(root: ParseNode) -> GrammarSpec:
    return GrammarTreeBuilder(root).build()
