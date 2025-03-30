// 7.03.24

public class Main {
    public static void main(String[] args) {
        System.out.println("Fedukov A A IU9-22B");

        System.out.println("\nFigure tests");
        Figure A = new Figure(1);
        System.out.println(A.getType());
        A.move();

        System.out.println("\nColoredFigure tests");
        ColoredFigure B = new ColoredFigure(0, "Blue");
        System.out.println(B.getColor());
        B.setColor("White");
        System.out.println(B.getColor());


    }
}

class Figure{
    public int type;

    public int getType() {
        return type;
    }

    public Figure(int type){
        // 0 - circle
        // 1 - square
        // 2 - rectangle

        this.type = type;
    }
    public void move(){
        System.out.println("Figure moved");
    }
}

class ColoredFigure extends Figure{

    public String name;
    public String color;

    public String getName() {
        return name;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public String getColor() {
        return color;
    }

    public ColoredFigure(int type, String color) {
        super(type);
        this.color = color;
    }

}

