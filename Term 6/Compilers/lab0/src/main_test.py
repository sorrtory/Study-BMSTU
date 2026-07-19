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
