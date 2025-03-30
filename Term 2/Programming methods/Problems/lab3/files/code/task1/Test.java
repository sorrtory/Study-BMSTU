package task1;

public class Test {
    public static void main(String[] args) {

        ChessBoard CB = new ChessBoard(6);
        CB.printQueens();
        CB.sortQueens();
        System.out.println("Queens sorted btw");
        CB.printQueens();

    }
}