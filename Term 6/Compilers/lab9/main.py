from __future__ import annotations

import abc
import math
import os
import re
import sys
from dataclasses import dataclass, field
import parser_edsl as pe


# Семантические ошибки


class SemanticError(pe.Error):
    def __init__(self, pos: pe.Position, message: str):
        self.pos = pos
        self._message = message

    @property
    def message(self) -> str:
        return self._message


class RepeatedNameError(SemanticError):
    def __init__(self, pos: pe.Position, name: str):
        super().__init__(pos, f"Повторное объявление имени {name}")


class RepeatedFieldError(SemanticError):
    def __init__(self, pos: pe.Position, name: str):
        super().__init__(pos, f"Повторное поле {name}")


class UnknownNameError(SemanticError):
    def __init__(self, pos: pe.Position, name: str):
        super().__init__(pos, f"Имя {name} не определено выше по тексту")


class BadTypeError(SemanticError):
    pass


# Таблицы символов


# Symbol: именованная сущность.
@dataclass
class Symbol:
    name: str


# ConstSymbol: обычная константа или элемент перечисления.
@dataclass
class ConstSymbol(Symbol):
    value: int | float


# TypeSymbol: объявленный тип.
@dataclass
class TypeSymbol(Symbol):
    type_info: "TypeInfo"


# TypeInfo: вычисленная информация о типе.
# size: размер значения в байтах.
# cardinality: число значений конечного порядкового типа.
@dataclass
class TypeInfo:
    size: int
    cardinality: int | None = None


@dataclass
class SymbolTable:
    """Локальная таблица символов"""

    symbols: dict[str, Symbol] = field(default_factory=dict)

    def add(self, symbol: Symbol, pos: pe.Position) -> None:
        if symbol.name in self.symbols:
            raise RepeatedNameError(pos, symbol.name)
        self.symbols[symbol.name] = symbol

    def find(self, name: str, pos: pe.Position) -> Symbol:
        try:
            return self.symbols[name]
        except KeyError:
            raise UnknownNameError(pos, name)


@dataclass
class SemanticContext:
    """Состояние семантического анализа"""

    globals: SymbolTable = field(default_factory=SymbolTable)
    constants: list[ConstSymbol] = field(default_factory=list)
    types: list[TypeSymbol] = field(default_factory=list)
    current_type: str | None = None

    def add_const(self, name: str, value: int | float, pos: pe.Position) -> None:
        symbol = ConstSymbol(name, value)
        self.globals.add(symbol, pos)
        self.constants.append(symbol)

    def add_type(self, name: str, info: TypeInfo, pos: pe.Position) -> None:
        symbol = TypeSymbol(name, info)
        self.globals.add(symbol, pos)
        self.types.append(symbol)

    def find_const(self, name: str, pos: pe.Position) -> ConstSymbol:
        symbol = self.globals.find(name, pos)
        if not isinstance(symbol, ConstSymbol):
            raise BadTypeError(pos, f"Имя {name} не является константой")
        return symbol

    def find_type(self, name: str, pos: pe.Position) -> TypeSymbol:
        symbol = self.globals.find(name, pos)
        if not isinstance(symbol, TypeSymbol):
            raise BadTypeError(pos, f"Имя {name} не является типом")
        return symbol


BUILTIN_TYPES = {
    # cardinality используется для массивов и множеств.
    "INTEGER": TypeInfo(size=2),
    "REAL": TypeInfo(size=4),
    "CHAR": TypeInfo(size=1, cardinality=256),
    "BOOLEAN": TypeInfo(size=1, cardinality=2),
}


# Абстрактное синтаксическое дерево


@dataclass
class LocatedName:
    # IDENT с координатой начала лексемы.
    name: str
    pos: pe.Position

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, = attrs
        return LocatedName(name, coords[0].start)


class Section(abc.ABC):
    @abc.abstractmethod
    def check(self, ctx: SemanticContext) -> None:
        pass


class TypeExpr(abc.ABC):
    # Возвращает вычисленную информацию о типе.
    @abc.abstractmethod
    def evaluate(self, ctx: SemanticContext) -> TypeInfo:
        pass


class ConstExpr(abc.ABC):
    # Вычисляет значение константного выражения.
    @abc.abstractmethod
    def evaluate(self, ctx: SemanticContext) -> int | float:
        pass


# Program -> Section*
@dataclass
class Program:
    sections: list[Section]
    symbol_table: SymbolTable | None = field(default=None, init=False)
    constants: list[ConstSymbol] = field(default_factory=list, init=False)
    types: list[TypeSymbol] = field(default_factory=list, init=False)

    def check(self) -> None:
        # Главный семантический проход
        ctx = SemanticContext()
        for section in self.sections:
            section.check(ctx)
        self.symbol_table = ctx.globals
        self.constants = ctx.constants
        self.types = ctx.types

    def format_result(self) -> str:
        # Формирование результата для корректной программы.
        lines = ["Программа корректна", "", "Константы:"]
        lines.extend(f"  {symbol.name} = {symbol.value}" for symbol in self.constants)
        lines.extend(("", "Типы:"))
        lines.extend(f"  {symbol.name} = {symbol.type_info.size} байт" for symbol in self.types)
        return "\n".join(lines)


# Section -> TypeSection
@dataclass
class TypeSection(Section):
    definitions: list["TypeDef"]

    def check(self, ctx: SemanticContext) -> None:
        for definition in self.definitions:
            definition.check(ctx)


# Section -> ConstSection
@dataclass
class ConstSection(Section):
    definitions: list["ConstDef"]

    def check(self, ctx: SemanticContext) -> None:
        for definition in self.definitions:
            definition.check(ctx)


# TypeDef -> IDENT = TypeExpr
@dataclass
class TypeDef:
    name: LocatedName
    type_expr: TypeExpr

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, type_expr = attrs
        return TypeDef(LocatedName(name, coords[0].start), type_expr)

    def check(self, ctx: SemanticContext) -> None:
        # Правая часть вычисляется до добавления имени.
        previous = ctx.current_type
        ctx.current_type = self.name.name
        try:
            info = self.type_expr.evaluate(ctx)
            ctx.add_type(self.name.name, info, self.name.pos)
        finally:
            ctx.current_type = previous


# ConstDef -> IDENT = ConstExpr
@dataclass
class ConstDef:
    name: LocatedName
    const_expr: ConstExpr

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, const_expr = attrs
        return ConstDef(LocatedName(name, coords[0].start), const_expr)

    def check(self, ctx: SemanticContext) -> None:
        ctx.add_const(self.name.name, self.const_expr.evaluate(ctx), self.name.pos)


# TypeExpr -> NamedType
@dataclass
class NamedType(TypeExpr):
    name: str
    pos: pe.Position | None = None

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, = attrs
        return NamedType(name, coords[0].start)

    def evaluate(self, ctx: SemanticContext) -> TypeInfo:
        # Встроенный тип или ранее объявленный тип.
        if self.name in BUILTIN_TYPES:
            return BUILTIN_TYPES[self.name]
        assert self.pos is not None
        return ctx.find_type(self.name, self.pos).type_info


# TypeExpr -> EnumType
# EnumType -> ( IDENT { , IDENT } )
@dataclass
class EnumType(TypeExpr):
    values: list[LocatedName]

    def evaluate(self, ctx: SemanticContext) -> TypeInfo:
        # Элементы перечисления становятся константами.
        for value, item in enumerate(self.values):
            ctx.add_const(item.name, value, item.pos)
        return TypeInfo(size=2, cardinality=len(self.values))


# TypeExpr -> RangeType
# RangeType -> ConstExpr .. ConstExpr
@dataclass
class RangeType(TypeExpr):
    left: ConstExpr
    right: ConstExpr
    pos: pe.Position

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        left, right = attrs
        return RangeType(left, right, coords[1].start)

    def evaluate(self, ctx: SemanticContext) -> TypeInfo:
        # Диапазон задаёт конечный порядковый тип.
        left = self.left.evaluate(ctx)
        right = self.right.evaluate(ctx)
        if not isinstance(left, int) or not isinstance(right, int):
            raise BadTypeError(self.pos, "Границы диапазона должны быть целыми")
        if left > right:
            raise BadTypeError(self.pos, f"Левая граница диапазона {left} больше правой {right}")
        return TypeInfo(size=2, cardinality=right - left + 1)


# TypeExpr -> ArrayType
# ArrayType -> array TypeExpr of TypeExpr
@dataclass
class ArrayType(TypeExpr):
    index_type: TypeExpr
    element_type: TypeExpr
    pos: pe.Position

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        index_type, element_type = attrs
        return ArrayType(index_type, element_type, coords[0].start)

    def evaluate(self, ctx: SemanticContext) -> TypeInfo:
        # Размер массива зависит от мощности индексного типа.
        index = self.index_type.evaluate(ctx)
        if index.cardinality is None:
            raise BadTypeError(self.pos, "Для индекса массива нужен конечный порядковый тип")
        element = self.element_type.evaluate(ctx)
        return TypeInfo(size=index.cardinality * element.size)


# TypeExpr -> SetType
# SetType -> set of TypeExpr
@dataclass
class SetType(TypeExpr):
    base_type: TypeExpr
    pos: pe.Position

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        base_type, = attrs
        return SetType(base_type, coords[0].start)

    def evaluate(self, ctx: SemanticContext) -> TypeInfo:
        # Один бит на каждый элемент базового типа.
        base = self.base_type.evaluate(ctx)
        if base.cardinality is None:
            raise BadTypeError(self.pos, "Для множества нужен конечный порядковый тип")
        return TypeInfo(size=math.ceil(base.cardinality / 8))


# Field -> IdentList : TypeExpr
@dataclass
class Field:
    names: list[LocatedName]
    type_expr: TypeExpr

    def evaluate(self, ctx: SemanticContext, fields: SymbolTable) -> int:
        # Проверка имён в локальной таблице записи.
        info = self.type_expr.evaluate(ctx)
        for name in self.names:
            if name.name in fields.symbols:
                raise RepeatedFieldError(name.pos, name.name)
            fields.symbols[name.name] = Symbol(name.name)
        return len(self.names) * info.size


# VariantBranch -> ConstList : ( FieldListOpt )
@dataclass
class VariantBranch:
    labels: list[ConstExpr]
    fields: list[Field]

    def evaluate(self, ctx: SemanticContext, fields: SymbolTable) -> int:
        # Проверка меток и вычисление размера ветви.
        for label in self.labels:
            label.evaluate(ctx)
        return sum(item.evaluate(ctx, fields) for item in self.fields)


# VariantPart -> case IDENT : NamedType of VariantBranchList
@dataclass
class VariantPart:
    tag_name: LocatedName
    tag_type: NamedType
    branches: list[VariantBranch]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        tag_name, tag_type, branches = attrs
        return VariantPart(LocatedName(tag_name, coords[1].start), tag_type, branches)

    def evaluate(self, ctx: SemanticContext, fields: SymbolTable) -> int:
        # Тег плюс наибольшая ветвь.
        tag_info = self.tag_type.evaluate(ctx)
        if self.tag_name.name in fields.symbols:
            raise RepeatedFieldError(self.tag_name.pos, self.tag_name.name)
        fields.symbols[self.tag_name.name] = Symbol(self.tag_name.name)
        branch_sizes = [branch.evaluate(ctx, fields) for branch in self.branches]
        return tag_info.size + max(branch_sizes, default=0)


# TypeExpr -> RecordType
# RecordType -> record RecordBody end
@dataclass
class RecordType(TypeExpr):
    fields: list[Field]
    variant_part: VariantPart | None
    symbol_table: SymbolTable | None = field(default=None, init=False)

    def evaluate(self, ctx: SemanticContext) -> TypeInfo:
        # Локальная таблица полей записи.
        self.symbol_table = SymbolTable()
        size = sum(item.evaluate(ctx, self.symbol_table) for item in self.fields)
        if self.variant_part is not None:
            size += self.variant_part.evaluate(ctx, self.symbol_table)
        return TypeInfo(size=size)


# TypeExpr -> PointerType
# PointerType -> ^ NamedType
@dataclass
class PointerType(TypeExpr):
    ref_type: NamedType

    def evaluate(self, ctx: SemanticContext) -> TypeInfo:
        # Проверка имени базового типа.
        if self.ref_type.name != ctx.current_type:
            self.ref_type.evaluate(ctx)
        return TypeInfo(size=4)


# ConstExpr -> INT_CONST
@dataclass
class IntConst(ConstExpr):
    value: int

    def evaluate(self, ctx: SemanticContext) -> int:
        return self.value


# ConstExpr -> REAL_CONST
@dataclass
class RealConst(ConstExpr):
    value: float

    def evaluate(self, ctx: SemanticContext) -> float:
        return self.value


# ConstExpr -> IDENT
@dataclass
class IdentConst(ConstExpr):
    name: str
    pos: pe.Position

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, = attrs
        return IdentConst(name, coords[0].start)

    def evaluate(self, ctx: SemanticContext) -> int | float:
        # Ссылка на объявленную константу.
        return ctx.find_const(self.name, self.pos).value


# ConstExpr -> + ConstExpr
# ConstExpr -> - ConstExpr
@dataclass
class UnaryConst(ConstExpr):
    op: str
    expr: ConstExpr

    def evaluate(self, ctx: SemanticContext) -> int | float:
        value = self.expr.evaluate(ctx)
        return value if self.op == "+" else -value


# Лексическая структура


def normalize_ident(name: str) -> str:
    # Нормализация регистра.
    return name.upper()


# REAL_CONST: вещественное число.
REAL_CONST = pe.Terminal(
    "REAL_CONST",
    r"(?:[0-9]+\.[0-9]+(?:[eE][-+]?[0-9]+)?|[0-9]+[eE][-+]?[0-9]+)",
    float,
    priority=6,
)

# INT_CONST: целое число.
INT_CONST = pe.Terminal("INT_CONST", r"[0-9]+", int, priority=7)

# IDENT: латинский идентификатор.
IDENT = pe.Terminal("IDENT", r"[A-Za-z][A-Za-z0-9]*", normalize_ident)


def make_keyword(image: str) -> pe.Terminal:
    return pe.Terminal(image, image, lambda _: None, re_flags=re.IGNORECASE, priority=10)


# Ключевые слова Pascal
(
    KW_TYPE,
    KW_CONST,
    KW_ARRAY,
    KW_OF,
    KW_SET,
    KW_RECORD,
    KW_END,
    KW_CASE,
    KW_INTEGER,
    KW_REAL,
    KW_CHAR,
    KW_BOOLEAN,
) = map(
    make_keyword,
    "type const array of set record end case integer real char boolean".split(),
)


# Конкретный синтаксис


# Нетерминалы грамматики
NProgram = pe.NonTerminal("Program")
NSections = pe.NonTerminal("Sections")
NSection = pe.NonTerminal("Section")
NTypeSection = pe.NonTerminal("TypeSection")
NConstSection = pe.NonTerminal("ConstSection")
NTypeDefs = pe.NonTerminal("TypeDefs")
NConstDefs = pe.NonTerminal("ConstDefs")
NTypeDef = pe.NonTerminal("TypeDef")
NConstDef = pe.NonTerminal("ConstDef")
NTypeExpr = pe.NonTerminal("TypeExpr")
NTypeName = pe.NonTerminal("TypeName")
NRecordBody = pe.NonTerminal("RecordBody")
NFieldList = pe.NonTerminal("FieldList")
NField = pe.NonTerminal("Field")
NIdentList = pe.NonTerminal("IdentList")
NLocatedIdent = pe.NonTerminal("LocatedIdent")
NVariantPart = pe.NonTerminal("VariantPart")
NVariantBranchList = pe.NonTerminal("VariantBranchList")
NVariantBranch = pe.NonTerminal("VariantBranch")
NFieldListOpt = pe.NonTerminal("FieldListOpt")
NConstList = pe.NonTerminal("ConstList")
NConstExpr = pe.NonTerminal("ConstExpr")


# Правила грамматики


# Program -> Sections
NProgram |= NSections, Program

# Sections -> empty
NSections |= lambda: []

# Sections -> Sections Section
NSections |= NSections, NSection, lambda sections, section: sections + [section]

# Section -> TypeSection
NSection |= NTypeSection

# Section -> ConstSection
NSection |= NConstSection

# TypeSection -> TYPE TypeDefs
NTypeSection |= KW_TYPE, NTypeDefs, TypeSection

# ConstSection -> CONST ConstDefs
NConstSection |= KW_CONST, NConstDefs, ConstSection

# TypeDefs -> TypeDef
NTypeDefs |= NTypeDef, lambda definition: [definition]

# TypeDefs -> TypeDefs TypeDef
NTypeDefs |= NTypeDefs, NTypeDef, lambda definitions, definition: definitions + [definition]

# ConstDefs -> ConstDef
NConstDefs |= NConstDef, lambda definition: [definition]

# ConstDefs -> ConstDefs ConstDef
NConstDefs |= NConstDefs, NConstDef, lambda definitions, definition: definitions + [definition]

# TypeDef -> IDENT = TypeExpr ;
NTypeDef |= IDENT, "=", NTypeExpr, ";", TypeDef.create

# ConstDef -> IDENT = ConstExpr ;
NConstDef |= IDENT, "=", NConstExpr, ";", ConstDef.create

# TypeName -> IDENT
NTypeName |= IDENT, NamedType.create

# TypeName -> INTEGER
NTypeName |= KW_INTEGER, lambda: NamedType("INTEGER")

# TypeName -> REAL
NTypeName |= KW_REAL, lambda: NamedType("REAL")

# TypeName -> CHAR
NTypeName |= KW_CHAR, lambda: NamedType("CHAR")

# TypeName -> BOOLEAN
NTypeName |= KW_BOOLEAN, lambda: NamedType("BOOLEAN")

# TypeExpr -> TypeName
NTypeExpr |= NTypeName

# TypeExpr -> ( IdentList )
NTypeExpr |= "(", NIdentList, ")", EnumType

# TypeExpr -> ConstExpr .. ConstExpr
NTypeExpr |= NConstExpr, "..", NConstExpr, RangeType.create

# TypeExpr -> ARRAY TypeExpr OF TypeExpr
NTypeExpr |= KW_ARRAY, NTypeExpr, KW_OF, NTypeExpr, ArrayType.create

# TypeExpr -> SET OF TypeExpr
NTypeExpr |= KW_SET, KW_OF, NTypeExpr, SetType.create

# TypeExpr -> ^ TypeName
NTypeExpr |= "^", NTypeName, PointerType

# TypeExpr -> RECORD RecordBody END
NTypeExpr |= KW_RECORD, NRecordBody, KW_END, lambda body: RecordType(body[0], body[1])

# RecordBody -> empty
NRecordBody |= lambda: ([], None)

# RecordBody -> FieldList
NRecordBody |= NFieldList, lambda fields: (fields, None)

# RecordBody -> VariantPart
NRecordBody |= NVariantPart, lambda variant: ([], variant)

# RecordBody -> FieldList ; VariantPart
NRecordBody |= NFieldList, ";", NVariantPart, lambda fields, variant: (fields, variant)

# FieldList -> Field
NFieldList |= NField, lambda item: [item]

# FieldList -> FieldList ; Field
NFieldList |= NFieldList, ";", NField, lambda items, item: items + [item]

# Field -> IdentList : TypeExpr
NField |= NIdentList, ":", NTypeExpr, Field

# LocatedIdent -> IDENT
NLocatedIdent |= IDENT, LocatedName.create

# IdentList -> LocatedIdent
NIdentList |= NLocatedIdent, lambda name: [name]

# IdentList -> IdentList , LocatedIdent
NIdentList |= NIdentList, ",", NLocatedIdent, lambda names, name: names + [name]

# VariantPart -> CASE IDENT : TypeName OF VariantBranchList
NVariantPart |= KW_CASE, IDENT, ":", NTypeName, KW_OF, NVariantBranchList, VariantPart.create

# VariantBranchList -> VariantBranch
NVariantBranchList |= NVariantBranch, lambda branch: [branch]

# VariantBranchList -> VariantBranchList ; VariantBranch
NVariantBranchList |= NVariantBranchList, ";", NVariantBranch, lambda branches, branch: branches + [branch]

# VariantBranch -> ConstList : ( FieldListOpt )
NVariantBranch |= NConstList, ":", "(", NFieldListOpt, ")", VariantBranch

# FieldListOpt -> empty
NFieldListOpt |= lambda: []

# FieldListOpt -> FieldList
NFieldListOpt |= NFieldList

# ConstList -> ConstExpr
NConstList |= NConstExpr, lambda item: [item]

# ConstList -> ConstList , ConstExpr
NConstList |= NConstList, ",", NConstExpr, lambda items, item: items + [item]

# ConstExpr -> INT_CONST
NConstExpr |= INT_CONST, IntConst

# ConstExpr -> REAL_CONST
NConstExpr |= REAL_CONST, RealConst

# ConstExpr -> IDENT
NConstExpr |= IDENT, IdentConst.create

# ConstExpr -> + ConstExpr
NConstExpr |= "+", NConstExpr, lambda expr: UnaryConst("+", expr)

# ConstExpr -> - ConstExpr
NConstExpr |= "-", NConstExpr, lambda expr: UnaryConst("-", expr)


def build_parser() -> pe.Parser:
    # Пропуск пробелов и комментариев Pascal.
    parser = pe.Parser(NProgram, method=pe.EARLEY)
    parser.add_skipped_domain(r"\s+")
    parser.add_skipped_domain(r"(?:\{[\s\S]*?\}|\(\*[\s\S]*?\*\))")
    return parser


def analyze_file(input_path: str) -> int:
    # Чтение, разбор, проверка, вывод.
    try:
        with open(input_path, encoding="utf-8") as source:
            tree = build_parser().parse(source.read())
        tree.check()
        print(tree.format_result())
        return 0
    except pe.Error as error:
        print(f"Ошибка {error.pos}: {error.message}", file=sys.stderr)
        return 1


def main(argv: list[str]) -> int:
    input_path = argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(__file__), "assets/input.txt")
    return analyze_file(input_path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
