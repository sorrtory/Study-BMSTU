package task1;

/*
    Последовательность точек в трёхмерном
    пространстве с операциями:

    1. порождение потока отрезков, соединяющих
    соседние точки и пересекающих плоскость Oxy.

    2. вычисление отношения количества точек,
    попадающих в шар с центром в начале координат
    и радиусом r, к количеству точек, которые в этот
    шар не попадают.

    Проверить работу первой операции нужно путём
    подсчёта количества отрезков, пересекающ
    плоскость Oxy в каждой из её четвертей.
*/
/*
    В каждом классе нужно реализовать по крайней мере два метода: первый метод
    должен возвращать Stream, а второй – Optional. Операции, выполняемые каждым методом,
    указаны в вариантах задания.

    В методе main вспомогательного класса task1.Test нужно продемонстрировать
    работоспособность разработанного класса, осуществив группировку содержимого потока,
    возвращаемого первым методом, с помощью группирующего коллектора.

    В исходном коде (включая класс task1.Test) запрещено использовать циклы и рекурсию.
*/
public class Test {
    public static void main(String[] args) {
        Space space = new Space();
        int neighbour_distance = 10;
        int r = 1;

        space.add(1, 1, 1);
//        space.add(2, 10, 10);
        space.add(-1, -1, 0);
        space.add(0, -2, 1);
        space.add(-3, 0, 1);
        space.add(0, 1, -1);

        System.out.println("    All the lines:");
        space.linesStream(neighbour_distance).forEach(System.out::println);

        System.out.println("    All the quarters of crossOXY:");
        System.out.println("I: " + space.linesStream(neighbour_distance).filter(line -> line.getQuarter(1)).count());
        System.out.println("II: " + space.linesStream(neighbour_distance).filter(line -> line.getQuarter(2)).count());
        System.out.println("III: " + space.linesStream(neighbour_distance).filter(line -> line.getQuarter(3)).count());
        System.out.println("IV: " + space.linesStream(neighbour_distance).filter(line -> line.getQuarter(4)).count());

        System.out.println("    All the points inside/outside sphere:");
        space.getPointsInside(r).ifPresent(System.out::println);
        space.getPointsOutside(r).ifPresent(System.out::println);
        if (space.getPointsInside(r).isPresent() & space.getPointsOutside(r).isPresent()
                & !space.getPointsOutside(r).get().isEmpty()){
            System.out.println((double) space.getPointsInside(r).get().size() / space.getPointsOutside(r).get().size());
        }

    }

}