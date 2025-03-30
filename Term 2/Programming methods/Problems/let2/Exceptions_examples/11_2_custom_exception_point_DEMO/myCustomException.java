public class myCustomException extends Exception{
    public myCustomException(){
        super("some message from my custom exception");
        System.out.println("--> start of myCustomException constructor");
    }
    public void getMsg(String msg){
        System.out.println(msg);
    }
}
