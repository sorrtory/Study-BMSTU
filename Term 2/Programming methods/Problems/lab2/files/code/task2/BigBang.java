package task2;

import task1.Point;

import java.util.ArrayList;
import java.util.List;

public class BigBang {
    private static String findCenterMass(List<Point> points){
        double x = 0, y = 0, m = 0;
        for (Point point: points){
            x += point.getX();
            y += point.getY();
            m += point.getM();
        }
        return "(Xc: %f, Yc: %f)".formatted(x/m, y/m);
    }
    public static void main (String [] args) {
        List<Point> points = new ArrayList<>();

        for (int i = 0; i < 100; i++){
            points.add(new Point(Math.random()*100,Math.random()*100, Math.random()));
            System.out.println(points.getLast());
        }

        System.out.println();
        System.out.println("Вселенная породилась))0, точек: " + Point.getCount());
        System.out.println("Хорошо, что центр масс получился в такой хорошей точке как: ");
        System.out.println(findCenterMass(points));



    }
}
