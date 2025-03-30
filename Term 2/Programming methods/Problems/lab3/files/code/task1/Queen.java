package task1;

public class Queen implements Comparable<Queen>{
    private int x;
    private int y;
    private int numCouldEasilyCapture;

    public void setNumCouldEasilyCapture(int n){this.numCouldEasilyCapture = n;}

    public int getX() {
        return x;
    }

    public int getY() {
        return y;
    }

    public Queen(int x, int y){
        this.x = x;
        this.y = y;
        this.numCouldEasilyCapture = 0;
    }

    @Override
    public int compareTo(Queen obj) {
        if (numCouldEasilyCapture==0 && obj.numCouldEasilyCapture==0) return 0;
        else if (numCouldEasilyCapture == 0) return -1;
        else if (obj.numCouldEasilyCapture == 0) return 1;
        else return numCouldEasilyCapture - obj.numCouldEasilyCapture;
    }

    @Override
    public String toString() {
        return "task1.Queen{" +
                "x=" + x +
                ", y=" + y +
                ", numCouldEasilyCapture=" + numCouldEasilyCapture +
                '}';
    }
}
