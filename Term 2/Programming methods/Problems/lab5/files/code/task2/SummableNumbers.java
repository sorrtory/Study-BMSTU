package task2;



import java.util.*;
import java.util.stream.Stream;

class myInt implements Comparable<myInt>{
    int x;
    int id;
    int type;
    myInt(int x, int id){
        this.x = x;
        this.id = id;
        this.type = (int) Math.signum(x);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        myInt myInt = (myInt) o;
        return x == myInt.x && id == myInt.id;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, id);
    }


    @Override
    public int compareTo(myInt o) {
        return Integer.compare(this.x, o.x);
    }

    @Override
    public String toString() {
//        return "myInt{" +
//                "x=" + x +
//                ", id=" + id +
//                ", type=" + type +
//                '}';
        return Integer.toString(x);
    }
}

public class SummableNumbers {
    ArrayList<myInt> numbers = new ArrayList<>();

    SummableNumbers(int[] x){
        Arrays.stream(x).forEach(q -> numbers.add(new myInt(q, numbers.size())));
    }
    SummableNumbers(List<myInt> x){
        x.stream().forEach(q -> numbers.add(new myInt(q.x, numbers.size())));
    }
    public void sort(){
        numbers.sort(myInt::compareTo);
    }

    public List<myInt> getNumbersType(int type) {
        return numbers.stream().filter(x -> x.type == type).toList();
    }

    public void add(int x){
        numbers.add(new myInt(x, numbers.size()));
    }
    public Stream<Integer> sumsStream() {
        ArrayList<Integer> result = new ArrayList<>();
        numbers.forEach(x1 -> numbers.stream().filter(x2 -> x1.id < x2.id).forEach(x2 -> result.add(x1.x + x2.x)));
        return result.stream();
    }
    public Stream<Integer> sumsStreamWithout(myInt w){
        ArrayList<Integer> result = new ArrayList<>();
        numbers.forEach(x1 -> numbers.stream().filter(x2 -> (x1.id < x2.id) & (x1 != w & x2 != w)).forEach(x2 -> result.add(x1.x + x2.x)));
        return result.stream();
    }
    
    private boolean myFilter(myInt x){
        Stream<myInt> more_than_x = numbers.stream().filter(x2 -> x2.x > x.x);
        return more_than_x.noneMatch(x2 -> sumsStreamWithout(x2).noneMatch(x3 -> x3 == x2.x));
    }
    public Optional<Integer> findSpecialX() {
        Optional<Integer> result = numbers.stream().filter(this::myFilter).map(x -> x.x).findFirst();
        return result;
    }
}
