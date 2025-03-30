import static java.lang.Math.*;

public class Array
{
   public String name;
   public String [] names = new String[10];
   private double points [][] = new double[200][100];

   public Array(String argName)
   {
      System.out.println("Запущен конструктор объекта Array: "+argName);
      this.name = argName;
      this.names[0] = "Николай";
   }

   public String getName()
   {
    return name;
   }

   public void setElement(int i, int j, double val)
   {
    this.points[i][j] = val;
   }

   public double getElement(int i, int j)
   {
    return this.points[i][j];
   }

   public int getM()
   {
    return this.points.length;
   }

   public int getN()
   {
    if(points.length>0)
      {
       return this.points[0].length;
      }
    else
      {
       return 0; 
      }
   }

}
