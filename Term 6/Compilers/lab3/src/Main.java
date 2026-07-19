import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Main {

    enum DomainTag {
        IF,
        GOTO,
        INT_IDENT,
        FLOAT_IDENT,
        NUMBER,
        PLUS,
        COMMA,
        E_NUMBER,
        END_OF_PROGRAM
    }

    static class Position {
        private final String text;
        private int index;
        private int line;
        private int pos;

        public Position(String text) {
            this.text = text;
            this.index = 0;
            this.line = 1;
            this.pos = 1;
        }

        private Position(String text, int index, int line, int pos) {
            this.text = text;
            this.index = index;
            this.line = line;
            this.pos = pos;
        }

        public int getIndex() {
            return index;
        }

        public int getLine() {
            return line;
        }

        public int getPos() {
            return pos;
        }

        public Position copy() {
            return new Position(text, index, line, pos);
        }

        // текущая кодовая точка; -1 == конец файла
        public int cp() {
            if (index >= text.length()) {
                return -1;
            }
            return text.codePointAt(index);
        }

        public boolean isEOF() {
            return cp() == -1;
        }

        public boolean isWhiteSpace() {
            int ch = cp();
            return ch != -1 && Character.isWhitespace(ch);
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
        public String toString() {
            return "(" + line + ", " + pos + ")";
        }
    }

    static class Fragment {
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

    static class Token {
        public final DomainTag tag;
        public final Fragment coords;
        public final String lexeme;

        public Token(DomainTag tag, Position start, Position follow, String lexeme) {
            this.tag = tag;
            this.coords = new Fragment(start, follow);
            this.lexeme = lexeme;
        }
    }

    static class Domain {
        public final DomainTag tag;
        public final Pattern pattern;

        public Domain(DomainTag tag, Pattern pattern) {
            this.tag = tag;
            this.pattern = pattern;
        }
    }

    // приоритет задается порядком (раньше - выше)
    static final Domain[] DOMAINS = {
            new Domain(DomainTag.IF,
                    Pattern.compile("\\AIF", Pattern.CASE_INSENSITIVE)),
            new Domain(DomainTag.GOTO,
                    Pattern.compile("\\AGOTO", Pattern.CASE_INSENSITIVE)),

            // Целочисленные переменные: начинаются с буквы «I», «J», «K», «L», «M» или «N»,
            // за которой может следовать не более пяти латинских букв и цифр, не
            // чувствительны к регистру.
            new Domain(DomainTag.INT_IDENT,
                    Pattern.compile("\\A[I-Ni-n](?:[ \\t]*[A-Za-z0-9]){0,5}")),

            // Вещественные переменные начинаются с любой другой буквы, за которой может
            // следовать не более пяти латинских букв и цифр.
            new Domain(DomainTag.FLOAT_IDENT,
                    Pattern.compile("\\A[A-HO-Za-ho-z](?:[ \\t]*[A-Za-z0-9]){0,5}")),

            // Целые числа - последовательности десятичных цифр, могут начинаться с нуля.
            new Domain(DomainTag.NUMBER,
                    Pattern.compile("\\A\\d(?:[ \\t]*\\d)*")),

            // Вещественные числа - содержат необязательную дробную часть
            // и необязательный порядок: 3.1415, 3e8, 6.022e23, 1.38e-23
            // Порядок может содержать минус. Пробелы тоже допустимы везде:
            // 1.38 e -23
            new Domain(DomainTag.E_NUMBER,
                    Pattern.compile(
                        "\\A\\d(?:[ \\t]*\\d)*"
                        + "(?:[ \\t]*\\.(?:[ \\t]*\\d)+)?"
                        + "(?:[ \\t]*e[ \\t]*-?(?:[ \\t]*\\d)+)?")),


            new Domain(DomainTag.PLUS, Pattern.compile("\\A\\+")),
            new Domain(DomainTag.COMMA, Pattern.compile("\\A,"))
    };

    static class Scanner {
        private final String program;
        private final Position cur;

        public Scanner(String program) {
            this.program = program;
            this.cur = new Position(program);
        }

        public Token nextToken() {
            while (!cur.isEOF()) {
                skipOuterWhitespace();

                if (cur.isEOF()) {
                    break;
                }

                Position start = cur.copy();
                Match best = findBestMatch();

                if (best != null) {
                    advanceByRawText(best.lexeme);
                    return new Token(best.domain.tag, start, cur.copy(), best.lexeme);
                }

                // ошибка + восстановление
                System.out.printf("syntax error (%d,%d)%n", cur.getLine(), cur.getPos());
                recover();
            }

            return new Token(DomainTag.END_OF_PROGRAM, cur.copy(), cur.copy(), "");
        }

        private void skipOuterWhitespace() {
            while (cur.isWhiteSpace()) {
                cur.next();
            }
        }

        private Match findBestMatch() {
            String rest = program.substring(cur.getIndex());

            Domain bestDomain = null;
            String bestLexeme = null;
            int bestLength = -1;

            for (Domain d : DOMAINS) {
                Matcher m = d.pattern.matcher(rest);
                if (m.find()) {
                    String lexeme = m.group();
                    int len = lexeme.length();

                    // сначала максимальная длина
                    // потом приоритет домена
                    // (чем раньше в массиве, тем выше приоритет)
                    if (len > bestLength) {
                        bestLength = len;
                        bestDomain = d;
                        bestLexeme = lexeme;
                    }
                }
            }

            if (bestDomain == null) {
                return null;
            }

            return new Match(bestDomain, bestLexeme);
        }

        private void recover() {
            while (!cur.isEOF()) {
                if (cur.isWhiteSpace()) {
                    skipOuterWhitespace();
                    if (findBestMatch() != null) {
                        return;
                    }
                } else {
                    if (findBestMatch() != null) {
                        return;
                    }
                    cur.next();
                }
            }
        }

        private void advanceByRawText(String raw) {
            int i = 0;
            while (i < raw.length()) {
                int ch = raw.codePointAt(i);

                if (ch == '\r') {
                    cur.next();
                    i++;
                } else if (ch == '\n') {
                    cur.next();
                    i++;
                } else {
                    cur.next();
                    i += Character.charCount(ch);
                }
            }
        }

        private static class Match {
            final Domain domain;
            final String lexeme;

            Match(Domain domain, String lexeme) {
                this.domain = domain;
                this.lexeme = lexeme;
            }
        }
    }

    public static void main(String[] args) {
        String inputFile = "../assets/input.txt";
        if (args.length > 0) {
            inputFile = args[0];
        }

        try {
            String program = Files.readString(Path.of(inputFile), StandardCharsets.UTF_8);

            Scanner scanner = new Scanner(program);

            while (true) {
                Token t = scanner.nextToken();
                if (t.tag == DomainTag.END_OF_PROGRAM) {
                    break;
                }

                System.out.printf("%s (%d, %d): %s%n",
                        t.tag,
                        t.coords.starting.getLine(),
                        t.coords.starting.getPos(),
                        t.lexeme);
            }

        } catch (IOException e) {
            System.err.println("Не удалось прочитать файл: " + inputFile);
            System.err.println("Текущая директория: " + Path.of("").toAbsolutePath());
        }
    }
}