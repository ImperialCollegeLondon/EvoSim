package vehicle;

import java.io.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import chargingStation.Geolocation;
import chargingStation.SocketType;

import static evoSim.Main.fileWriter;

public class ElectricVehicle {
    private static final PrintWriter printWriter = new PrintWriter(fileWriter);

    private int index;
    public static int lastIndex = 0;

    private static final Random rand = new Random();

    private final Geolocation origin;
    private final Geolocation destination;
    private final SocketType socketType;
    private final ChargingType chargingType;
    private final int batteryLevel;
    private final double distanceConstraint;
    private boolean willingToPay;
    private final double waitTime;
    private final CarModel carModel;

    public ElectricVehicle(Geolocation origin, Geolocation destination, SocketType socketType,
                           ChargingType chargingType, int batteryLevel, double distanceConstraint,
                           double waitTime, CarModel carModel) {
        this.origin = origin;
        this.destination = destination;
        this.socketType = socketType;
        this.chargingType = chargingType;
        this.batteryLevel = batteryLevel;
        this.distanceConstraint = distanceConstraint;
//        this.willingToPay = willingToPay;
        this.waitTime = waitTime;
        this.carModel = carModel;
    }

    public void setIndex(int index) {
        this.index = index;
    }

    public int getIndex() {
        return index;
    }

    public Geolocation getDestination() {
        return destination;
    }

    public Geolocation getOrigin() {
        return origin;
    }

    public SocketType getSocketType() {
        return socketType;
    }

    public ChargingType getChargingType() {
        return chargingType;
    }

    public int getBatteryLevel() {
        return batteryLevel;
    }

    public double getDistanceConstraint() {
        return distanceConstraint;
    }

    public void setWillingToPay(double alpha)  {
        int randomNum = rand.nextInt(100);
        int currentSum = 0;
        boolean willingToPay = false;
        Map<Boolean, Double> map = new HashMap<>();
        map.put(true, alpha);
        map.put(false, 100.0 - alpha);
        for (Map.Entry<Boolean, Double> entry : map.entrySet()) {
            willingToPay = entry.getKey();
            Double v = entry.getValue();

            if (randomNum > currentSum && randomNum <= (currentSum + v)) {
                break;
            }
            currentSum += v;
        }
        this.willingToPay = willingToPay;
    }

    public void setWillingToPayDirectly(boolean willingToPay) {
        this.willingToPay = willingToPay;
    }

    public boolean getWillingToPay() {
        return willingToPay;
    }

    public static double getRandomWaitTime() {
        double randomN = rand.nextDouble() * 100;
        int time;

        if (randomN <= 7.56) {
            time = 0;
        } else if (randomN <= 31.09) {
            time = 5;
        } else if (randomN <= 63.86) {
            time = 10;
        } else if (randomN <= 76.47) {
            time = 15;
        } else if (randomN <= 82.35) {
            time = 30;
        } else {
            time = 500; // more than 30 minutes
        }
        return time;
    }

    public double getWaitTime() {
        return waitTime;
    }

    public CarModel getCarModel() {
        return carModel;
    }

    public double timeToCharge() {
        double time;
        double fullChargingTime;
        if (chargingType == ChargingType.STANDARD) {
            fullChargingTime = 8.0;
        } else if (chargingType == ChargingType.FAST) {
            fullChargingTime = 5.0;
        } else { // if (chargingType == ChargingType.RAPID)
            fullChargingTime = 2.0;
        }
        time = (100.0 - batteryLevel) / 100.0 * fullChargingTime;
        return time;
    }

    public static void printEVheadings() {
        printWriter.println();
        printWriter.println("index    origin    destination    socketType    chargingType       " +
                "batteryLevel    distanceConstraint    priceConstraint    waitTime    carModel");
        printWriter.println();
    }

    public void printEV() {
        printWriter.print(this.getIndex() + " " +
                this.getOrigin().printGeolocation() +  " " +
                this.getDestination().printGeolocation() + " " +
                this.getSocketType() + " " +
                this.getChargingType() + " " +
                this.getBatteryLevel() + " " +
                this.getDistanceConstraint() + " " +
                this.getWillingToPay() + " " +
                this.getWaitTime() + " " +
                this.getCarModel());
    }
}

