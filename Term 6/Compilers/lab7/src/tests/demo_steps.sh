#!/usr/bin/env bash

set -u

cd "$(dirname "$0")/.."

section() {
  printf '\n===== %s =====\n' "$1"
}

run() {
  printf '\n$ %s\n' "$*"
  "$@"
}

section "API generator.py"
run python3 generator.py --help

section "Грамматика входного языка генератора"
run cat generator_grammar.txt

section "Первый запуск: ручная таблица из 2.3"
run python3 generator.py \
  generator_grammar.txt \
  generated/generated_input_table.py \
  --mode enum \
  --sets

section "Второй запуск: уже сгенерированная таблица"
run python3 generator.py \
  generator_grammar.txt \
  generated/generated_input_table_2.py \
  --mode enum \
  --bootstrap-table generated/generated_input_table.py

section "Грамматика калькулятора"
run cat calculator/arithmetic_grammar.txt

section "Генерация таблицы калькулятора"
run python3 generator.py \
  calculator/arithmetic_grammar.txt \
  generated/calc_table.py \
  --mode string \
  --sets

section "Запуск калькулятора"
printf '(2+3)*4\n' | python3 -m calculator.calculator


section "Ошибка: грамматика не LL(1)"
printf '`axiom S `is "a" `or "a" "b" `end\n' > /tmp/not_ll1_demo.txt
if ! run python3 generator.py /tmp/not_ll1_demo.txt /tmp/not_ll1_table.py --mode string; then
  printf 'Это ожидаемая ошибка: таблица для такой грамматики не строится.\n'
fi
