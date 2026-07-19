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
