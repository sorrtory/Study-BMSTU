import static java.lang.Math.*;

public class Point
{
   public String name;
   private double x;
   private double y;
   private double vx;
   private double vy;
   private double m;
   static private int N = 0;

   public Point(String argName, int xVar, int yVar)
   {
      System.out.println("Инициализирован объект Point: "+argName);
      this.name = argName;
      this.N++;
      this.x = xVar;
      this.y = yVar;
      this.m = 10;
   }

   public String getName()
   {
    return name;
   }

   public static void getN()
   {
    System.out.println("Количество частиц N: "+N);
   }

   public void getInfo()
   {
    System.out.println("x="+this.x+" y="+this.y);
   }

   public void setV(double vxVar,double vyVar)
   {
    this.vx = vxVar;
    this.vy = vyVar;
   }
 
   public double getE()
   {
    return m*(pow(this.vx,2)+pow(this.vy,2))/2;
   }




}
