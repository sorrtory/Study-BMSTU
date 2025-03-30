#ifndef PARSER_H
#define    PARSER_H

#include <string>

namespace parser {

// Координаты в тексте
    struct coord {
        int offs; // смещение относительно начала
    };

// parse выполняет синтаксический анализ текста по грамматике:
//
//   <Expr> ::= <Term> <Expr> | ε.
//   <Term> ::= IDENT | NUMBER | LPAREN <Expr> RPAREN.
//
//	<Call> ::= IDENT ( <Args> )
//	| IDENT ( )
//	| NUMBER
//	<Args> ::= <Call> , <Args> | <Call>
//
//
// Здесь IDENT -- непустая последовательность букв и цифр, начинающаяся с буквы;
//       NUMBER -- непустая последовательность цифр;
//       LPAREN и RPAREN -- круглые скобки.
//
// В случае обнаружения синтаксической ошибки порождается исключение
// типа coord, в котором записаны координаты ошибки в тексте.
    void parse(std::string text) throw(coord);

}

#endif	/* PARSER_H */