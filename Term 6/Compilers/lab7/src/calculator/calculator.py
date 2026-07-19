from typing import List, Optional

from predictive_parser import ParseNode, ParserError, PredictiveParser, Token

try:
    from generated.calc_table import PARSE_TABLE, EPSILON_SYMBOL
except ImportError:
    print("Error: calc_table.py not found. Generate it first:")
    print(
        "  python3 generator.py calculator/arithmetic_grammar.txt "
        "generated/calc_table.py --mode string"
    )
    raise


class CalcLexerError(Exception):
    pass


class CalcLexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def advance(self) -> None:
        ch = self.current_char()
        if ch is None:
            return
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1

    def skip_whitespace(self) -> None:
        while self.current_char() is not None and self.current_char().isspace():
            self.advance()

    def read_number(self) -> Token[str]:
        start_line = self.line
        start_col = self.column
        chars: List[str] = []

        while self.current_char() is not None and self.current_char().isdigit():
            chars.append(self.current_char())
            self.advance()

        return Token("n", int("".join(chars)), start_line, start_col)

    def next_token(self) -> Token[str]:
        self.skip_whitespace()

        ch = self.current_char()
        if ch is None:
            return Token("EOF", "", self.line, self.column)

        if ch.isdigit():
            return self.read_number()

        if ch in "+*()":
            token = Token(ch, ch, self.line, self.column)
            self.advance()
            return token

        raise CalcLexerError(f"Unexpected character {ch!r} at {self.line}:{self.column}")

NONTERMINALS = {"E", "E1", "T", "T1", "F"}
START = "E"


def terminal_node_label(token: Token[str]) -> str:
    if token.type == "n":
        return f"n({token.value})"
    return token.type


class Calculator:
    def eval(self, node: ParseNode[str]) -> int:
        if node.label == "E":
            return self.eval_E(node)
        raise ParserError(f"Internal error: cannot evaluate node {node.label!r}")

    def eval_E(self, node: ParseNode[str]) -> int:
        # E ::= T E1
        return self.eval_T(node.children[0]) + self.eval_E1(node.children[1])

    def eval_E1(self, node: ParseNode[str]) -> int:
        # E1 ::= + T E1 | ε
        if self.is_epsilon_node(node):
            return 0
        return self.eval_T(node.children[1]) + self.eval_E1(node.children[2])

    def eval_T(self, node: ParseNode[str]) -> int:
        # T ::= F T1
        return self.eval_F(node.children[0]) * self.eval_T1(node.children[1])

    def eval_T1(self, node: ParseNode[str]) -> int:
        # T1 ::= * F T1 | ε
        if self.is_epsilon_node(node):
            return 1
        return self.eval_F(node.children[1]) * self.eval_T1(node.children[2])

    def eval_F(self, node: ParseNode[str]) -> int:
        # F ::= n | ( E )
        first_child = node.children[0]
        if first_child.token is not None and first_child.token.type == "n":
            return int(first_child.token.value)
        return self.eval_E(node.children[1])

    @staticmethod
    def is_epsilon_node(node: ParseNode[str]) -> bool:
        return len(node.children) == 1 and node.children[0].label == EPSILON_SYMBOL


def calculate(text: str) -> int:
    lexer = CalcLexer(text)
    parser = PredictiveParser(
        lexer=lexer,
        table=PARSE_TABLE,
        start_symbol=START,
        nonterminals=NONTERMINALS,
        epsilon_symbol=EPSILON_SYMBOL,
        eof_token_type="EOF",
        terminal_node_label=terminal_node_label,
    )
    tree = parser.parse()
    return Calculator().eval(tree)


def main() -> int:
    try:
        text = input("expression> ")
        result = calculate(text)
        print(result)
    except (CalcLexerError, ParserError) as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
