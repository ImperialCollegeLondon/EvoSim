/*
 * Project: Evo-Sim
 * Developed by: Irina Danes
 */

package electricVehicle;

import java.util.Random;

public class DistanceConstraint {
    private static final Random rand = new Random();

    public static double getRandomDistanceConstraint()  {
        double randomN = rand.nextDouble() * 100;
        double distanceInMins;

        if (randomN <= 29.56) {
            distanceInMins = 5;
        } else if (randomN <= 29.56 + 60) {
            distanceInMins = 15;
        } else {
            distanceInMins = 30;
        }
        return getDistanceInKms(distanceInMins);
    }

    public static double getDistanceInKms(double distanceInMins) {
        return distanceInMins / 10.0;
    }
}
