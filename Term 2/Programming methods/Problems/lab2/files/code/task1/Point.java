package task1;

public class  Point {
    static double maxX, maxY;
    static double minX, minY;
    static int count = 0;
    private double x, y, m;
    public  Point ( double x ,  double y, double m) {
        this.x = x;
        this.y = y;
        this.m = m;
        count += 1;

        if (x > maxX){
            maxX = x;
        }
        if (y > maxY){
            maxY = y;
        }

        if (x < minX){
            minX = x;
        }
        if (y < minY){
            minY = y;
        }
    }

    public static double getSquare(){
        return (maxX - minX) * (maxY - minY);
    }
    public static int getCount(){
        return count;
    }
    public double getX()  { return x; }
    public double getY()  { return y; }
    public double getM()  { return m; }


    public String toString() {
        return "(X: %7.3f Y: %7.3f  M: %7.3f)".formatted(x, y, m);
    }

}