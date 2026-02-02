# Lab 1

## Условие

По имеющейся SRS определить:

- завершимость
- конечность классов эквивалентности по НФ (для построения эквивалент-
  ностей считаем, что правила могут применяться в обе стороны). Если их
  конечное число, то построить минимальную систему переписывания, им
  соответствующую.
- локальную конфлюэнтность и пополняемость по Кнуту-Бендиксу

### Исходная система переписывания

```math
\left\{ \begin{aligned}

    aabc  &\rightarrow bbaa \\
    b  &\rightarrow ccaa \\
    bc  &\rightarrow a \\
    aac  &\rightarrow ε \\

\end{aligned} \right.
```

## Решение

### Завершимость

1. Используя [AProVE](https://aprove.informatik.rwth-aachen.de/interface/v-AProVE2023/srs_wst), проверяем систему на завершимость

```
(RULES
    a a b c -> b b a a ,
    b -> c c a a ,
    b c -> a ,
    a a c ->
)
```

Калькулятор, через матричную интерпретацию a, b, c, используя натуральные числа с минус бесконечностью,
доказывает, что система завершается.

2. Используя метод проб и ошибок, введем следующий порядок $\succ_{\text{L}}$:

- Количество букв $b$
- Длина слова

Проверим каждое правило на уменьшение в этом порядке:

```math
\left\{
\begin{aligned}

aabc &\rightarrow bbaa; \quad
\left(aa\underline{b}c \prec_{\text{L}} \underline{bb}aa \right) \Rightarrow Увеличивается \\

b &\rightarrow ccaa; \quad
\left(\underline{b} \succ_{\text{L}} ccaa \right) \Rightarrow Уменьшается \\

bc &\rightarrow a; \quad
\left(\underline{b}c \succ_{\text{L}} a \right) \Rightarrow Уменьшается \\

aac &\rightarrow \varepsilon; \quad
\left(aaс \succ_{\text{L}} \varepsilon \right) \Rightarrow Уменьшается \\


\end{aligned}
\right.
```

Заметим, что правило $aabc \rightarrow bbaa$ увеличивает слово в порядке $\succ_{\text{L}}$.

Найдем все нормальные формы слова $aabc$:

```mermaid
stateDiagram-v2
    aabc --> bbaa : aabc -> bbaa
        bbaa --> ccaabaa : b -> ccaa
            ccaabaa --> ccaaccaaaa : b -> ccaa
                ccaaccaaaa --> cccaaaa : aac -> ε
                    note right of cccaaaa: НФ
        bbaa --> bccaaaa : b -> ccaa
            bccaaaa --> acaaaa : bc -> a
                note right of acaaaa: НФ
            bccaaaa --> ccaaccaaa : b -> ccaa
                ccaaccaaa --> cccaaaa : aac -> ε

    aabc --> aaa : bc -> a
        note right of aaa: НФ

    aabc --> aaccaac : b -> ccaa
        aaccaac --> c : aac -> ε
            note right of c: НФ
```

Рассмотрим теперь нормальные формы слова $aabc$ в порядке $\succ_{\text{L}}$ относительно него самого:

- $aa\underline{b}c \succ_{\text{L}} aaa$
- $aa\underline{b}c \succ_{\text{L}} c$
- $aa\underline{b}c \succ_{\text{L}} acaaaa$
- $aa\underline{b}c \succ_{\text{L}} cccaaaa$

Таким образом все нормальные формы слова $aabc$ меньше самого слова $aabc$ в порядке $\succ_{\text{L}}$. Что значит, что правило $aabc \rightarrow bbaa$ также уменьшает порядок.

Соответственно все правила уменьшают порядок $\succ_{\text{L}}$, который бесконечно уменьшаться не может, а значит наша система завершается.

### Локальная конфлюэнтность и пополняемость по Кнуту-Бендиксу

#### Shortlex

Переориентируем правила в порядке shortlex для фундированности
(сначала по длине, затем по алфавиту: $a < b < c$):

```math
\left\{
\begin{aligned}
&bbaa \rightarrow aabc (*) \\
&ccaa \rightarrow b  (*) \\
&bc \rightarrow a \\
&aac \rightarrow \epsilon \\
\end{aligned}
\right.
```

Запустим [алгоритм Кнуту-Бендикса](./solution/src/bin/kb.rs) на переориентированной системе

#### Локальная конфлюентность

Программа разбирет критические пары и добавит недостающие правила.

Например для слова $bccaa$ добавится правило $acaa \rightarrow bb$:

```mermaid
stateDiagram-v2
    %% Diagram: processing bccaa
    bccaa --> acaa : bc -> a
        note right of acaa: НФ
    bccaa --> bb : ccaa -> b
        note right of bb: НФ
```

#### Пополняемость по Кнуту-Бендиксу

В итоге получим такую систему переписывания:

```math
\left\{
\begin{aligned}
&bbaa \rightarrow aabc \\
&ccaa \rightarrow b \\
&bc \rightarrow a \\
&aac \rightarrow \epsilon \\
\\[2ex]
&c \rightarrow b \\
&ac \rightarrow ab \\
&ba \rightarrow ab \\
&bb \rightarrow a \\
&ca \rightarrow ab \\
&cb \rightarrow a \\
&aaa \rightarrow b \\
&aab \rightarrow \epsilon \\
&caa \rightarrow aab \\
&cab \rightarrow aa \\
&cca \rightarrow cab \\
&ccb \rightarrow ca \\
&aaaa \rightarrow ab \\
&aaab \rightarrow a \\
&acaa \rightarrow bb \\
&ccab \rightarrow aab \\
&aaaaa \rightarrow aab \\
&aaaab \rightarrow aa \\
&aaaaab \rightarrow aaa \\
\end{aligned}
\right.
```

#### Конечность классов эквивалентности по НФ

Используя эквивалентну систему переписывания, наконец
найдем нормальные формы при помощи программы [перебора слов](src/bin/auto.rs)

```bash
# Меняя длину рекурсии DEPTH с с 10, на 20 ничего не меняется,
# так что это конечный набор нормальных форм
cargo run --bin auto | grep "RESULTING NORMAL FORMS"
```

```
Normal forms: {b, aa, ab, a, ε}
```

### Минимизация

Используя нормальные формы и то что напринтила программа перебора,
строим минимальный автомат переходов между нормальными формами:

```bash
cargo run --bin auto > out

grep -w "WORD a" out
grep -w "WORD b" out
grep -w "WORD c" out

grep -w "WORD aa" out
grep -w "WORD ab" out
grep -w "WORD ac" out

grep -w "WORD ba" out
grep -w "WORD bb" out
grep -w "WORD bc" out

grep -w "WORD aaa" out
grep -w "WORD aab" out
grep -w "WORD aac" out

grep -w "WORD aba" out
grep -w "WORD abb" out
grep -w "WORD abc" out
```

```mermaid
stateDiagram-v2
    [*] --> ε
    ε --> a : a
    ε --> b : b
    ε --> b : c %% c -> b

    %% a + a == aa
    %% a + c != ab => New rule: ac -> ab
    a --> aa : a
    a --> ab : b
    a --> ab : c %% ac -> ab

    b --> ab : a %% ba -> ab
    b --> a : b  %% bb -> a
    b --> a : c  %% bc -> a

    aa --> b : a %% aaa -> b
    aa --> ε : b %% aab -> ε
    aa --> ε : c %% aac -> ε

    ab --> ε : a %% aba -> ε
    ab --> aa : b %% abb -> aa
    ab --> aa : c %% abc -> aa
```

Построим соответствующую систему переписывания, беря правила из автомата
(то есть берем все стрелки, которые не ведут себя в соответствии с добавляемыми буквами)

Пример добавление правила:

- $a \xrightarrow{a} aa \quad$ - ожидаемое поведение.
- $a \xrightarrow{c} ab \quad$ - необычное поведение, так как добавление $a$ к $a$ должно вести к $aa$, а не к $ab$). Следовательно, добавляем правило $ac \rightarrow ab$.

Продолжая этот процесс, получаем следующую систему переписывания:

```math
\left\{
\begin{aligned}
    &c \rightarrow b \\
    &ac \rightarrow ab \\
    &ba \rightarrow ab \\
    &bb \rightarrow a \\
    &bc \rightarrow a \\
    &aaa \rightarrow b \\
    &aab \rightarrow \varepsilon \\
    &aac \rightarrow \varepsilon \\
    &aba \rightarrow \varepsilon \\
    &abb \rightarrow aa \\
    &abc \rightarrow aa \\
\end{aligned}
\right.
```

Удаляем лишние, включающие в себя другие, правила, оставляя только минимальный набор. Для этого пойдем от ε и будем добавлять по одной букве, строя стрелки по уже известным правилам.

Итоговый минимальный автомат

```mermaid
stateDiagram-v2
    [*] --> ε
    ε --> a : a
    ε --> b : b
    ε --> b : c %% c -> b

    %% a + a == aa
    %% a + c != ab => New rule: ac -> ab
    a --> aa : a
    a --> ab : b

    b --> ab : a %% ba -> ab
    b --> a : b  %% bb -> a

    aa --> b : a %% aaa -> b
    aa --> ε : b %% aab -> ε

```

Соответствующая минимальная система переписывания:

```math
\left\{
\begin{aligned}
    &c \rightarrow b \\
    &ba \rightarrow ab \\
    &bb \rightarrow a \\
    &aaa \rightarrow b \\
    &aab \rightarrow \varepsilon \\
\end{aligned}
\right.
```

## Тестирование

Перейдем в папку решения

```bash
cd lab1/solution
```

## Фаззинг

```bash
cargo run --bin fuzz
```

Пример вывода программы фаззинг тестирования:

```
...
Applying rule b -> aaa on bbbabcbbb with result {bbbaaaacbbb, baaababcbbb, bbaaaabcbbb, bbbabcaaabb, bbbabcbaaab, bbbabcbbaaa, aaabbabcbbb}
Applying rule ab -> ba on bbbabcbbb with result {bbbbacbbb}
Checking normal form ababbbbb in second SRS: true
Fuzz test passed for input bcbabbbbb
Fuzz test completed
```

## Инварианты

```bash
cargo run --bin inv
```

Пример вывода программы тестирования инвариантов:

```
...
GetNormalForms: Current string: babababcc
GetNormalForms: Normal forms so far: {a}
Calculating inv2 for a: 0
--- Inv3 ---
Calculating inv3 for cabbaabcc: false
Word cabbaabcc violates inv3, skipping further checks.
---
All invariant equivalence tests passed

```

### Гомоморфизм в циклическую группу порядка 5

Возьмём инвариант, который сохраняет считает количество букв с таким весами:

```
h(a) = 2
h(b) = 1
h(c) = 1
```

Тогда для любого слова $s$ определим инвариант:

$I(s) = 2 \cdot |s|_a + |s|_b + |s|_c \bmod 5$

### Отсутствие подстроки $ccc$

Если строка изначально не содержит подстроку $ccc$, то и после применения любых правил она не будет её содержать.

### Максимальная глубина вложенности

Если рассматривать $a$ как открывающую скобку, $b$ как двойную открывающую скобку, а $c$ как закрывающую скобку, то можно ввести инвариант максимальной глубины вложенности скобок.

- a увеличивает глубину на 1
- b увеличивает глубину на 2
- c уменьшает глубину на 1

Тогда максимальная глубина вложенности строки (читая ее слева направо) не может превышать 3
