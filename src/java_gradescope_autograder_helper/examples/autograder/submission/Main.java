/*
 * Student file structure does not matter as long as they have a `.java` file
 * with the same name as the entry point specified in
 * `/autograder/source/tests.py`. If multiple files with the same name are
 * present, the autograder will fail with an appropriate error message.
 */

public class Main {

    public static void main(String[] args) {
        if (args.length == 0) {
            return;
        }

        if (args[0].equals("greet") && args.length > 1) {
            System.out.println(greet(args[1]));
            return;
        }

        if (args[0].equals("add") && args.length > 2) {
            try {
                int a = Integer.parseInt(args[1]);
                int b = Integer.parseInt(args[2]);
                System.out.println(add(a, b));
                return;
            } catch (NumberFormatException e) {
                System.out.println("Error: Arguments for add must be integers");
                return;
            }
        }

        System.out.println(
            "Usage: `java Main greet <name>` OR `java Main add <number> <number>`"
        );
    }

    public static String greet(String name) {
        return "Hello, " + name + "!"; // + " Banana Split!";
    }

    public static int add(int a, int b) {
        return a + b;
    }
}
