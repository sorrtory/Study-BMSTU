% Лабораторная работа № 1.3 «Объектно-ориентированный лексический анализатор» 
% 23 марта 2026 г. 
% Александр Федуков, ИУ9-62Б

# Цель работы

Целью данной работы является приобретение навыка реализации лексического анализатора на
объектно-ориентированном языке без применения каких-либо средств автоматизации решения задачи лексического
анализа.

# Индивидуальный вариант

- Строковые литералы: ограничены апострофами, для включения апострофа в литерал он удваивается, не пересекают
  границы строк текста.
- Вещественные литералы: последовательности десятичных цифр, которые могут включать точку и предваряться
  знаком «минус».
- Идентификаторы: последовательности буквенных символов Unicode, точек и цифр, начинающиеся с буквы.

## Лексический домен для защиты

- Знаки операций состоят из знаков +, -, \*, /, =, \<, >, ! и могут состоять
- из произвольного количества этих знаков. Разделяют общую таблицу
- с идентификаторами.

# Реализация

```java
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Main {

    enum DomainTag {
        IDENT,
        FLOAT,
        STRING,
        SIGN,
        END_OF_PROGRAM
    }
    // Знаки операций состоят из знаков +, -, *, /, =, <, >, ! и могут состоять
    // из произвольного количества этих знаков. Разделяют общую таблицу
    // с идентификаторами.

    static final class Position implements Comparable<Position> {
        private final String text;
        private int line;
        private int pos;
        private int index;

        public Position(String text) {
            this.text = text;
            this.line = 1;
            this.pos = 1;
            this.index = 0;
        }

        private Position(String text, int line, int pos, int index) {
            this.text = text;
            this.line = line;
            this.pos = pos;
            this.index = index;
        }

        public int getLine() {
            return line;
        }

        public int getPos() {
            return pos;
        }

        public int getIndex() {
            return index;
        }

        public Position copy() {
            return new Position(text, line, pos, index);
        }

        public int cp() {
            return (index >= text.length()) ? -1 : text.codePointAt(index);
        }

        public boolean isEOF() {
            return cp() == -1;
        }

        public boolean isWhiteSpace() {
            return index < text.length() && Character.isWhitespace(text.codePointAt(index));
        }

        public boolean isLetter() {
            return !isEOF() && Character.isLetter(cp());
        }

        public boolean isDigit() {
            return !isEOF() && Character.isDigit(cp());
        }

        public boolean isDecimalDigit() {
            int ch = cp();
            return ch >= '0' && ch <= '9';
        }

        public boolean isSign(){
            int ch = cp();
            return ch == '+' || ch == '-' || ch == '*' || ch == '/' ||
                    ch == '=' || ch == '<' || ch == '>' || ch == '!';
        }

        public boolean isNewLine() {
            if (index >= text.length()) {
                return true;
            }
            char ch = text.charAt(index);
            if (ch == '\r' && index + 1 < text.length()) {
                return text.charAt(index + 1) == '\n';
            }
            return ch == '\n';
        }

        public void next() {
            if (index >= text.length()) {
                return;
            }

            char ch = text.charAt(index);

            if (ch == '\r') {
                index++;
                if (index < text.length() && text.charAt(index) == '\n') {
                    index++;
                }
                line++;
                pos = 1;
                return;
            }

            if (ch == '\n') {
                index++;
                line++;
                pos = 1;
                return;
            }

            int cp = text.codePointAt(index);
            index += Character.charCount(cp);
            pos++;
        }

        @Override
        public int compareTo(Position other) {
            return Integer.compare(this.index, other.index);
        }

        @Override
        public String toString() {
            return "(" + line + ", " + pos + ")";
        }
    }

    static final class Fragment {
        public final Position starting;
        public final Position following;

        public Fragment(Position starting, Position following) {
            this.starting = starting;
            this.following = following;
        }

        @Override
        public String toString() {
            return starting + "-" + following;
        }
    }

    static final class Message {
        public final boolean isError;
        public final String text;

        public Message(boolean isError, String text) {
            this.isError = isError;
            this.text = text;
        }
    }

    static final class MessageList {
        private final TreeMap<Position, Message> messages = new TreeMap<>();

        public void addError(Position coord, String text) {
            messages.put(coord.copy(), new Message(true, text));
        }

        public Iterable<Map.Entry<Position, Message>> getSorted() {
            return messages.entrySet();
        }

        public boolean isEmpty() {
            return messages.isEmpty();
        }
    }

    static final class NameDictionary {
        private final LinkedHashMap<String, Integer> nameCodes = new LinkedHashMap<>();
        private final ArrayList<String> names = new ArrayList<>();

        public int addName(String name) {
            Integer code = nameCodes.get(name);
            if (code != null) {
                return code;
            }
            int newCode = names.size();
            names.add(name);
            nameCodes.put(name, newCode);
            return newCode;
        }

        public String getName(int code) {
            return names.get(code);
        }

        public List<String> getAllNames() {
            return names;
        }
    }

    static final class Compiler {
        public final MessageList messages = new MessageList();
        public final NameDictionary names = new NameDictionary();

        public Scanner getScanner(String program) {
            return new Scanner(program, this);
        }
    }

    static abstract class Token {
        public final DomainTag tag;
        public final Fragment coords;

        protected Token(DomainTag tag, Position starting, Position following) {
            this.tag = tag;
            this.coords = new Fragment(starting, following);
        }

        public abstract String attrText();

        @Override
        public String toString() {
            String attr = attrText();
            if (attr.isEmpty()) {
                return tag + " " + coords;
            }
            return tag + " " + coords + ": " + attr;
        }
    }
    
        static final class IdentToken extends Token {
        public final int code;

        public IdentToken(int code, Position starting, Position following) {
            super(DomainTag.IDENT, starting, following);
            this.code = code;
        }

        @Override
        public String attrText() {
            return Integer.toString(code);
        }
    }

    static final class SignToken extends Token {
        public final int code;

        public SignToken(int code, Position starting, Position following) {
            super(DomainTag.SIGN, starting, following);
            this.code = code;
        }

        @Override
        public String attrText() {
            return Integer.toString(code);
        }
    }

    static final class FloatToken extends Token {
        public final double value;

        public FloatToken(double value, Position starting, Position following) {
            super(DomainTag.FLOAT, starting, following);
            this.value = value;
        }

        @Override
        public String attrText() {
            return Double.toString(value);
        }
    }

    static final class StringToken extends Token {
        public final String value;

        public StringToken(String value, Position starting, Position following) {
            super(DomainTag.STRING, starting, following);
            this.value = value;
        }

        @Override
        public String attrText() {
            return value;
        }
    }

    static final class EndToken extends Token {
        public EndToken(Position starting, Position following) {
            super(DomainTag.END_OF_PROGRAM, starting, following);
        }

        @Override
        public String attrText() {
            return "";
        }
    }

    static final class Scanner {
        private final String program;
        private final Compiler compiler;
        private final Position cur;

        public Scanner(String program, Compiler compiler) {
            this.program = program;
            this.compiler = compiler;
            this.cur = new Position(program);
        }

        public Token nextToken() {
            while (!cur.isEOF()) {
                while (cur.isWhiteSpace()) {
                    cur.next();
                }

                if (cur.isEOF()) {
                    break;
                }

                int ch = cur.cp();
                

                if (ch == '\'') {
                    return readString();
                }

                if (ch == '-' || cur.isDecimalDigit()) {
                    Token t = tryReadFloat();
                    if (t != null) {
                        return t;
                    }
                    compiler.messages.addError(cur.copy(), "unexpected character");
                    cur.next();
                    continue;
                }

                if (cur.isLetter()) {
                    return readIdent();
                }

                if (cur.isSign()) {
                    return readSign();
                }

                compiler.messages.addError(cur.copy(), "unexpected character");
                cur.next();
            }

            return new EndToken(cur.copy(), cur.copy());
        }

        private SignToken readSign() {
            Position start = cur.copy();
            StringBuilder sb = new StringBuilder();

            while (cur.isSign()) {
                sb.appendCodePoint(cur.cp());
                cur.next();
            }

            int code = compiler.names.addName(sb.toString());
            return new SignToken(code, start, cur.copy());
        }

        private IdentToken readIdent() {
            Position start = cur.copy();
            StringBuilder sb = new StringBuilder();

            sb.appendCodePoint(cur.cp());
            cur.next();

            while (cur.isLetter() || cur.isDigit() || cur.cp() == '.') {
                sb.appendCodePoint(cur.cp());
                cur.next();
            }

            int code = compiler.names.addName(sb.toString());
            return new IdentToken(code, start, cur.copy());
        }

        private Token tryReadFloat() {
            Position start = cur.copy();
            StringBuilder raw = new StringBuilder();

            if (cur.cp() == '-') {
                int next = peekNextCodePoint();
                
                Position new_pos = cur.copy();
                new_pos.next();

                if (new_pos.isSign()) {
                    return readSign();
                }
                
                if (!isDecimalDigit(next)) {
                    return null;
                }
                raw.append('-');
                cur.next();
            }

            if (!cur.isDecimalDigit()) {
                return null;
            }

            while (cur.isDecimalDigit()) {
                raw.append((char) cur.cp());
                cur.next();
            }

            if (cur.cp() == '.' && isDecimalDigit(peekNextCodePoint())) {
                raw.append('.');
                cur.next();

                while (cur.isDecimalDigit()) {
                    raw.append((char) cur.cp());
                    cur.next();
                }
            }

            double value;
            try {
                value = Double.parseDouble(raw.toString());
                if (Double.isInfinite(value)) {
                    compiler.messages.addError(start, "floating constant is too large");
                    value = 0.0;
                }
            } catch (NumberFormatException e) {
                compiler.messages.addError(start, "bad floating constant");
                value = 0.0;
            }

            return new FloatToken(value, start, cur.copy());
        }

        private StringToken readString() {
            Position start = cur.copy();
            StringBuilder value = new StringBuilder();

            cur.next(); // пропускаем открывающий апостроф

            while (true) {
                if (cur.isEOF()) {
                    compiler.messages.addError(cur.copy(),
                            "end of program found, closing apostrophe expected");
                    return new StringToken(value.toString(), start, cur.copy());
                }

                if (cur.isNewLine()) {
                    compiler.messages.addError(cur.copy(), "newline in string literal");
                    return new StringToken(value.toString(), start, cur.copy());
                }

                if (cur.cp() == '\'') {
                    cur.next(); // съели апостроф

                    if (cur.cp() == '\'') {
                        value.append('\''); // удвоенный апостроф внутри строки
                        cur.next();
                        continue;
                    }

                    // это был закрывающий апостроф
                    return new StringToken(value.toString(), start, cur.copy());
                }

                value.appendCodePoint(cur.cp());
                cur.next();
            }
        }

        private int peekNextCodePoint() {
            if (cur.isEOF()) {
                return -1;
            }
            int nextIndex = cur.getIndex() + Character.charCount(cur.cp());
            return (nextIndex >= program.length()) ? -1 : program.codePointAt(nextIndex);
        }

        private boolean isDecimalDigit(int cp) {
            return cp >= '0' && cp <= '9';
        }
    }

    public static void main(String[] args) {
        String inputFile = "../assets/input.txt";
        if (args.length > 0) {
            inputFile = args[0];
        }

        try {
            String program = Files.readString(Path.of(inputFile), StandardCharsets.UTF_8);

            Compiler compiler = new Compiler();
            Scanner scanner = compiler.getScanner(program);

            while (true) {
                Token t = scanner.nextToken();
                if (t.tag == DomainTag.END_OF_PROGRAM) {
                    break;
                }
                System.out.println(t);
            }

            if (!compiler.messages.isEmpty()) {
                System.out.println("MESSAGES:");
                for (Map.Entry<Position, Message> e : compiler.messages.getSorted()) {
                    System.out.printf("%s %s: %s%n",
                            e.getValue().isError ? "Error" : "Warning",
                            e.getKey(),
                            e.getValue().text);
                }
            }

        } catch (IOException e) {
            System.err.println("Не удалось прочитать файл: " + inputFile);
            System.err.println("Текущая директория: " + Path.of("").toAbsolutePath());
        }
    }
}
```

# Тестирование

Входные данные

```
abc
Привет123
A.b.2
переменная.7
abc
123
-456
12.34
-0.75
'hello'
'don''t'
'строка с пробелами'
abc123'qq'
-
.
'not closed
12.
.5
@


+++++++++

+-= +-= <+> <+>
```

Вывод на `stdout`

```
IDENT (1, 1)-(1, 4): 0
IDENT (2, 1)-(2, 10): 1
IDENT (3, 1)-(3, 6): 2
IDENT (4, 1)-(4, 13): 3
IDENT (5, 1)-(5, 4): 0
FLOAT (6, 1)-(6, 4): 123.0
FLOAT (7, 1)-(7, 5): -456.0
FLOAT (8, 1)-(8, 6): 12.34
FLOAT (9, 1)-(9, 6): -0.75
STRING (10, 1)-(10, 8): hello
STRING (11, 1)-(11, 9): don't
STRING (12, 1)-(12, 21): строка с пробелами
IDENT (13, 1)-(13, 7): 4
STRING (13, 7)-(13, 11): qq
STRING (16, 1)-(16, 12): not closed
FLOAT (17, 1)-(17, 3): 12.0
FLOAT (18, 2)-(18, 3): 5.0
SIGN (22, 1)-(22, 10): 5
SIGN (24, 1)-(24, 4): 6
SIGN (24, 5)-(24, 8): 6
SIGN (24, 9)-(24, 12): 7
SIGN (24, 13)-(24, 16): 7
MESSAGES:
Error (14, 1): unexpected character
Error (15, 1): unexpected character
Error (16, 12): newline in string literal
Error (17, 3): unexpected character
Error (18, 1): unexpected character
Error (19, 1): unexpected character
```

# Вывод

В ходе лабораторной работы был реализован объектно-ориентированный лексический анализатор. Были описаны и
обработаны основные лексические домены: идентификаторы, вещественные литералы, строковые литералы и знаки
операций. Программа сохраняет найденные лексемы, их атрибуты и координаты, а также выводит сообщения об
ошибках.
