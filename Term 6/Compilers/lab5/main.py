from __future__ import annotations

import abc
import re
import sys
import os
from dataclasses import dataclass
from pprint import pformat

import parser_edsl as pe


# Абстрактное синтаксическое дерево


class Section(abc.ABC):
    pass


class TypeExpr(abc.ABC):
    pass


class ConstExpr(abc.ABC):
    pass


# Program -> Section*
@dataclass
class Program:
    sections: list[Section]


# Section -> TypeSection
@dataclass
class TypeSection(Section):
    definitions: list["TypeDef"]


# Section -> ConstSection
@dataclass
class ConstSection(Section):
    definitions: list["ConstDef"]


# TypeDef -> IDENT = TypeExpr
@dataclass
class TypeDef:
    name: str
    type_expr: TypeExpr


# ConstDef -> IDENT = ConstExpr
@dataclass
class ConstDef:
    name: str
    const_expr: ConstExpr


# TypeExpr -> NamedType
@dataclass
class NamedType(TypeExpr):
    name: str


# TypeExpr -> EnumType
# EnumType -> ( IDENT { , IDENT } )
@dataclass
class EnumType(TypeExpr):
    values: list[str]


# TypeExpr -> RangeType
# RangeType -> ConstExpr .. ConstExpr
@dataclass
class RangeType(TypeExpr):
    left: ConstExpr
    right: ConstExpr


# TypeExpr -> ArrayType
# ArrayType -> array TypeExpr of TypeExpr
@dataclass
class ArrayType(TypeExpr):
    index_type: TypeExpr
    element_type: TypeExpr


# TypeExpr -> SetType
# SetType -> set of TypeExpr
@dataclass
class SetType(TypeExpr):
    base_type: TypeExpr


# Field -> IdentList : TypeExpr
@dataclass
class Field:
    names: list[str]
    type_expr: TypeExpr


# VariantBranch -> ConstList : ( FieldListOpt )
@dataclass
class VariantBranch:
    labels: list[ConstExpr]
    fields: list[Field]


# VariantPart -> case IDENT : NamedType of VariantBranchList
@dataclass
class VariantPart:
    tag_name: str
    tag_type: NamedType
    branches: list[VariantBranch]


# TypeExpr -> RecordType
# RecordType -> record RecordBody end
@dataclass
class RecordType(TypeExpr):
    fields: list[Field]
    variant_part: VariantPart | None

# TypeExpr -> CallbackType
@dataclass
class CallbackType(TypeExpr):
    procedure_params: list[Field]

# TypeExpr -> PointerType
# PointerType -> ^ NamedType
@dataclass
class PointerType(TypeExpr):
    ref_type: NamedType


# ConstExpr -> INT_CONST
@dataclass
class IntConst(ConstExpr):
    value: int


# ConstExpr -> REAL_CONST
@dataclass
class RealConst(ConstExpr):
    value: float


# ConstExpr -> IDENT
@dataclass
class IdentConst(ConstExpr):
    name: str


# ConstExpr -> + ConstExpr
# ConstExpr -> - ConstExpr
@dataclass
class UnaryConst(ConstExpr):
    op: str
    expr: ConstExpr


# Лексическая структура

def normalize_ident(name: str) -> str:
    """Ключевые слова и идентификаторы нечувствительны к регистру.
    Для AST имена удобно хранить в верхнем регистре.
    """
    return name.upper()


# REAL_CONST -> вещественное число в десятичной записи
REAL_CONST = pe.Terminal(
    "REAL_CONST",
    r"(?:[0-9]+\.[0-9]+(?:[eE][-+]?[0-9]+)?|[0-9]+[eE][-+]?[0-9]+)",
    float,
    priority=6,
)

# INT_CONST -> [0-9]+
INT_CONST = pe.Terminal("INT_CONST", r"[0-9]+", int, priority=7)

# IDENT -> [A-Za-z][A-Za-z0-9]*
IDENT = pe.Terminal("IDENT", r"[A-Za-z][A-Za-z0-9]*", normalize_ident)


def make_keyword(image: str) -> pe.Terminal:
    return pe.Terminal(
        image,
        image,
        lambda _: None,
        re_flags=re.IGNORECASE,
        priority=10,
    )


# Ключевые слова Pascal (нечувствительные к регистру)
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
    KW_PROCEDURE,
) = map(
    make_keyword,
    "type const array of set record end case integer real char boolean procedure".split(),
)


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
NVariantPart = pe.NonTerminal("VariantPart")
NVariantBranchList = pe.NonTerminal("VariantBranchList")
NVariantBranch = pe.NonTerminal("VariantBranch")
NFieldListOpt = pe.NonTerminal("FieldListOpt")
NConstList = pe.NonTerminal("ConstList")
NConstExpr = pe.NonTerminal("ConstExpr")


# Правила грамматики


# Program -> Sections
NProgram |= NSections, Program


# Sections -> ε
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
NTypeDefs |= NTypeDef, lambda typedef_: [typedef_]

# TypeDefs -> TypeDefs TypeDef
NTypeDefs |= NTypeDefs, NTypeDef, lambda typedefs, typedef_: typedefs + [typedef_]


# ConstDefs -> ConstDef
NConstDefs |= NConstDef, lambda constdef: [constdef]

# ConstDefs -> ConstDefs ConstDef
NConstDefs |= NConstDefs, NConstDef, lambda constdefs, constdef: constdefs + [constdef]


# TypeDef -> IDENT = TypeExpr ;
NTypeDef |= IDENT, "=", NTypeExpr, ";", TypeDef

# ConstDef -> IDENT = ConstExpr ;
NConstDef |= IDENT, "=", NConstExpr, ";", ConstDef


# TypeName -> IDENT
NTypeName |= IDENT, NamedType

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
NTypeExpr |= NConstExpr, "..", NConstExpr, RangeType

# TypeExpr -> ARRAY TypeExpr OF TypeExpr
NTypeExpr |= KW_ARRAY, NTypeExpr, KW_OF, NTypeExpr, ArrayType

# TypeExpr -> SET OF TypeExpr
NTypeExpr |= KW_SET, KW_OF, NTypeExpr, SetType

# TypeExpr -> ^ TypeName
NTypeExpr |= "^", NTypeName, PointerType

# TypeExpr -> RECORD RecordBody END
NTypeExpr |= KW_RECORD, NRecordBody, KW_END, lambda body: RecordType(body[0], body[1])

## NEW
NTypeExpr |= KW_PROCEDURE, "(", NFieldListOpt, ")", CallbackType

# RecordBody -> ε
NRecordBody |= lambda: ([], None)

# RecordBody -> FieldList
NRecordBody |= NFieldList, lambda fields: (fields, None)

# RecordBody -> VariantPart
NRecordBody |= NVariantPart, lambda variant_part: ([], variant_part)

# RecordBody -> FieldList ; VariantPart
NRecordBody |= (
    NFieldList,
    ";",
    NVariantPart,
    lambda fields, variant_part: (fields, variant_part),
)


# FieldList -> Field
NFieldList |= NField, lambda field: [field]

# FieldList -> FieldList ; Field
NFieldList |= NFieldList, ";", NField, lambda fields, field: fields + [field]


# Field -> IdentList : TypeExpr
NField |= NIdentList, ":", NTypeExpr, Field


# IdentList -> IDENT
NIdentList |= IDENT, lambda ident: [ident]

# IdentList -> IdentList , IDENT
NIdentList |= NIdentList, ",", IDENT, lambda idents, ident: idents + [ident]


# VariantPart -> CASE IDENT : TypeName OF VariantBranchList
NVariantPart |= (
    KW_CASE,
    IDENT,
    ":",
    NTypeName,
    KW_OF,
    NVariantBranchList,
    VariantPart,
)


# VariantBranchList -> VariantBranch
NVariantBranchList |= NVariantBranch, lambda branch: [branch]

# VariantBranchList -> VariantBranchList ; VariantBranch
NVariantBranchList |= (
    NVariantBranchList,
    ";",
    NVariantBranch,
    lambda branches, branch: branches + [branch],
)


# VariantBranch -> ConstList : ( FieldListOpt )
NVariantBranch |= NConstList, ":", "(", NFieldListOpt, ")", VariantBranch


# FieldListOpt -> ε
NFieldListOpt |= lambda: []

# FieldListOpt -> FieldList
NFieldListOpt |= NFieldList


# ConstList -> ConstExpr
NConstList |= NConstExpr, lambda const_expr: [const_expr]

# ConstList -> ConstList , ConstExpr
NConstList |= (
    NConstList,
    ",",
    NConstExpr,
    lambda consts, const_expr: consts + [const_expr],
)


# ConstExpr -> INT_CONST
NConstExpr |= INT_CONST, IntConst

# ConstExpr -> REAL_CONST
NConstExpr |= REAL_CONST, RealConst

# ConstExpr -> IDENT
NConstExpr |= IDENT, IdentConst

# ConstExpr -> + ConstExpr
NConstExpr |= "+", NConstExpr, lambda expr: UnaryConst("+", expr)

# ConstExpr -> - ConstExpr
NConstExpr |= "-", NConstExpr, lambda expr: UnaryConst("-", expr)


# Построение парсера

def build_parser() -> pe.Parser:
    parser = pe.Parser(NProgram, method=pe.EARLEY)

    # Пробелы, табы, переводы строк
    parser.add_skipped_domain(r"\s+")

    # Комментарии Pascal:
    # { ... }
    # (* ... *)
    parser.add_skipped_domain(r"(?:\{[\s\S]*?\}|\(\*[\s\S]*?\*\))")

    return parser


# Работа с файлами

def analyze_file(input_path: str, output_path: str) -> int:
    """Читает input-файл, строит AST и записывает результат в output-файл.
    Если output-файл уже существует, он перезаписывается.
    """
    parser = build_parser()

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = parser.parse(source)
        result_text = pformat(tree, sort_dicts=False, width=120)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result_text)
            f.write("\n")
        print("Анализ завершён успешно. Результат записан в", output_path)
        return 0

    except pe.Error as e:
        error_text = f"Ошибка {e.pos}: {e.message}"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(error_text)
            f.write("\n")
        print(error_text, file=sys.stderr)
        return 1

    except Exception as e:
        error_text = f"Внутренняя ошибка: {e}"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(error_text)
            f.write("\n")
        print(error_text, file=sys.stderr)
        return 1


# Энтрипоинт

def main(argv: list[str]) -> int:
    if len(argv) <= 1:
        input_path = os.path.join(os.path.dirname(__file__), "assets/input.txt")
        output_path = os.path.join(os.path.dirname(__file__), "assets/output.txt")
    elif len(argv) == 2:
        input_path = argv[1]
        output_path = os.path.join(os.path.dirname(__file__), "assets/output.txt")
    else:
        input_path = argv[1]
        output_path = argv[2]

    return analyze_file(input_path, output_path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
