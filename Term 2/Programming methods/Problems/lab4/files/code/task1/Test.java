package task1;

public class Test {
    public static void main(String[ ] args ) {
        StringBuilder b = new StringBuilder("kmqwertyjkdndsnjvdjwekmcvklvcwekmvckvcnvnjcnjwe");
        SuffixList suff = new SuffixList(b, "we");
        for(Integer s : suff) System.out.println(s + " " +b.substring(s, b.length()));

        System.out.println("AFTER Changes");
        b.insert(1,"x");
        suff.setW("km");

        for(Integer s : suff) System.out.println(s + " " +b.substring(s, b.length()));
    }
}