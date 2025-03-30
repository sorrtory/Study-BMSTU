package task2;

public class Test {
    public static void main(String[ ] args ) {
        String[] s = new String[5];
        s[0] = "abhcsa1";
        s[1] = "a1aaaaa";
        s[2] = "bbbbaaa2";
        s[3] = "aaa2aaadsf";
        s[4] = "sfaaaaacc";

        StringList L = new StringList(s);
        for (String suff: L) System.out.println(suff);

        System.out.println("AFTER Changes");

        s[0] = "zxc";
        for (String suff: L) System.out.println(suff);

    }
}
