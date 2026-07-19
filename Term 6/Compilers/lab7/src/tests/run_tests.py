import filecmp
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
PYTHON = sys.executable
sys.path.insert(0, ROOT)


def run(args):
    print("$", " ".join(args))
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    if result.returncode != 0:
        raise SystemExit(result.returncode)


run([PYTHON, "generator.py", "generator_grammar.txt", "generated/generated_input_table.py", "--mode", "enum"])
run([PYTHON, "generator.py", "generator_grammar.txt", "generated/generated_input_table_2.py", "--mode", "enum", "--bootstrap-table", "generated/generated_input_table.py"])
same_generated_tables = filecmp.cmp(
    os.path.join(ROOT, "generated", "generated_input_table.py"),
    os.path.join(ROOT, "generated", "generated_input_table_2.py"),
    shallow=False,
)
print("Self-application table equality:", same_generated_tables)
assert same_generated_tables

from generated.generated_input_table import PARSE_TABLE as GENERATED_INPUT_TABLE
from grammar_parser import build_manual_table

same_as_manual_table = build_manual_table() == GENERATED_INPUT_TABLE
print("Manual table equality:", same_as_manual_table)
assert same_as_manual_table

run([PYTHON, "generator.py", "calculator/arithmetic_grammar.txt", "generated/calc_table.py", "--mode", "string"])

from calculator.calculator import calculate

for expression, expected in {
    "2+3*4": 14,
    "(2+3)*4": 20,
    "7": 7,
    "2*3+4*5": 26,
}.items():
    actual = calculate(expression)
    print(expression, "=", actual)
    assert actual == expected, (expression, actual, expected)
