public class Main {

   public static void main(String[] args) {

        Point PointA = new Point("A");
        System.out.println("Имя точки:"+PointA.getName());
        PointA.setCoord(1.0,1.0,1.0);
        System.out.println("Длинна радиус-вектора:"+PointA.getR());
        
        try {
            PointA.someExample();
        }
        catch(myCustomException qqq)
        {
            qqq.getMsg("Поимали исключительную ситуацию");
        }

   }
}
