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
