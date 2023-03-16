public class Test {
    public static Integer div(int a,int b){
        try{
            return a/b;
        }
        finally {
            System.out.println("ajjaja");
        }
    }

    public static void main(String[] args) {

        try{
            div(1,0);
        }catch (Exception e){
            System.out.println("ananan");
        }
    }




}
