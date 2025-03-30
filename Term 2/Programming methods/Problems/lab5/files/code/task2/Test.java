package task2;

/*
Множество целых чисел с операциями:
1. порождение потока таких чисел из множества,
что каждое из них равно сумме двух других чисел
множества;
2. поиск такого числа x в множестве, что все
другие числа множества, большие x, не равны
сумме двух других чисел множества;
3. добавление числа в множество.

Проверить работу второй операции нужно путём
ранжирования чисел на три группы:
отрицательные, нулевые и положительные.
*/

public class Test {
    private static String num2(SummableNumbers numbers){
        if (numbers.findSpecialX().isEmpty()){
            return "Нет такого числа";
        } else {
            return Integer.toString(numbers.findSpecialX().get());
        }
    }
    public static void main(String[] args) {
        SummableNumbers numbers = new SummableNumbers(new int[]{1, 2, 3, -15, -1, -2});

        System.out.println("1) Суммы последовательности:");
        System.out.println(numbers.sumsStream().toList());
//        numbers.sort(); // Не работает сортировка почему?
//        System.out.println(numbers.sumsStream().toList());

        System.out.println("2) Число в соотвествии с условием: ");
        System.out.println(num2(numbers));

        System.out.println("Added 0 btw");
        numbers.add(0);

        SummableNumbers negative = new SummableNumbers(numbers.getNumbersType(-1));
        SummableNumbers nulls = new SummableNumbers(numbers.getNumbersType(0));
        SummableNumbers positive = new SummableNumbers(numbers.getNumbersType(1));

        System.out.println("Число по группам: ");
        System.out.println("Числа: " + negative.numbers + " Суммы: " + negative.sumsStream().toList() + " Число: " + num2(negative));
        System.out.println("Числа: " + nulls.numbers + " Суммы: " + nulls.sumsStream().toList() + " Число: " + num2(nulls));
        System.out.println("Числа: " + positive.numbers + " Суммы: " + positive.sumsStream().toList() + " Число: " + num2(positive));


    }
}
