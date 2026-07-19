% Лабораторная работа № 3.1 «Самоприменимый генератор компиляторов
  на основе предсказывающего анализа»
% 3 июня 2026 г.
% Александр Федуков, ИУ9-62Б

# Цель работы
Целью данной работы является изучение алгоритма построения таблиц предсказывающего анализатора.

# Индивидуальный вариант

```text
$ ключевые слова
$ начинаются с обратной кавычки

F  `is "n" `or "(" E ")" `end
T  `is F T1 `end
T1 `is "*" F T1 `or `epsilon `end
`axiom E  `is T E1 `end
E1 `is "+" T E1 `or `epsilon `end
```

# Грамматика на входном языке

```text
`axiom Start `is Grammar "EOF" `end
Grammar `is Rule GrammarTail `end
GrammarTail `is Rule GrammarTail `or `epsilon `end
Rule `is NtermRule `or AxiomRule `end
NtermRule `is "NONTERM" "IS" Expr "END" `end
AxiomRule `is "AXIOM" "NONTERM" "IS" Expr "END" `end
Expr `is Alternative ExprTail `end
ExprTail `is "OR" Alternative ExprTail `or `epsilon `end
Alternative `is "EPSILON" `or SymbolList `end
SymbolList `is Symbol SymbolListTail `end
SymbolListTail `is Symbol SymbolListTail `or `epsilon `end
Symbol `is "NONTERM" `or "TERM" `end
```

# Реализация

## Генератор компиляторов

### generator.py

```python
import argparse
import importlib.util
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from grammar_parser import (
    INPUT_NONTERMINALS,
    LexerError,
    ParserError,
    PredictiveParser,
    TokenType,
    Lexer,
)
from grammar_semantics import GrammarError, build_grammar_spec
from table_builder import build_all, format_sets
from table_emitter import emit_python_table

TableType = Dict[Tuple[str, TokenType], List[Any]]


def load_table_from_file(filename: str) -> TableType:
    module_name = os.path.splitext(os.path.basename(filename))[0]
    spec = importlib.util.spec_from_file_location(module_name, filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load table from {filename}")    

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    table = getattr(module, "PARSE_TABLE", None)
    if table is None:
        raise RuntimeError(f"File {filename} does not contain PARSE_TABLE")
    return table


def parse_input_grammar(filename: str, bootstrap_table: Optional[TableType]):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    lexer = Lexer(text)
    parser = PredictiveParser(
        lexer,
        table=bootstrap_table,
        start_symbol="Start",
        nonterminals=INPUT_NONTERMINALS,
    )
    return parser.parse()


def generate_table(
    input_filename: str,
    output_filename: str,
    terminal_mode: str,
    bootstrap_table_filename: Optional[str] = None,
    print_sets: bool = False,
) -> None:
    bootstrap_table = None
    if bootstrap_table_filename is not None:
        bootstrap_table = load_table_from_file(bootstrap_table_filename)

    tree = parse_input_grammar(input_filename, bootstrap_table)
    grammar = build_grammar_spec(tree)
    first, follow, parse_table = build_all(grammar)

    emit_python_table(parse_table, output_filename, terminal_mode)

    if print_sets:
        print(format_sets("FIRST", first))
        print(format_sets("FOLLOW", follow))

    print(f"Axiom: {grammar.axiom}")
    print(f"Nonterminals: {len(grammar.nonterminals)}")
    print(f"Terminals: {len(grammar.terminals) + 1} including EOF")
    print(f"Table cells: {len(parse_table)}")
    print(f"Generated table written to {output_filename}")


def main() -> int:
    arg_parser = argparse.ArgumentParser(
        description="LL(1) parse-table generator for the grammar language from lab 3.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    arg_parser.add_argument(
        "input",
        nargs="?",
        default="generator_grammar.txt",
        help="grammar description file",
    )
    arg_parser.add_argument(
        "output",
        nargs="?",
        default="generated/generated_input_table.py",
        help="output Python source file with PARSE_TABLE",
    )
    arg_parser.add_argument(
        "--mode",
        choices=("enum", "string"),
        default="enum",
        help="how to emit terminal symbols: TokenType.NAME or plain strings",
    )
    arg_parser.add_argument(
        "--bootstrap-table",
        default=None,
        help="Python file with PARSE_TABLE to parse the input grammar; if omitted, manual table is used",
    )
    arg_parser.add_argument(
        "--sets",
        action="store_true",
        help="print FIRST and FOLLOW sets",
    )

    args = arg_parser.parse_args()

    try:
        generate_table(
            args.input,
            args.output,
            args.mode,
            bootstrap_table_filename=args.bootstrap_table,
            print_sets=args.sets,
        )
    except (LexerError, ParserError, GrammarError, RuntimeError) as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### table_builder.py

```python
from typing import Dict, List, Optional, Set, Tuple

from grammar_semantics import GrammarError, GrammarSpec, GrammarSymbol, Production


EPSILON_SYMBOL = "ε"
END_MARKER = "EOF"


ParseTable = Dict[Tuple[str, str], Production]


def first_of_sequence(
    symbols: List[GrammarSymbol],
    first: Dict[str, Set[str]],
) -> Set[str]:
    if not symbols:
        return {EPSILON_SYMBOL}

    result: Set[str] = set()

    for symbol in symbols:
        if symbol.is_terminal:
            result.add(symbol.name)
            return result

        symbol_first = first[symbol.name]
        result.update(symbol_first - {EPSILON_SYMBOL})

        if EPSILON_SYMBOL not in symbol_first:
            return result

    result.add(EPSILON_SYMBOL)
    return result


def build_first(spec: GrammarSpec) -> Dict[str, Set[str]]:
    first: Dict[str, Set[str]] = {nonterm: set() for nonterm in spec.nonterminals}
    changed = True

    while changed:
        changed = False

        for left, productions in spec.productions.items():
            for production in productions:
                before = len(first[left])
                first[left].update(first_of_sequence(production.right, first))
                if len(first[left]) != before:
                    changed = True

    return first


def build_follow(spec: GrammarSpec, first: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    follow: Dict[str, Set[str]] = {nonterm: set() for nonterm in spec.nonterminals}
    follow[spec.axiom].add(END_MARKER)

    changed = True
    while changed:
        changed = False

        for left, productions in spec.productions.items():
            for production in productions:
                symbols = production.right

                for i, symbol in enumerate(symbols):
                    if symbol.is_terminal:
                        continue

                    tail = symbols[i + 1:]
                    tail_first = first_of_sequence(tail, first)

                    before = len(follow[symbol.name])
                    follow[symbol.name].update(tail_first - {EPSILON_SYMBOL})

                    if EPSILON_SYMBOL in tail_first:
                        follow[symbol.name].update(follow[left])

                    if len(follow[symbol.name]) != before:
                        changed = True

    return follow


def build_parse_table(
    spec: GrammarSpec,
    first: Dict[str, Set[str]],
    follow: Dict[str, Set[str]],
) -> ParseTable:
    table: ParseTable = {}

    for left, productions in spec.productions.items():
        for production in productions:
            production_first = first_of_sequence(production.right, first)

            for terminal in sorted(production_first - {EPSILON_SYMBOL}):
                put_table_cell(table, left, terminal, production)

            if EPSILON_SYMBOL in production_first:
                for terminal in sorted(follow[left]):
                    put_table_cell(table, left, terminal, production)

    return table


def put_table_cell(table: ParseTable, left: str, terminal: str, production: Production) -> None:
    key = (left, terminal)
    old_production = table.get(key)

    if old_production is not None:
        if old_production.right_as_tuple() == production.right_as_tuple():
            return

        raise GrammarError(
            "Grammar is not LL(1): conflict for "
            f"{left!r} with lookahead {terminal!r} at {production.line}:{production.column}; "
            f"old production is {left} -> {old_production.right_as_text()}, "
            f"new production is {left} -> {production.right_as_text()}"
        )

    table[key] = production


def build_all(spec: GrammarSpec) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]], ParseTable]:
    first = build_first(spec)
    follow = build_follow(spec, first)
    table = build_parse_table(spec, first, follow)
    return first, follow, table


def format_sets(title: str, sets: Dict[str, Set[str]]) -> str:
    lines = [title]
    for name in sorted(sets):
        body = ", ".join(sorted(sets[name]))
        lines.append(f"  {name}: {{ {body} }}")
    return "\n".join(lines)

```

### table_emitter.py

```python
from typing import Dict, List, Tuple

from grammar_parser import TokenType
from grammar_semantics import GrammarError, GrammarSymbol, Production
from table_builder import EPSILON_SYMBOL, ParseTable


def emit_python_table(
    table: ParseTable,
    output_filename: str,
    terminal_mode: str,
    table_name: str = "PARSE_TABLE",
) -> None:
    if terminal_mode not in ("enum", "string"):
        raise ValueError("terminal_mode must be 'enum' or 'string'")

    lines: List[str] = []
    lines.append("# This file was generated by generator.py")
    lines.append("# Do not edit it by hand.")
    lines.append("")

    if terminal_mode == "enum":
        lines.append("from grammar_parser import TokenType, EPSILON_SYMBOL")
        lines.append("")
    else:
        lines.append(f"EPSILON_SYMBOL = {EPSILON_SYMBOL!r}")
        lines.append("")

    lines.append(f"{table_name} = {{")

    for key in sorted(table.keys(), key=lambda item: (item[0], item[1])):
        left, lookahead = key
        production = table[key]
        rendered_key = render_key(left, lookahead, terminal_mode)
        rendered_right = render_right(production.right, terminal_mode)
        lines.append(f"    {rendered_key}: {rendered_right},")

    lines.append("}")
    lines.append("")

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def render_key(left: str, lookahead: str, terminal_mode: str) -> str:
    return f"({left!r}, {render_terminal(lookahead, terminal_mode)})"


def render_right(symbols: List[GrammarSymbol], terminal_mode: str) -> str:
    if not symbols:
        return "[EPSILON_SYMBOL]"

    rendered_symbols = [render_symbol(symbol, terminal_mode) for symbol in symbols]
    return "[" + ", ".join(rendered_symbols) + "]"


def render_symbol(symbol: GrammarSymbol, terminal_mode: str) -> str:
    if symbol.is_terminal:
        return render_terminal(symbol.name, terminal_mode)
    return repr(symbol.name)


def render_terminal(name: str, terminal_mode: str) -> str:
    if terminal_mode == "string":
        return repr(name)

    if not hasattr(TokenType, name):
        raise GrammarError(
            f"Terminal {name!r} cannot be emitted as TokenType.{name}; "
            "use --mode string or rename the terminal"
        )
    return f"TokenType.{name}"
```

### grammar_parser.py

```python
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


def parse_grammar_text(
    text: str,
    table: Optional[Dict[Tuple[str, TokenType], List[Symbol]]] = None,
) -> ParseNode:
    lexer = Lexer(text)
    parser = PredictiveParser(lexer, table=table)
    return parser.parse()


def parse_grammar_file(
    filename: str,
    table: Optional[Dict[Tuple[str, TokenType], List[Symbol]]] = None,
) -> ParseNode:
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
```

### grammar_semantics.py

```python
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
```

### predictive_parser.py

```python
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Protocol, Set, Tuple, TypeVar, Union


class ParserError(Exception):
    pass


TokenType = TypeVar("TokenType")


@dataclass
class Token(Generic[TokenType]):
    type: TokenType
    value: Any
    line: int
    column: int


@dataclass
class ParseNode(Generic[TokenType]):
    label: str
    children: List["ParseNode[TokenType]"] = field(default_factory=list)
    token: Token[TokenType] | None = None


class Lexer(Protocol[TokenType]):
    def next_token(self) -> Token[TokenType]:
        ...


Symbol = Union[str, TokenType]
ParseTable = Dict[Tuple[str, TokenType], List[Symbol[TokenType]]]


class PredictiveParser(Generic[TokenType]):
    def __init__(
        self,
        lexer: Lexer[TokenType],
        table: ParseTable[TokenType],
        start_symbol: str,
        nonterminals: Set[str],
        epsilon_symbol: str,
        eof_token_type: TokenType,
        terminal_node_label: Callable[[Token[TokenType]], str] | None = None,
        token_type_name: Callable[[TokenType], str] = str,
    ):
        self.lexer = lexer
        self.current = self.lexer.next_token()
        self.table = table
        self.start_symbol = start_symbol
        self.nonterminals = nonterminals
        self.epsilon_symbol = epsilon_symbol
        self.eof_token_type = eof_token_type
        self.terminal_node_label = terminal_node_label or self.default_terminal_node_label
        self.token_type_name = token_type_name

    def error(self, message: str) -> None:
        raise ParserError(f"{message} at {self.current.line}:{self.current.column}")

    def parse(self) -> ParseNode[TokenType]:
        root = ParseNode[TokenType](self.start_symbol)
        stack: List[Tuple[Symbol[TokenType], ParseNode[TokenType]]] = [
            (self.start_symbol, root)
        ]

        while stack:
            top_symbol, top_node = stack.pop()

            if top_symbol == self.epsilon_symbol:
                top_node.label = self.epsilon_symbol
                continue

            if isinstance(top_symbol, str) and top_symbol in self.nonterminals:
                production = self.table.get((top_symbol, self.current.type))
                if production is None:
                    self.error(
                        f"No rule for {top_symbol} with lookahead "
                        f"{self.token_type_name(self.current.type)}"
                    )

                children = [ParseNode[TokenType](self.symbol_label(symbol)) for symbol in production]
                top_node.children = children

                for symbol, child in reversed(list(zip(production, children))):
                    stack.append((symbol, child))
                continue

            if self.current.type != top_symbol:
                self.error(
                    f"Expected {self.token_type_name(top_symbol)}, "
                    f"got {self.token_type_name(self.current.type)}"
                )

            top_node.label = self.terminal_node_label(self.current)
            top_node.token = self.current
            self.current = self.lexer.next_token()

        if self.current.type != self.eof_token_type:
            self.error("Extra input after complete parse")

        return root

    def symbol_label(self, symbol: Symbol[TokenType]) -> str:
        if isinstance(symbol, str):
            return symbol
        return self.token_type_name(symbol)

    def default_terminal_node_label(self, token: Token[TokenType]) -> str:
        return self.token_type_name(token.type)
```


## Калькулятор

```python
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
```

# Тестирование

## Генератор компиляторов

Таблица для калькулятора

```python
# This file was generated by generator.py
# Do not edit it by hand.

EPSILON_SYMBOL = 'ε'

PARSE_TABLE = {
    ('E', '('): ['T', 'E1'],
    ('E', 'n'): ['T', 'E1'],
    ('E1', ')'): [EPSILON_SYMBOL],
    ('E1', '+'): ['+', 'T', 'E1'],
    ('E1', 'EOF'): [EPSILON_SYMBOL],
    ('F', '('): ['(', 'E', ')'],
    ('F', 'n'): ['n'],
    ('T', '('): ['F', 'T1'],
    ('T', 'n'): ['F', 'T1'],
    ('T1', ')'): [EPSILON_SYMBOL],
    ('T1', '*'): ['*', 'F', 'T1'],
    ('T1', '+'): [EPSILON_SYMBOL],
    ('T1', 'EOF'): [EPSILON_SYMBOL],
}
```

Таблица для собственной грамматики

```python
# This file was generated by generator.py
# Do not edit it by hand.

from grammar_parser import TokenType, EPSILON_SYMBOL

PARSE_TABLE = {
    ('Alternative', TokenType.EPSILON): [TokenType.EPSILON],
    ('Alternative', TokenType.NONTERM): ['SymbolList'],
    ('Alternative', TokenType.TERM): ['SymbolList'],
    ('AxiomRule', TokenType.AXIOM): [TokenType.AXIOM, TokenType.NONTERM, TokenType.IS, 'Expr', TokenType.END],
    ('Expr', TokenType.EPSILON): ['Alternative', 'ExprTail'],
    ('Expr', TokenType.NONTERM): ['Alternative', 'ExprTail'],
    ('Expr', TokenType.TERM): ['Alternative', 'ExprTail'],
    ('ExprTail', TokenType.END): [EPSILON_SYMBOL],
    ('ExprTail', TokenType.OR): [TokenType.OR, 'Alternative', 'ExprTail'],
    ('Grammar', TokenType.AXIOM): ['Rule', 'GrammarTail'],
    ('Grammar', TokenType.NONTERM): ['Rule', 'GrammarTail'],
    ('GrammarTail', TokenType.AXIOM): ['Rule', 'GrammarTail'],
    ('GrammarTail', TokenType.EOF): [EPSILON_SYMBOL],
    ('GrammarTail', TokenType.NONTERM): ['Rule', 'GrammarTail'],
    ('NtermRule', TokenType.NONTERM): [TokenType.NONTERM, TokenType.IS, 'Expr', TokenType.END],
    ('Rule', TokenType.AXIOM): ['AxiomRule'],
    ('Rule', TokenType.NONTERM): ['NtermRule'],
    ('Start', TokenType.AXIOM): ['Grammar', TokenType.EOF],
    ('Start', TokenType.NONTERM): ['Grammar', TokenType.EOF],
    ('Symbol', TokenType.NONTERM): [TokenType.NONTERM],
    ('Symbol', TokenType.TERM): [TokenType.TERM],
    ('SymbolList', TokenType.NONTERM): ['Symbol', 'SymbolListTail'],
    ('SymbolList', TokenType.TERM): ['Symbol', 'SymbolListTail'],
    ('SymbolListTail', TokenType.END): [EPSILON_SYMBOL],
    ('SymbolListTail', TokenType.NONTERM): ['Symbol', 'SymbolListTail'],
    ('SymbolListTail', TokenType.OR): [EPSILON_SYMBOL],
    ('SymbolListTail', TokenType.TERM): ['Symbol', 'SymbolListTail'],
}
```

## Калькулятор

Проверка вычисления выражений

```text
$ python3 -m calculator.calculator
expression> (2+3)*4
20
```

# Вывод
В ходе работы реализован генератор таблиц предсказывающего анализатора для
LL(1)-грамматик. Реализация строит множества FIRST и FOLLOW, формирует таблицу
разбора и выводит её в виде Python-модуля.

Проверена самоприменимость генератора: таблица для входного языка совпадает с
ручной таблицей. Дополнительно проверен отдельный калькулятор, использующий
сгенерированную таблицу разбора.
