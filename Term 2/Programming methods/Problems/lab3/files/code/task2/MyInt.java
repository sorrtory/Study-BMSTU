package task2;

public class MyInt implements Comparable<MyInt>{
    private int num;
    private int numPriveDivs;
    
    private int countNumPrimeDivs(){

        int d = 2;
        int count = 1;
        int n = num;

        while (d * d <= n){
            if (n % d == 0){
                n = n / d;
                count += 1;
            }
            else {
                d += 1;
            }
        }
        if (n > 1){
            count += 1;
        }

        return count;
    }

    public MyInt(int num){
        this.num = num;
        this.numPriveDivs = countNumPrimeDivs();
        
    }

    @Override
    public int compareTo(MyInt obj) {
        if (numPriveDivs==0 && obj.numPriveDivs==0) return 0;
        else if (numPriveDivs == 0) return -1;
        else if (obj.numPriveDivs == 0) return 1;
        else return numPriveDivs - obj.numPriveDivs;
    }

    @Override
    public String toString() {
        return "MyInt{" +
                "num=" + num +
                ", numPriveDivs=" + numPriveDivs +
                '}';
    }
}
