## Абстрактный синтаксис языка

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


## Конкретный синтаксис языка

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