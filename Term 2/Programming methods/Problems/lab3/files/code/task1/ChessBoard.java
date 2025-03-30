package task1;

import java.util.ArrayList;
import java.util.Collections;

public class ChessBoard {
    private int numOfQueens;
    private ArrayList<Queen> queens;

    public void printQueens(){
        if (numOfQueens == 0){
            System.out.println("No queens though");
        }
        else {
            for (int i = 0; i < numOfQueens; i++) {
                System.out.println(queens.get(i));
            }
        }
    }
    public void sortQueens(){
        Collections.sort(this.queens);
    }
    private boolean CouldCapture(Queen q1, Queen q2){
        return q1.getX() == q2.getX() | q1.getY() == q2.getY() | (Math.abs(q1.getX() - q2.getX()) == Math.abs(q2.getY() - q1.getY()));
    }
    private void MakeQueens(){
        // Adding
        for (int i = 0; i < numOfQueens; i++) {
            queens.add(new Queen((int) (Math.random() * 8) + 1, (int) (Math.random() * 8) + 1));
        }

        // Balancing
        for (int i = 0; i < numOfQueens; i++) {
            int couldCapture = 0;
            for (int j = 0; j < numOfQueens; j++) {
                if (i != j & CouldCapture(queens.get(i), queens.get(j))) {
                    couldCapture += 1;
                }
            }
            queens.get(i).setNumCouldEasilyCapture(couldCapture);
        }
    }
    public ChessBoard(int numOfQueens){
        this.numOfQueens = numOfQueens;
        this.queens = new ArrayList<Queen>();
        MakeQueens();
    }
}
