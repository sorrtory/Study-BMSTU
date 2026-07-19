import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import main  # noqa: E402


def check(source: str) -> main.Program:
    tree = main.build_parser().parse(source)
    tree.check()
    return tree


class SemanticAnalysisTests(unittest.TestCase):
    def assert_error(self, source: str, message: str) -> None:
        with self.assertRaises(main.SemanticError) as error:
            check(source)
        self.assertIn(message, error.exception.message)

    def test_computes_constants_and_type_sizes(self) -> None:
        tree = check(
            """
            const Limit = 3;
            type
              Color = (red, green, blue);
              Values = array 1..Limit of Color;
              Flags = set of Color;
              Node = record value: Values; next: ^Node end;
            """
        )

        self.assertEqual(
            [(symbol.name, symbol.value) for symbol in tree.constants],
            [("LIMIT", 3), ("RED", 0), ("GREEN", 1), ("BLUE", 2)],
        )
        self.assertEqual(
            {symbol.name: symbol.type_info.size for symbol in tree.types},
            {"COLOR": 2, "VALUES": 6, "FLAGS": 1, "NODE": 10},
        )

    def test_computes_variant_record_size(self) -> None:
        tree = check(
            """
            type
              Kind = (small, large);
              Item = record fixed: INTEGER; case tag: Kind of
                small: (letter: CHAR);
                large: (number: REAL)
              end;
            """
        )

        sizes = {symbol.name: symbol.type_info.size for symbol in tree.types}
        self.assertEqual(sizes["ITEM"], 8)

    def test_rejects_unknown_identifier_used_before_declaration(self) -> None:
        self.assert_error(
            "type First = Second; Second = INTEGER;",
            "Имя SECOND не определено выше по тексту",
        )

    def test_rejects_shared_type_and_const_name(self) -> None:
        self.assert_error(
            "const Answer = 42; type Answer = INTEGER;",
            "Повторное объявление имени ANSWER",
        )

    def test_rejects_duplicate_enum_constant(self) -> None:
        self.assert_error(
            "const Red = 1; type Color = (red, green);",
            "Повторное объявление имени RED",
        )

    def test_rejects_duplicate_record_field(self) -> None:
        self.assert_error(
            "type Pair = record x: INTEGER; x: REAL end;",
            "Повторное поле X",
        )

    def test_rejects_inverted_range(self) -> None:
        self.assert_error(
            "type Broken = 10..1;",
            "Левая граница диапазона 10 больше правой 1",
        )


if __name__ == "__main__":
    unittest.main()
