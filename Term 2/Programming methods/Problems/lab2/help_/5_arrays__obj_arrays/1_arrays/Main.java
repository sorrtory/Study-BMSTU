public class Main {

   public static void main(String[] args) {

      Array A = new Array("A");
      System.out.println("A.names[0] = "+A.names[0]);
      System.out.println("A.names[1] = "+A.names[1]);

      A.setElement(0,0,123.45);
      System.out.println("A.getElement[0][0] = "+A.getElement(0,0));
  
      System.out.println("A [M х N] = "+A.getM()+" "+A.getN());


   }
}
