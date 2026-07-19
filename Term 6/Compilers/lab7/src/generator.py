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
