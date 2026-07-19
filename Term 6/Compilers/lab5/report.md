% Лабораторная работа № 2.2 «Абстрактные синтаксические деревья» 
% 8 апреля 2026 г. 
% Александр Федуков, ИУ9-62Б

# Цель работы

Целью данной работы является получение навыков составления грамматик и проектирования синтаксических деревьев.

# Индивидуальный вариант

Объявления типов и констант в Паскале. Ключевые слова и идентификаторы не чувствительны к регистру.

Пример:

```pascal
Type
  Coords = Record x, y: INTEGER end;
Const
  MaxPoints = 100;
type
  CoordsVector = array 1..MaxPoints of Coords;

(* графический и текстовый дисплеи *)
const
  Heigh = 480;
  Width = 640;
  Lines = 24;
  Columns = 80;
type
  BaseColor = (red, green, blue, highlited);
  Color = set of BaseColor;
  GraphicScreen = array 1..Heigh of array 1..Width of Color;
  TextScreen = array 1..Lines of array 1..Columns of
    record
      Symbol : CHAR;
      SymColor : Color;
      BackColor : Color
    end;

{ определения токенов }
TYPE
  Domain = (Ident, IntNumber, RealNumber);
  Token = record
    fragment : record
      start, following : record
        row, col : INTEGER
      end
    end;
    case tokType : Domain of
      Ident : (
        name : array 1..32 of CHAR
      );
      IntNumber : (
        intval : INTEGER
      );
      RealNumber : (
        realval : REAL
      )
  end;

  Year = 1900..2050;

  List = record
    value : Token;
    next : ^List
  end;
```

## Синтаксическое расширение для защиты

Добавить процедурный тип

```
TypeExpr -> PROCEDURE ( FieldListOpt )
```

```python
# TypeExpr -> CallbackType
@dataclass
class CallbackType(TypeExpr):
    procedure_params: list[Field]
...
KW_PROCEDURE
...
NTypeExpr |= KW_PROCEDURE, "(", NFieldListOpt, ")", CallbackType
```

# Реализация

## Абстрактный синтаксис

```
Program -> Section*

Section -> TypeSection
         | ConstSection

TypeSection -> TypeDef+
ConstSection -> ConstDef+

TypeDef -> IDENT = TypeExpr
ConstDef -> IDENT = ConstExpr

TypeExpr -> NamedType
          | EnumType
          | RangeType
          | ArrayType
          | SetType
          | RecordType
          | PointerType

NamedType -> IDENT
           | INTEGER
           | REAL
           | CHAR
           | BOOLEAN

EnumType -> ( IDENT { , IDENT } )

RangeType -> ConstExpr .. ConstExpr

ArrayType -> array TypeExpr of TypeExpr

SetType -> set of TypeExpr

RecordType -> record RecordBody end

RecordBody -> ε
            | FieldList
            | VariantPart
            | FieldList ; VariantPart

FieldList -> Field { ; Field }

Field -> IdentList : TypeExpr

IdentList -> IDENT { , IDENT }

VariantPart -> case IDENT : NamedType of VariantBranchList

VariantBranchList -> VariantBranch { ; VariantBranch }

VariantBranch -> ConstList : ( FieldListOpt )

FieldListOpt -> ε
              | FieldList

ConstList -> ConstExpr { , ConstExpr }

PointerType -> ^ NamedType

ConstExpr -> INT_CONST
           | REAL_CONST
           | IDENT
           | + ConstExpr
           | - ConstExpr

CallbackType -> procedure ( FieldListOpt )
```

## Лексическая структура и конкретный синтаксис

### Лексическая структура

Ключевые слова:
TYPE, CONST, ARRAY, OF, SET, RECORD, END, CASE, INTEGER, REAL, CHAR, BOOLEAN, PROCEDURE.
Ключевые слова не чувствительны к регистру.

Идентификаторы:
IDENT -> [A-Za-z][A-Za-z0-9]*
Идентификаторы не чувствительны к регистру и при построении AST приводятся к верхнему регистру.

Целые константы:
INT_CONST -> [0-9]+

Вещественные константы:
REAL_CONST -> [0-9]+\.[0-9]+([eE][-+]?[0-9]+)?
            | [0-9]+[eE][-+]?[0-9]+

Игнорируются пробельные символы и комментарии вида { ... } и (* ... *).

### Конкретный синтаксис

```
Program -> Sections

Sections -> ε
         | Sections Section

Section -> TypeSection
         | ConstSection

TypeSection -> TYPE TypeDefs

ConstSection -> CONST ConstDefs

TypeDefs -> TypeDef
         | TypeDefs TypeDef

ConstDefs -> ConstDef
          | ConstDefs ConstDef

TypeDef -> IDENT = TypeExpr ;

ConstDef -> IDENT = ConstExpr ;

TypeExpr -> TypeName
          | ( IdentList )
          | ConstExpr .. ConstExpr
          | ARRAY TypeExpr OF TypeExpr
          | SET OF TypeExpr
          | ^ TypeName
          | RECORD END
          | RECORD FieldList END
          | RECORD FieldList ; END
          | RECORD VariantPart END
          | RECORD FieldList ; VariantPart END
          | PROCEDURE ( FieldListOpt )

TypeName -> IDENT
          | INTEGER
          | REAL
          | CHAR
          | BOOLEAN

FieldList -> Field
           | FieldList ; Field

Field -> IdentList : TypeExpr

VariantPart -> CASE IDENT : TypeName OF VariantList

VariantList -> VariantBranch
             | VariantList ; VariantBranch

VariantBranch -> ConstList : ( FieldListOpt )

FieldListOpt -> ε
              | FieldList

IdentList -> IDENT
           | IdentList , IDENT

ConstList -> ConstExpr
           | ConstList , ConstExpr

ConstExpr -> INT_CONST
           | REAL_CONST
           | IDENT
           | + ConstExpr
           | - ConstExpr
```

## Программная реализация

```python
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
```

# Тестирование

## Входные данные

```
Type
  Coords = Record x, y: INTEGER end;
Const
  MaxPoints = 100;
type
  CoordsVector = array 1..MaxPoints of Coords;

(* графический и текстовый дисплеи *)
const
  Heigh = 480;
  Width = 640;
  Lines = 24;
  Columns = 80;
type
  BaseColor = (red, green, blue, highlited);
  Color = set of BaseColor;
  GraphicScreen = array 1..Heigh of array 1..Width of Color;
  TextScreen = array 1..Lines of array 1..Columns of
    record
      Symbol : CHAR;
      SymColor : Color;
      BackColor : Color
    end;

{ определения токенов }
TYPE
  Domain = (Ident, IntNumber, RealNumber);
  Token = record
    fragment : record
      start, following : record
        row, col : INTEGER
      end
    end;
    case tokType : Domain of
      Ident : (
        name : array 1..32 of CHAR
      );
      IntNumber : (
        intval : INTEGER
      );
      RealNumber : (
        realval : REAL
      )
  end;

  Year = 1900..2050;

  List = record
    value : Token;
    next : ^List
  end;



  Callbacks = record
    onclick : procedure(x, y: INTEGER; button: (Left, Mid, Right));
    onpress : procedure(key: CHAR; modifier: set of (Ctrl, Shift, Alt))
  end;
```

## Вывод на `stdout`

<!-- ENABLE LONG LINES -->

```
Program(sections=[TypeSection(definitions=[TypeDef(name='COORDS',
                                                   type_expr=RecordType(fields=[Field(names=['X', 'Y'],
                                                                                      type_expr=NamedType(name='INTEGER'))],
                                                                        variant_part=None))]),
                  ConstSection(definitions=[ConstDef(name='MAXPOINTS', const_expr=IntConst(value=100))]),
                  TypeSection(definitions=[TypeDef(name='COORDSVECTOR',
                                                   type_expr=ArrayType(index_type=RangeType(left=IntConst(value=1),
                                                                                            right=IdentConst(name='MAXPOINTS')),
                                                                       element_type=NamedType(name='COORDS')))]),
                  ConstSection(definitions=[ConstDef(name='HEIGH', const_expr=IntConst(value=480)),
                                            ConstDef(name='WIDTH', const_expr=IntConst(value=640)),
                                            ConstDef(name='LINES', const_expr=IntConst(value=24)),
                                            ConstDef(name='COLUMNS', const_expr=IntConst(value=80))]),
                  TypeSection(definitions=[TypeDef(name='BASECOLOR',
                                                   type_expr=EnumType(values=['RED', 'GREEN', 'BLUE', 'HIGHLITED'])),
                                           TypeDef(name='COLOR',
                                                   type_expr=SetType(base_type=NamedType(name='BASECOLOR'))),
                                           TypeDef(name='GRAPHICSCREEN',
                                                   type_expr=ArrayType(index_type=RangeType(left=IntConst(value=1),
                                                                                            right=IdentConst(name='HEIGH')),
                                                                       element_type=ArrayType(index_type=RangeType(left=IntConst(value=1),
                                                                                                                   right=IdentConst(name='WIDTH')),
                                                                                              element_type=NamedType(name='COLOR')))),
                                           TypeDef(name='TEXTSCREEN',
                                                   type_expr=ArrayType(index_type=RangeType(left=IntConst(value=1),
                                                                                            right=IdentConst(name='LINES')),
                                                                       element_type=ArrayType(index_type=RangeType(left=IntConst(value=1),
                                                                                                                   right=IdentConst(name='COLUMNS')),
                                                                                              element_type=RecordType(fields=[Field(names=['SYMBOL'],
                                                                                                                                    type_expr=NamedType(name='CHAR')),
                                                                                                                              Field(names=['SYMCOLOR'],
                                                                                                                                    type_expr=NamedType(name='COLOR')),
                                                                                                                              Field(names=['BACKCOLOR'],
                                                                                                                                    type_expr=NamedType(name='COLOR'))],
                                                                                                                      variant_part=None))))]),
                  TypeSection(definitions=[TypeDef(name='DOMAIN',
                                                   type_expr=EnumType(values=['IDENT', 'INTNUMBER', 'REALNUMBER'])),
                                           TypeDef(name='TOKEN',
                                                   type_expr=RecordType(fields=[Field(names=['FRAGMENT'],
                                                                                      type_expr=RecordType(fields=[Field(names=['START',
                                                                                                                                'FOLLOWING'],
                                                                                                                         type_expr=RecordType(fields=[Field(names=['ROW',
                                                                                                                                                                   'COL'],
                                                                                                                                                            type_expr=NamedType(name='INTEGER'))],
                                                                                                                                              variant_part=None))],
                                                                                                           variant_part=None))],
                                                                        variant_part=VariantPart(tag_name='TOKTYPE',
                                                                                                 tag_type=NamedType(name='DOMAIN'),
                                                                                                 branches=[VariantBranch(labels=[IdentConst(name='IDENT')],
                                                                                                                         fields=[Field(names=['NAME'],
                                                                                                                                       type_expr=ArrayType(index_type=RangeType(left=IntConst(value=1),
                                                                                                                                                                                right=IntConst(value=32)),
                                                                                                                                                           element_type=NamedType(name='CHAR')))]),
                                                                                                           VariantBranch(labels=[IdentConst(name='INTNUMBER')],
                                                                                                                         fields=[Field(names=['INTVAL'],
                                                                                                                                       type_expr=NamedType(name='INTEGER'))]),
                                                                                                           VariantBranch(labels=[IdentConst(name='REALNUMBER')],
                                                                                                                         fields=[Field(names=['REALVAL'],
                                                                                                                                       type_expr=NamedType(name='REAL'))])]))),
                                           TypeDef(name='YEAR',
                                                   type_expr=RangeType(left=IntConst(value=1900),
                                                                       right=IntConst(value=2050))),
                                           TypeDef(name='LIST',
                                                   type_expr=RecordType(fields=[Field(names=['VALUE'],
                                                                                      type_expr=NamedType(name='TOKEN')),
                                                                                Field(names=['NEXT'],
                                                                                      type_expr=PointerType(ref_type=NamedType(name='LIST')))],
                                                                        variant_part=None)),
                                           TypeDef(name='CALLBACKS',
                                                   type_expr=RecordType(fields=[Field(names=['ONCLICK'],
                                                                                      type_expr=CallbackType(procedure_params=[Field(names=['X',
                                                                                                                                            'Y'],
                                                                                                                                     type_expr=NamedType(name='INTEGER')),
                                                                                                                               Field(names=['BUTTON'],
                                                                                                                                     type_expr=EnumType(values=['LEFT',
                                                                                                                                                                'MID',
                                                                                                                                                                'RIGHT']))])),
                                                                                Field(names=['ONPRESS'],
                                                                                      type_expr=CallbackType(procedure_params=[Field(names=['KEY'],
                                                                                                                                     type_expr=NamedType(name='CHAR')),
                                                                                                                               Field(names=['MODIFIER'],
                                                                                                                                     type_expr=SetType(base_type=EnumType(values=['CTRL',
                                                                                                                                                                                  'SHIFT',
                                                                                                                                                                                  'ALT'])))]))],
                                                                        variant_part=None))])])
```

# Вывод

В ходе лабораторной работы была составлена грамматика для подмножества языка Паскаль, включающего объявления
типов и констант. Для синтаксических конструкций были описаны классы абстрактного синтаксического дерева. С
помощью библиотеки parser_edsl был реализован синтаксический анализатор, который выполняет лексический и
синтаксический разбор входной программы и строит AST.
