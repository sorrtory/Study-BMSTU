package task2;

import java.util.Arrays;

public class Test {
    public static void main(String[] args) {
        // Разница между num и this.num???
        // Что значит @Override
        // Когда var public, а когда getVar и private
        int n = 10;

        MyInt[] myIntArrayList = new MyInt[n];

        for (int i = 0; i < n; i++) {
            myIntArrayList[i] = (new MyInt((int) (Math.random() * 100)));
        }

        System.out.println("List before sort");
        for (int i = 0; i < n; i++) {
            System.out.println(myIntArrayList[i]);
        }

        Arrays.sort(myIntArrayList);
        System.out.println("\nList after sort");
        for (int i = 0; i < n; i++) {
            System.out.println(myIntArrayList[i]);
        }

    }
}
