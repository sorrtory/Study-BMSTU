Вообще схема такая

```
program     -> список функций и процедур
function    -> Function ... statements End Function
sub         -> Sub ... statements End Sub
statement   -> assignment | if | for | do_loop | dim | call
expr        -> идентификаторы, числа, строки, операции, скобки
```

то есть продолжая бизон будет таким

```
program
    : modules
    ;

modules
    : module
    | modules module
    ;

module
    : function
    | sub
    ;

function
    : FUNCTION IDENT '(' params ')' statements END FUNCTION
    ;

sub
    : SUB IDENT '(' params ')' statements END SUB
    ;

statements
    : /* empty */
    | statements statement
    ;

statement
    : assignment
    | if_stmt
    | for_stmt
    | do_stmt
    | dim_stmt
    | call
    ;

assignment
    : IDENT '=' expr
    ;

if_stmt
    : IF expr THEN statements END IF
    | IF expr THEN statements ELSE statements END IF
    ;

for_stmt
    : FOR IDENT '=' expr TO expr statements NEXT IDENT
    ;

do_stmt
    : DO statements LOOP
    | DO WHILE expr statements LOOP
    | DO UNTIL expr statements LOOP
    | DO statements LOOP WHILE expr
    | DO statements LOOP UNTIL expr
    ;

dim_stmt
    : DIM IDENT '(' expr ')'
    ;

call
    : IDENT
    | IDENT '(' args ')'
    ;

expr
    : IDENT
    | NUMBER
    | STRING
    | call
    | '(' expr ')'
    | expr '+' expr
    | expr '-' expr
    | expr '*' expr
    | expr '/' expr
    ;
```

тогда чтобы скомпилировать опишем как-то так

```
%{
#include <stdio.h>

int yylex(void);
void yyerror(const char *msg);
%}

%token IDENT
%token NUMBER
%token STRING
%token NEWLINE

%token FUNCTION
%token SUB
%token END
%token IF
%token THEN
%token ELSE
%token FOR
%token TO
%token NEXT
%token DO
%token WHILE
%token UNTIL
%token LOOP
%token DIM

%token GE
%token LE
%token NE

%left '=' '<' '>' GE LE NE
%left '+' '-'
%left '*' '/'
%right UMINUS

%%

program
    : newlines_opt modules newlines_opt
    ;

modules
    : module
    | modules module
    ;

module
    : function
    | sub
    ;

function
    : FUNCTION header newlines statements END FUNCTION newlines_opt
    ;

sub
    : SUB header newlines statements END SUB newlines_opt
    ;

header
    : IDENT
    | IDENT '(' params_opt ')'
    ;

params_opt
    : /* empty */
    | params
    ;

params
    : param
    | params ',' param
    ;

param
    : IDENT
    | IDENT '(' IDENT ')'
    ;

statements
    : /* empty */
    | statements statement newlines
    ;

statement
    : assignment
    | dim_stmt
    | if_stmt
    | for_stmt
    | do_stmt
    | call_stmt
    ;

assignment
    : variable '=' expr
    ;

dim_stmt
    : DIM IDENT '(' expr ')'
    ;

if_stmt
    : IF expr THEN newlines statements END IF
    | IF expr THEN newlines statements ELSE newlines statements END IF
    ;

for_stmt
    : FOR variable '=' expr TO expr newlines statements NEXT variable
    ;

do_stmt
    : DO newlines statements LOOP
    | DO WHILE expr newlines statements LOOP
    | DO UNTIL expr newlines statements LOOP
    | DO newlines statements LOOP WHILE expr
    | DO newlines statements LOOP UNTIL expr
    ;

call_stmt
    : variable
    ;

variable
    : IDENT
    | IDENT '(' args_opt ')'
    ;

args_opt
    : /* empty */
    | args
    ;

args
    : expr
    | args ',' expr
    ;

expr
    : variable
    | NUMBER
    | STRING
    | '(' expr ')'
    | '-' expr %prec UMINUS
    | expr '+' expr
    | expr '-' expr
    | expr '*' expr
    | expr '/' expr
    | expr '=' expr
    | expr '<' expr
    | expr '>' expr
    | expr GE expr
    | expr LE expr
    | expr NE expr
    ;

newlines_opt
    : /* empty */
    | newlines
    ;

newlines
    : NEWLINE
    | newlines NEWLINE
    ;

%%

int yylex(void)
{
    return 0;
}

void yyerror(const char *msg)
{
    fprintf(stderr, "syntax error: %s\n", msg);
}

int main(void)
{
    return yyparse();
}
```
