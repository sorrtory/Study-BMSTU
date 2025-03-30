#include <cctype>
#include <iostream>
#include "parser.h"

namespace parser {

// Теги лексем
    enum tag_t {
        IDENT, NUMBER, LPAREN, RPAREN, END, COMMA
    };

// Контекст парсера
    struct context {
        std::string text;  // текст для анализа
        coord cur;         // координаты текущей позиции в тексте
        coord next;        // координаты следующей позиции в тексте
        coord start;       // координаты начала текущей лексемы
        tag_t tag;         // тег текущей лексемы
    };

// next_char считывает следующий символ из текста и возвращает его код.
// Если достигнут конец текста, next_char возвращает -1.
    int next_char(context &ctx) {
        ctx.cur = ctx.next;
        if (ctx.next.offs == ctx.text.length()) return -1;
        return ctx.text[ctx.next.offs++];
    }

// next_token распознаёт следующую лексему в тексте.
    void next_token(context &ctx) throw(coord) {
        int c;
        while (isspace(c = next_char(ctx)));

        ctx.start = ctx.cur;
        switch (c) {
            case -1:
                ctx.tag = END;
                break;
            case '(':
                ctx.tag = LPAREN;
                break;
            case ')':
                ctx.tag = RPAREN;
                break;
            case ',':
                ctx.tag = COMMA;
                break;
            default:
                if (isalpha(c)) {
                    while (isalnum(c = next_char(ctx)));
                    ctx.tag = IDENT;
                    ctx.next.offs--;
                } else if (isdigit(c)) {
                    while (isdigit(c = next_char(ctx)));
                    ctx.tag = NUMBER;
                    ctx.next.offs--;
                } else {
                    throw ctx.cur;
                }
        }
    }

    void parse_expr(context &) throw(coord);

    void parse_term(context &) throw(coord);

    void parse(std::string text) throw(coord) {
        context ctx{text};
        ctx.next = coord{0};
        next_token(ctx);
        parse_expr(ctx);
        if (ctx.tag != END) throw ctx.start;
    }

    void parse_expr(context &ctx) throw(coord) {
        if (ctx.tag == IDENT || ctx.tag == NUMBER || ctx.tag == LPAREN || ctx.tag == COMMA) {
            parse_term(ctx);
            parse_expr(ctx);
        }
    }

    void parse_term(context &ctx) throw(coord) {
        switch (ctx.tag) {
            case COMMA:
                next_token(ctx);
                if (ctx.tag != NUMBER && ctx.tag != IDENT) throw ctx.start;
                break;
            case IDENT:
                next_token(ctx);
                if (ctx.tag != LPAREN) throw ctx.start; // проверить ctx
                break;
            case NUMBER:
                next_token(ctx);
                break;
            case LPAREN:
                next_token(ctx);
                parse_expr(ctx);
                if (ctx.tag != RPAREN) throw ctx.start;
                next_token(ctx);
                break;
        }
    }

}