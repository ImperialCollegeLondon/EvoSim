/*
 * Project: Evo-Sim
 * Developed by: Irina Danes
 */

package utils;

import java.util.Random;

public enum ChargingType {
    STANDARD(29.76), FAST(67.85), RAPID(2.38);

    private final double percent;

    ChargingType(double percent) {
        this.percent = percent;
    }

    private double getPercent() {
        return percent;
    }

    private static final Random rand = new Random();

    public static ChargingType getRandomChargingType() {
        int randomNum = rand.nextInt(100);
        int currentSum = 0;
        ChargingType currentValue = values()[0];
        for (int i = 0; i < values().length; i++) {
            currentValue = values()[i];
            if (randomNum > currentSum &&
                    randomNum <= (currentSum + currentValue.getPercent())) {
                break;
            }
            currentSum += currentValue.getPercent();
        }
        return currentValue;
    }

    public static ChargingType getChargingTypeFromString(String s) {
        if (s.equals("STANDARD")) {
            return STANDARD;
        } else if (s.equals("FAST")) {
            return FAST;
        } else {
            return RAPID;
        }
    }

    public static ChargingType convertKWsToChargingType(double s) {
        if (s < 4) {
            return STANDARD;
        } else if (s < 10) {
            return FAST;
        } else {
            return RAPID;
        }
    }

}