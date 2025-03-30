public class Main {

   public static void main(String[] args) {

      int i;
      double E=0.0;
      Point A = new Point("A", 10, 10);
      Point B = new Point("B", 10, 0);
      Point C = new Point("C", 0, 0);

      A.getInfo();
      B.getInfo();
      C.getInfo();
      Point.getN();

      Point [] points = new Point[100];
      points[0] = new Point("AA", 100,100);
      points[1] = new Point("BB", 101,101);
      points[2] = new Point("CC", 102,102);
      points[3] = new Point("DD", 103,103);
      points[4] = new Point("EE", 104,104);
      points[5] = new Point("FF", 105,105);
 
      points[0].setV(100,100);
      points[1].setV(100,100);
      points[2].setV(100,100);
      points[3].setV(100,100);
      points[4].setV(100,100);
      points[5].setV(100,100);

      System.out.println("points len: " + points.length);

      for(i=0; i< points.length; i++)
         {
          if(points[i] != null)
            {
             System.out.println("Eк "+i+"=" + points[i].getE());
             E = E +  points[i].getE();
            }
          else
            {
             System.out.println("Object "+i+" not initialised");
            }
         }

      System.out.println("Total E = "+E);


      //points[0].getE;
      //points[1].getE;
      //points[2].getE;
      //points[3].getE;
      //points[4].getE;
      //points[5].getE;

      Point.getN();
   }
}
