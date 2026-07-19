% Лабораторная работа № 2.3 «Синтаксический анализатор на основе предсказывающего анализа»
% 29 апреля 2026 г.
% Александр Федуков, ИУ9-62Б

# Цель работы

Целью данной работы является изучение алгоритма построения таблиц предсказывающего анализатора.

# Индивидуальный вариант

```
$ ключевые слова
$ начинаются с обратной кавычки
$ комментарии начинаются с $

F  `is "n" `or "(" E ")" `end
T  `is F T1 `end
T1 `is "*" F T1 `or `epsilon `end
`axiom E  `is T E1 `end
E1 `is "+" T E1 `or `epsilon `end
```

# Реализация

## Неформальное описание синтаксиса входного языка

```
Ключевые слова:
`axiom
`is
`or
`end
`epsilon

Комментарии начинаются с символа $
Правила задаются в виде:
NONTERM `is <Expr> `end
или
`axiom NONTERM `is <Expr> `end

Можно использовать `or для альтернатив
```

Каждое правило задаёт один нетерминал и список его альтернатив. Левая часть правила - имя нетерминала. Правая
часть начинается после ключевого слова `is и заканчивается ключевым словом `end. Альтернативы в правой части
разделяются ключевым словом \`or.

Терминальные символы записываются в двойных кавычках, например "n", "+", "(". Нетерминальные символы
записываются как идентификаторы, состоящие из букв и цифр и начинающиеся с буквы.

Пустая альтернатива задаётся ключевым словом \`epsilon. Комментарии начинаются с символа $ и продолжаются до
конца строки. Пробельные символы вне терминальных строк игнорируются.

## Лексическая структура

```
NONTERM = LETTER { LETTER | DIGIT }
TERM    = '"' { CHAR } '"'
LETTER  = 'A'..'Z' | 'a'..'z'
DIGIT   = '0'..'9'
CHAR    = любой символ, кроме " и конца строки
COMMENT = '$' { любой символ, кроме конца строки }

Дополнительно:
- ключевые слова начинаются с символа `
- пробельные символы вне TERM игнорируются лексическим анализатором
- после окончания входного текста формируется служебный токен EOF
- `epsilon` используется только как самостоятельная альтернатива = пустая цепочка.
```

## Грамматика языка

```
<Start>           ::= <Grammar> EOF
<Grammar>         ::= <Rule> <GrammarTail>
<GrammarTail>     ::= <Rule> <GrammarTail> | ε
<Rule>            ::= <NtermRule> | <AxiomRule>
<NtermRule>       ::= NONTERM "`is" <Expr> "`end"
<AxiomRule>       ::= "`axiom" NONTERM "`is" <Expr> "`end"
<Expr>            ::= <Alternative> <ExprTail>
<ExprTail>        ::= "`or" <Alternative> <ExprTail> | ε
<Alternative>     ::= "`epsilon" | <SymbolList>
<SymbolList>      ::= <Symbol> <SymbolListTail>
<SymbolListTail>  ::= <Symbol> <SymbolListTail> | ε
<Symbol>          ::= NONTERM | TERM
```

## Программная реализация

```python
from dataclasses import dataclass, field
from enum import Enum, auto
import os
from typing import List, Optional, Dict, Tuple, Union


# Ошибки лексера
class LexerError(Exception):
    pass


# Ошибки парсера
class ParserError(Exception):
    pass


# Типы токенов
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


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.type.name}({self.value!r}) at {self.line}:{self.column}"


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

    def read_nonterm(self) -> Token:
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

    def read_keyword(self) -> Token:
        start_line = self.line
        start_col = self.column

        if self.current_char() != "`":
            raise LexerError(f"Expected keyword at {start_line}:{start_col}")

        # read the keyword
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

    def read_term(self) -> Token:
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

    def next_token(self) -> Token:
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


@dataclass
class ParseNode:
    label: str
    children: List["ParseNode"] = field(default_factory=list)


Symbol = Union[str, TokenType]


# Нетерминалы
START = "<Start>"
GRAMMAR = "<Grammar>"
GRAMMAR_TAIL = "<GrammarTail>"
RULE = "<Rule>"
NTERM_RULE = "<NtermRule>"
AXIOM_RULE = "<AxiomRule>"
EXPR = "<Expr>"
EXPR_TAIL = "<ExprTail>"
ALTERNATIVE = "<Alternative>"
SYMBOL_LIST = "<SymbolList>"
SYMBOL_LIST_TAIL = "<SymbolListTail>"
SYMBOL_NT = "<Symbol>"

NONTERMINALS = {
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

EPS = "ε"


def is_nonterminal(symbol: Symbol) -> bool:
    return isinstance(symbol, str) and symbol in NONTERMINALS


def is_epsilon(symbol: Symbol) -> bool:
    return symbol == EPS


def token_name(t: TokenType) -> str:
    return t.name


class PredictiveParser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current = self.lexer.next_token()
        self.table: Dict[Tuple[str, TokenType], List[Symbol]] = {}
        self._build_table()

    def error(self, message: str) -> None:
        raise ParserError(f"{message} at {self.current.line}:{self.current.column}")

    def _build_table(self) -> None:
        T = TokenType

        # <Start> ::= <Grammar> EOF
        for lookahead in (T.AXIOM, T.NONTERM):
            self.table[(START, lookahead)] = [GRAMMAR, T.EOF]

        # <Grammar> ::= <Rule> <GrammarTail>
        for lookahead in (T.AXIOM, T.NONTERM):
            self.table[(GRAMMAR, lookahead)] = [RULE, GRAMMAR_TAIL]

        # <GrammarTail> ::= <Rule> <GrammarTail> | ε
        for lookahead in (T.AXIOM, T.NONTERM):
            self.table[(GRAMMAR_TAIL, lookahead)] = [RULE, GRAMMAR_TAIL]
        self.table[(GRAMMAR_TAIL, T.EOF)] = [EPS]

        # <Rule> ::= <NtermRule> | <AxiomRule>
        self.table[(RULE, T.NONTERM)] = [NTERM_RULE]
        self.table[(RULE, T.AXIOM)] = [AXIOM_RULE]

        # <NtermRule> ::= NONTERM `is <Expr> `end
        self.table[(NTERM_RULE, T.NONTERM)] = [T.NONTERM, T.IS, EXPR, T.END]

        # <AxiomRule> ::= `axiom NONTERM `is <Expr> `end
        self.table[(AXIOM_RULE, T.AXIOM)] = [T.AXIOM, T.NONTERM, T.IS, EXPR, T.END]

        # <Expr> ::= <Alternative> <ExprTail>
        for lookahead in (T.EPSILON, T.NONTERM, T.TERM):
            self.table[(EXPR, lookahead)] = [ALTERNATIVE, EXPR_TAIL]

        # <ExprTail> ::= `or <Alternative> <ExprTail> | ε
        self.table[(EXPR_TAIL, T.OR)] = [T.OR, ALTERNATIVE, EXPR_TAIL]
        self.table[(EXPR_TAIL, T.END)] = [EPS]

        # <Alternative> ::= `epsilon | <SymbolList>
        self.table[(ALTERNATIVE, T.EPSILON)] = [T.EPSILON]
        self.table[(ALTERNATIVE, T.NONTERM)] = [SYMBOL_LIST]
        self.table[(ALTERNATIVE, T.TERM)] = [SYMBOL_LIST]

        # <SymbolList> ::= <Symbol> <SymbolListTail>
        for lookahead in (T.NONTERM, T.TERM):
            self.table[(SYMBOL_LIST, lookahead)] = [SYMBOL_NT, SYMBOL_LIST_TAIL]

        # <SymbolListTail> ::= <Symbol> <SymbolListTail> | ε
        for lookahead in (T.NONTERM, T.TERM):
            self.table[(SYMBOL_LIST_TAIL, lookahead)] = [SYMBOL_NT, SYMBOL_LIST_TAIL]
        for lookahead in (T.OR, T.END):
            self.table[(SYMBOL_LIST_TAIL, lookahead)] = [EPS]

        # <Symbol> ::= NONTERM | TERM
        self.table[(SYMBOL_NT, T.NONTERM)] = [T.NONTERM]
        self.table[(SYMBOL_NT, T.TERM)] = [T.TERM]

    def _terminal_node_label(self, token: Token) -> str:
        if token.type == TokenType.NONTERM:
            return f'NONTERM("{token.value}")'
        if token.type == TokenType.TERM:
            return f'TERM("{token.value}")'
        if token.type == TokenType.EOF:
            return "EOF"
        return token.value

    def parse(self) -> ParseNode:
        root = ParseNode(START)
        stack: List[Tuple[Symbol, ParseNode]] = [(START, root)]

        while stack:
            top_symbol, top_node = stack.pop()

            if is_epsilon(top_symbol):
                top_node.label = EPS
                continue

            if isinstance(top_symbol, TokenType):
                if self.current.type != top_symbol:
                    self.error(
                        f"Expected {token_name(top_symbol)}, got {token_name(self.current.type)}"
                    )
                top_node.label = self._terminal_node_label(self.current)
                top_node.token = self.current
                self.current = self.lexer.next_token()
                continue

            if is_nonterminal(top_symbol):
                production = self.table.get((top_symbol, self.current.type))
                if production is None:
                    self.error(
                        f"No rule for {top_symbol} with lookahead {token_name(self.current.type)}"
                    )

                children = [ParseNode(self._symbol_to_label(sym)) for sym in production]
                top_node.children = children

                for sym, child in reversed(list(zip(production, children))):
                    stack.append((sym, child))
                continue

            raise ParserError(f"Internal parser error: unknown symbol {top_symbol!r}")

        if self.current.type != TokenType.EOF:
            self.error("Extra input after complete parse")

        return root

    @staticmethod
    def _symbol_to_label(symbol: Symbol) -> str:
        if symbol == EPS:
            return EPS
        if isinstance(symbol, TokenType):
            if symbol == TokenType.EOF:
                return "EOF"
            return symbol.name
        return symbol


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
        self.lines.append("digraph ParseTree {")
        self.lines.append("  rankdir=TB;")
        self.lines.append("  node [shape=box];")
        self.lines.append("  edge [arrowhead=normal];")
        self.emit_node_recursive(root)
        self.lines.append("}")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines))


def main() -> None:
    input_filename = "input.txt"
    output_filename = "output.dot"

    if not os.path.exists(input_filename):
        input_filename = __file__.replace("main.py", "input.txt")
        output_filename = __file__.replace("main.py", "output.dot")
        if not os.path.exists(input_filename):
            print(f"Error: {input_filename} not found")
            return

    with open(input_filename, "r", encoding="utf-8") as f:
        text = f.read()

    lexer = Lexer(text)
    parser = PredictiveParser(lexer)
    tree = parser.parse()

    exporter = DotExporter()
    exporter.export(tree, output_filename)

    print(f"Parse successful. DOT written to {output_filename}")


if __name__ == "__main__":
    try:
        main()
    except (LexerError, ParserError) as e:
        print(f"Error: {e}")
```

# Тестирование

Входные данные

```
$ This is a comment
`axiom E `is "n" `end
```

Вывод на `stdout`

```
digraph ParseTree {
  rankdir=TB;
  node [shape=box];
  edge [arrowhead=normal];
  n1 [label="<Start>"];
  n2 [label="<Grammar>"];
  n3 [label="<Rule>"];
  n4 [label="<AxiomRule>"];
  n5 [label="`axiom"];
  n4 -> n5;
  n6 [label="NONTERM(\"E\")"];
  n4 -> n6;
  n7 [label="`is"];
  n4 -> n7;
  n8 [label="<Expr>"];
  n9 [label="<Alternative>"];
  n10 [label="<SymbolList>"];
  n11 [label="<Symbol>"];
  n12 [label="TERM(\"n\")"];
  n11 -> n12;
  n10 -> n11;
  n13 [label="<SymbolListTail>"];
  n14 [label="ε"];
  n13 -> n14;
  n10 -> n13;
  { rank=same; n11 -> n13 [style=invis]; }
  n9 -> n10;
  n8 -> n9;
  n15 [label="<ExprTail>"];
  n16 [label="ε"];
  n15 -> n16;
  n8 -> n15;
  { rank=same; n9 -> n15 [style=invis]; }
  n4 -> n8;
  n17 [label="`end"];
  n4 -> n17;
  { rank=same; n5 -> n6 -> n7 -> n8 -> n17 [style=invis]; }
  n3 -> n4;
  n2 -> n3;
  n18 [label="<GrammarTail>"];
  n19 [label="ε"];
  n18 -> n19;
  n2 -> n18;
  { rank=same; n3 -> n18 [style=invis]; }
  n1 -> n2;
  n20 [label="EOF"];
  n1 -> n20;
  { rank=same; n2 -> n20 [style=invis]; }
}
```

# Вывод

В ходе лабораторной работы был реализован синтаксический анализатор на основе предсказывающего разбора.
Для входного языка были описаны лексическая структура, грамматика и таблица разбора.
Также был разработан лексический анализатор и алгоритм построения дерева вывода.
Программа разбирает входные правила грамматики и формирует дерево вывода в формате DOT.
