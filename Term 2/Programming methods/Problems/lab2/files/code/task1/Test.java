package task1;

public class Test {
    public static void main (String [] args) {
        for (int i = 0; i < 100; i++){
            Point p = new Point(Math.random()*100,Math.random()*100, 0);
            System.out.println(p);
        }

        System.out.println();
        System.out.println("Square: " + Point.getSquare());
        

    }
}
