Поставил джаву и настроил IDE

Читал лекции и условие, понял, что нужно написать лексический анализатор и +- что это такое.

Научился читать файлы

```java
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class ReadFileTest {
    private static final String INPUT_FILE = "lab3/assets/input.txt";

    public static void main(String[] args) {
        try {
            String text = Files.readString(Path.of(INPUT_FILE), StandardCharsets.UTF_8);
            System.out.println("=== FILE: " + INPUT_FILE + " ===");
            System.out.println(text);
        } catch (IOException e) {
            System.err.println("Не удалось прочитать файл: " + INPUT_FILE);
            System.err.println("Текущая директория: " + Path.of("").toAbsolutePath());
        }
    }
}
```

Как я понимаю дальше надо написать код, который через регулярные выражения будет распознавать лексические домены. Причем надо поставить их в определенном порядке, чтобы соблюдать приоритет.
