public class Main
{
	public static void main(String[] args) {
	try{
        int result = Factorial.getFactorial(-1);
        System.out.println(result);
	   }
	catch(myFE kkk) {
	    System.out.println(kkk.getMessage());
	     System.out.println(kkk.getNumber());
	     }
	}
}

class Factorial{
    public static int getFactorial(int num) throws myFE {
        int result=1;
        if(num < 0) throw new myFE("num меньше 0", num);
        for(int i=1; i<=num; i++) {
            result*=i;
        }
        return result;
    }
}


class myFE extends Exception {
    private int number;
    public int getNumber() {return number;}
    public myFE (String message, int num){
        super(message);
        number=num;
    }
    
}

