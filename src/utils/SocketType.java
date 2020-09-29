/*
 * Project: Evo-Sim
 * Developed by: Irina Danes
 */

package utils;

import java.util.Random;

public enum SocketType {
    TYPE1(30), TYPE2(59.46), THREE_PIN_SQUARE(1.69), DC_COMBO_TYPE2(3.64), CHADEMO(3.77), CCS4(1.32);

    private final double percent;

    SocketType(double percent) {
        this.percent = percent;
    }

    private double getPercent() {
        return percent;
    }

    public static SocketType getSocketType(String s) {
        switch(s) {
            case "TYPE_1":
            case "TYPE1":
                return TYPE1;
            case "TYPE2":
            case "TYPE_2":
                return TYPE2;
            case "THREE_PIN_SQUARE":
                return THREE_PIN_SQUARE;
            case "DC_COMBO_TYPE_2":
            case "DC_COMBO_TYPE2":
                return DC_COMBO_TYPE2;
            case "CHADEMO":
                return CHADEMO;
            default: // "CCS4"
                return CCS4;
        }
    }

    private static final Random rand = new Random();

    public static SocketType getRandomSocketType() {
        int randomNum = rand.nextInt(100);
        int currentSum = 0;
        SocketType currentValue = values()[0];
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
}
