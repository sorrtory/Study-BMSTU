from enum import Enum, auto
import os
from typing import Dict, List, Optional, Set, Tuple, Union

from predictive_parser import (
    ParseNode,
    ParserError,
    PredictiveParser as BasePredictiveParser,
    Token,
)


# Ошибки лексера
class LexerError(Exception):
    pass


# Типы токенов входного языка генератора
class TokenType(Enum):
    AXIOM = auto()
    IS = auto()
    OR = auto()
    END = auto()
    EPSILON = auto()
    NONTERM = auto()
    TERM = auto()
    EOF = auto()


KEYWORDS = {
    "`axiom": TokenType.AXIOM,
    "`is": TokenType.IS,
    "`or": TokenType.OR,
    "`end": TokenType.END,
    "`epsilon": TokenType.EPSILON,
}

class Lexer:
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

    def skip_whitespace_and_comments(self) -> None:
        while True:
            ch = self.current_char()

            while ch is not None and ch.isspace():
                self.advance()
                ch = self.current_char()

            # Комментарии начинаются с '$'
            if ch == "$":
                while self.current_char() is not None and self.current_char() != "\n":
                    self.advance()
                continue

            break

    def read_nonterm(self) -> Token[TokenType]:
        start_line = self.line
        start_col = self.column
        chars: List[str] = []

        ch = self.current_char()
        if ch is None or not ch.isalpha():
            raise LexerError(f"Expected NONTERM at {start_line}:{start_col}")

        while self.current_char() is not None and self.current_char().isalnum():
            chars.append(self.current_char())
            self.advance()

        return Token(TokenType.NONTERM, "".join(chars), start_line, start_col)

    def read_keyword(self) -> Token[TokenType]:
        start_line = self.line
        start_col = self.column

        if self.current_char() != "`":
            raise LexerError(f"Expected keyword at {start_line}:{start_col}")

        chars = ["`"]
        self.advance()

        if self.current_char() is None or not self.current_char().isalpha():
            raise LexerError(f"Invalid keyword at {start_line}:{start_col}")

        while self.current_char() is not None and self.current_char().isalpha():
            chars.append(self.current_char())
            self.advance()

        value = "".join(chars)
        token_type = KEYWORDS.get(value)
        if token_type is None:
            raise LexerError(f"Unknown keyword {value!r} at {start_line}:{start_col}")

        return Token(token_type, value, start_line, start_col)

    def read_term(self) -> Token[TokenType]:
        start_line = self.line
        start_col = self.column

        if self.current_char() != '"':
            raise LexerError(f"Expected '\"' at {start_line}:{start_col}")

        self.advance()
        chars: List[str] = []

        while True:
            ch = self.current_char()
            if ch is None:
                raise LexerError(f"Unterminated TERM at {start_line}:{start_col}")
            if ch == "\n":
                raise LexerError(f"Newline inside TERM at {self.line}:{self.column}")
            if ch == '"':
                self.advance()
                break
            chars.append(ch)
            self.advance()

        return Token(TokenType.TERM, "".join(chars), start_line, start_col)

    def next_token(self) -> Token[TokenType]:
        self.skip_whitespace_and_comments()

        ch = self.current_char()
        if ch is None:
            return Token(TokenType.EOF, "", self.line, self.column)

        if ch == "`":
            return self.read_keyword()
        if ch == '"':
            return self.read_term()
        if ch.isalpha():
            return self.read_nonterm()

        raise LexerError(f"Unexpected character {ch!r} at {self.line}:{self.column}")

Symbol = Union[str, TokenType]


# Нетерминалы грамматики входного языка генератора
START = "Start"
GRAMMAR = "Grammar"
GRAMMAR_TAIL = "GrammarTail"
RULE = "Rule"
NTERM_RULE = "NtermRule"
AXIOM_RULE = "AxiomRule"
EXPR = "Expr"
EXPR_TAIL = "ExprTail"
ALTERNATIVE = "Alternative"
SYMBOL_LIST = "SymbolList"
SYMBOL_LIST_TAIL = "SymbolListTail"
SYMBOL_NT = "Symbol"

INPUT_NONTERMINALS: Set[str] = {
    START,
    GRAMMAR,
    GRAMMAR_TAIL,
    RULE,
    NTERM_RULE,
    AXIOM_RULE,
    EXPR,
    EXPR_TAIL,
    ALTERNATIVE,
    SYMBOL_LIST,
    SYMBOL_LIST_TAIL,
    SYMBOL_NT,
}

EPSILON_SYMBOL = "ε"


def token_name(t: TokenType) -> str:
    return t.name


def terminal_node_label(token: Token[TokenType]) -> str:
    if token.type == TokenType.NONTERM:
        return f'NONTERM("{token.value}")'
    if token.type == TokenType.TERM:
        return f'TERM("{token.value}")'
    if token.type == TokenType.EOF:
        return "EOF"
    return str(token.value)


class PredictiveParser(BasePredictiveParser[TokenType]):
    def __init__(
        self,
        lexer: Lexer,
        table: Optional[Dict[Tuple[str, TokenType], List[Symbol]]] = None,
        start_symbol: str = START,
        nonterminals: Optional[Set[str]] = None,
    ):
        super().__init__(
            lexer=lexer,
            table=table if table is not None else build_manual_table(),
            start_symbol=start_symbol,
            nonterminals=nonterminals if nonterminals is not None else INPUT_NONTERMINALS,
            epsilon_symbol=EPSILON_SYMBOL,
            eof_token_type=TokenType.EOF,
            terminal_node_label=terminal_node_label,
            token_type_name=token_name,
        )


def build_manual_table() -> Dict[Tuple[str, TokenType], List[Symbol]]:
    table: Dict[Tuple[str, TokenType], List[Symbol]] = {}
    T = TokenType

    # Start ::= Grammar EOF
    for lookahead in (T.AXIOM, T.NONTERM):
        table[(START, lookahead)] = [GRAMMAR, T.EOF]

    # Grammar ::= Rule GrammarTail
    for lookahead in (T.AXIOM, T.NONTERM):
        table[(GRAMMAR, lookahead)] = [RULE, GRAMMAR_TAIL]

    # GrammarTail ::= Rule GrammarTail | ε
    for lookahead in (T.AXIOM, T.NONTERM):
        table[(GRAMMAR_TAIL, lookahead)] = [RULE, GRAMMAR_TAIL]
    table[(GRAMMAR_TAIL, T.EOF)] = [EPSILON_SYMBOL]

    # Rule ::= NtermRule | AxiomRule
    table[(RULE, T.NONTERM)] = [NTERM_RULE]
    table[(RULE, T.AXIOM)] = [AXIOM_RULE]

    # NtermRule ::= NONTERM IS Expr END
    table[(NTERM_RULE, T.NONTERM)] = [T.NONTERM, T.IS, EXPR, T.END]

    # AxiomRule ::= AXIOM NONTERM IS Expr END
    table[(AXIOM_RULE, T.AXIOM)] = [T.AXIOM, T.NONTERM, T.IS, EXPR, T.END]

    # Expr ::= Alternative ExprTail
    for lookahead in (T.EPSILON, T.NONTERM, T.TERM):
        table[(EXPR, lookahead)] = [ALTERNATIVE, EXPR_TAIL]

    # ExprTail ::= OR Alternative ExprTail | ε
    table[(EXPR_TAIL, T.OR)] = [T.OR, ALTERNATIVE, EXPR_TAIL]
    table[(EXPR_TAIL, T.END)] = [EPSILON_SYMBOL]

    # Alternative ::= EPSILON | SymbolList
    table[(ALTERNATIVE, T.EPSILON)] = [T.EPSILON]
    table[(ALTERNATIVE, T.NONTERM)] = [SYMBOL_LIST]
    table[(ALTERNATIVE, T.TERM)] = [SYMBOL_LIST]

    # SymbolList ::= Symbol SymbolListTail
    for lookahead in (T.NONTERM, T.TERM):
        table[(SYMBOL_LIST, lookahead)] = [SYMBOL_NT, SYMBOL_LIST_TAIL]

    # SymbolListTail ::= Symbol SymbolListTail | ε
    for lookahead in (T.NONTERM, T.TERM):
        table[(SYMBOL_LIST_TAIL, lookahead)] = [SYMBOL_NT, SYMBOL_LIST_TAIL]
    for lookahead in (T.OR, T.END):
        table[(SYMBOL_LIST_TAIL, lookahead)] = [EPSILON_SYMBOL]

    # Symbol ::= NONTERM | TERM
    table[(SYMBOL_NT, T.NONTERM)] = [T.NONTERM]
    table[(SYMBOL_NT, T.TERM)] = [T.TERM]

    return table


class DotExporter:
    def __init__(self):
        self.lines: List[str] = []
        self.counter = 0

    def next_id(self) -> str:
        self.counter += 1
        return f"n{self.counter}"

    @staticmethod
    def escape_label(label: str) -> str:
        return label.replace("\\", "\\\\").replace('"', '\\"')

    def emit_node_recursive(self, node: ParseNode) -> str:
        node_id = self.next_id()
        self.lines.append(f'  {node_id} [label="{self.escape_label(node.label)}"];')

        child_ids: List[str] = []
        for child in node.children:
            child_id = self.emit_node_recursive(child)
            child_ids.append(child_id)
            self.lines.append(f"  {node_id} -> {child_id};")

        # Невидимые связи для сохранения порядка потомков
        if len(child_ids) >= 2:
            chain = " -> ".join(child_ids)
            self.lines.append(f"  {{ rank=same; {chain} [style=invis]; }}")

        return node_id

    def export(self, root: ParseNode, filename: str) -> None:
        self.lines = []
        self.counter = 0
        self.lines.append("digraph ParseTree {")
        self.lines.append("  rankdir=TB;")
        self.lines.append("  node [shape=box];")
        self.lines.append("  edge [arrowhead=normal];")
        self.emit_node_recursive(root)
        self.lines.append("}")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines))


def parse_grammar_text(text: str, table: Optional[Dict[Tuple[str, TokenType], List[Symbol]]] = None) -> ParseNode:
    lexer = Lexer(text)
    parser = PredictiveParser(lexer, table=table)
    return parser.parse()


def parse_grammar_file(filename: str, table: Optional[Dict[Tuple[str, TokenType], List[Symbol]]] = None) -> ParseNode:
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_grammar_text(text, table=table)


# Минимальный запуск как в лабораторной 2.3: 
# построить DOT-дерево для input.txt
def main() -> int:
    input_filename = "input.txt"
    output_filename = "output.dot"

    if not os.path.exists(input_filename):
        input_filename = __file__.replace("grammar_parser.py", "input.txt")
        output_filename = __file__.replace("grammar_parser.py", "output.dot")
        if not os.path.exists(input_filename):
            print(f"Error: {input_filename} not found")
            return 1

    try:
        tree = parse_grammar_file(input_filename)
        exporter = DotExporter()
        exporter.export(tree, output_filename)
        print(f"Parse successful. DOT written to {output_filename}")
    except (LexerError, ParserError) as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
