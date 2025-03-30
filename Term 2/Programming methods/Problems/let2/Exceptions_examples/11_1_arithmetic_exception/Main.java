public class Main
{
  public static void main (String[]args)
  {
    //System.out.println("Не перехваченные исключения:");
    //System.out.println(10/0); // далее программа "свалится"
    
    int a = 1;
    int b = 2;
    
    if(a>b) {
        throw new RuntimeException("не равно!");
    }
      
    try {
        System.out.println(10/0);
    }
    catch (ArithmeticException aaa) {
        System.out.println(aaa.getMessage());
    }
    finally {
        System.out.println("Exiting from try");
    }
    System.out.println("End of program");
  }
}


