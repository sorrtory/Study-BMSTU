% Лабораторная работа № 0.0. Знакомство с компиляцией программ
% 9 февраля 2026 г.
% Александр Федуков, ИУ9-62Б

# Цель работы

Заполнить первую лабораторную, которая проводится до лекции😉.

# Индивидуальный вариант

Грамматика:

```
<Program> ::= <Articles> <Body> .
<Articles> ::= <Article> <Articles> | .

<Article>  ::= define word <Body> end .
<Body>     ::= if <Body> <ElsePart> endif <Body>
             | integer <Body> | word <Body> | .
<ElsePart> ::= else <Body> | .
```

# Реализация

```python
import re

def parse(src: str):
    # split by whitespace
    raw = re.findall(r"\S+", src)
    # convert to int when possible or keep as string
    tokens = [int(t) if re.fullmatch(r"[+-]?\d+", t) else t for t in raw]

    KW = {"define", "end", "if", "else", "endif"}

    # articles dict + main program body
    articles = {}
    main_body = []

    # Stack of frames describing where we are
    # Frame formats:
    #   ("body", body_list)                         -- generic sequence container
    #   ("define", name, body_list)                 -- inside define ... end
    #   ("if", then_list, else_list_or_None)        -- inside if ... [else ...] endif

    stack = [("body", main_body)]

    # Use top of the stack to find the current body list
    def cur_body_list():
        kind = stack[-1][0]
        if kind == "body":
            return stack[-1][1]
        if kind == "define":
            return stack[-1][2]
        # kind == "if"
        then_list, else_list = stack[-1][1], stack[-1][2]
        return then_list if else_list is None else else_list

    def push_define(name: str):
        body = []
        stack.append(("define", name, body))

    def push_if():
        then_part = []
        stack.append(("if", then_part, None))

    def start_else():
        kind = stack[-1][0]
        if kind != "if":
            return False
        then_part, else_part = stack[-1][1], stack[-1][2]
        if else_part is not None:
            return False
        stack[-1] = ("if", then_part, [])
        return True

    def close_if():
        if stack[-1][0] != "if":
            return None
        _, then_part, else_part = stack.pop()
        node = ["if", then_part] if else_part is None else ["if", then_part, else_part]
        cur_body_list().append(node)
        return True

    def close_define():
        if stack[-1][0] != "define":
            return None
        _, name, body = stack.pop()
        articles[name] = body
        return True

    i = 0
    n = len(tokens)

    while i < n:
        t = tokens[i]

        # control words
        if t == "define":
            if stack != [("body", main_body)] or main_body:
                return None
            i += 1
            if i >= n or not isinstance(tokens[i], str) or tokens[i] in KW:
                return None
            name = tokens[i]
            push_define(name)
            i += 1
            continue

        if t == "end":
            # closes current define
            if not close_define():
                return None
            i += 1
            continue

        if t == "if":
            push_if()
            i += 1
            continue

        if t == "else":
            # must be inside if, and only once
            if not start_else():
                return None
            i += 1
            continue

        if t == "endif":
            if not close_if():
                return None
            i += 1
            continue

        # regular tokens: int or word
        if isinstance(t, int):
            cur_body_list().append(t)
            i += 1
            continue

        if isinstance(t, str):
            if t in KW:  # keywords cannot appear as regular words
                return None
            cur_body_list().append(t)
            i += 1
            continue

        return None

    # End of input: stack must be back to just main body
    if stack != [("body", main_body)]:
        return None

    return (articles, main_body)


if __name__ == "__main__":
    print(parse("define abs dup 0 < if -1 * endif end 10 abs -10 abs"))
    # ({'abs': ['dup', 0, '<', ['if', [-1, '*']]]}, [10, 'abs', -10, 'abs'])
```

# Тестирование

```
redmibook :: BMSTU-Compilers/lab0/src % python3 main.py
({'abs': ['dup', 0, '<', ['if', [-1, '*']]]}, [10, 'abs', -10, 'abs'])
```

Были также реализованы юнит тесты

```python
import unittest
from main import parse


class TestParser(unittest.TestCase):

    def test_simple_expression(self):
        result = parse("1 2 +")
        self.assertEqual(result, ({}, [1, 2, "+"]))

    def test_if_without_else(self):
        result = parse("x dup 0 swap if drop -1 endif")
        self.assertEqual(
            result,
            ({}, ["x", "dup", 0, "swap", ["if", ["drop", -1]]]),
        )

    def test_if_with_else(self):
        result = parse("x dup 0 swap if drop -1 else swap 1 + endif")
        self.assertEqual(
            result,
            ({}, ["x", "dup", 0, "swap", ["if", ["drop", -1], ["swap", 1, "+"]]]),
        )

    def test_factorial_with_exit(self):
        input_str = """define -- 1 - end
         define =0? dup 0 = end
         define =1? dup 1 = end
         define factorial
             =0? if drop 1 exit endif
             =1? if drop 1 exit endif
             dup --
             factorial
             *
         end
         0 factorial
         1 factorial
         2 factorial
         3 factorial
         4 factorial"""

        result = parse(input_str)
        self.assertEqual(
            result,
            (
                {
                    "--": [1, "-"],
                    "=0?": ["dup", 0, "="],
                    "=1?": ["dup", 1, "="],
                    "factorial": [
                        "=0?",
                        ["if", ["drop", 1, "exit"]],
                        "=1?",
                        ["if", ["drop", 1, "exit"]],
                        "dup",
                        "--",
                        "factorial",
                        "*",
                    ],
                },
                [0, "factorial", 1, "factorial", 2, "factorial", 3, "factorial", 4, "factorial"],
            ),
        )

    def test_factorial_with_nested_if_else(self):
        input_str = """define -- 1 - end
         define =0? dup 0 = end
         define =1? dup 1 = end
         define factorial
             =0? if
                 drop 1
             else =1? if
                 drop 1
             else
                 dup --
                 factorial
                 *
             endif
             endif
         end
         0 factorial
         1 factorial
         2 factorial
         3 factorial
         4 factorial"""

        result = parse(input_str)
        self.assertEqual(
            result,
            (
                {
                    "--": [1, "-"],
                    "=0?": ["dup", 0, "="],
                    "=1?": ["dup", 1, "="],
                    "factorial": [
                        "=0?",
                        [
                            "if",
                            ["drop", 1],
                            ["=1?",
                             [
                                 "if",
                                 ["drop", 1],
                                 ["dup", "--", "factorial", "*"],
                             ]
                            ],
                        ],
                    ],
                },
                [0, "factorial", 1, "factorial", 2, "factorial", 3, "factorial", 4, "factorial"],
            ),
        )

    def test_incomplete_define(self):
        result = parse("define word w1 w2 w3")
        self.assertIsNone(result)

    def test_empty_input(self):
        result = parse("")
        self.assertEqual(result, ({}, []))

    def test_only_whitespace(self):
        result = parse("   \n\t  ")
        self.assertEqual(result, ({}, []))

    def test_single_define(self):
        result = parse("define double dup + end")
        self.assertEqual(result, ({"double": ["dup", "+"]}, []))

    def test_nested_if_statements(self):
        result = parse("if if 1 endif endif")
        self.assertEqual(result, ({}, [["if", [["if", [1]]]]]))
```

Тесты пройдены успешно

```
redmibook :: BMSTU-Compilers/lab0/src % python3 -m unittest main_test.py
..........
----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK
```

# Вывод

Был реализован синтаксический анализатор. По заданной грамматике он строил синтаксическое дерево,
представленное в виде вложенных списков. В итоге получался словарь из статьи и тела программы.

Я реализовал данный парсер при помощи стека, который хранил информацию о том, где мы находимся в структуре
программы. Таким образом, при встрече ключевых слов, таких как `define`, `if`, `else`, `endif`, я помещал их в
стек и в дальнейшем разборе опирался на эту информацию для правильного построения дерева.

По сути я распознал язык при помощи DPDA. Такой подход научил меня использовать теорию формальных языков на
практике и дал понимание того, как компиляторы могут обрабатывать сложные конструкции языка программирования.
