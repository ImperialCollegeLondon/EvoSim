package vehicle;
import java.util.Random;

public class BatteryLevel {
    private static final Random rand = new Random();

    public static int getRandomBatteryLevel()  {
        double randomN = rand.nextDouble() * 100;
        if (randomN <= 9.66) {
            return 1 + rand.nextInt(5);  // 1-5
        } else if (randomN <= 9.66 + 46.21) {
            return 6 + rand.nextInt(20);  // 6-25
        } else if (randomN <= 9.66 + 46.21 + 29.66) {
            return 26 + rand.nextInt(25); // 26-50
        } else if (randomN <= 9.66 + 46.21 + 29.66 + 6.90) {
            return 51 + rand.nextInt(25); // 51-75
        } else {
            return 75 + rand.nextInt(5); // 75-80
        }
    }

}

