package chargingDemand;

import vehicle.BatteryLevel;
import vehicle.CarModel;
import vehicle.ChargingType;
import vehicle.DistanceConstraint;
import vehicle.ElectricVehicle;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;
import java.util.Random;

import chargingStation.Geolocation;
import chargingStation.SocketType;


public class DemandGenerator {

    public static void generateEVs(List<ElectricVehicle> evs, int amount, double willingToPayPercentage) {
        Random rand = new Random();
        for (int i = 0; i < amount; i++) {
            evs.add(new ElectricVehicle(new Geolocation(rand.nextFloat() * 0.23 + 51.41, rand.nextFloat() * 0.34 - 0.29),
                    new Geolocation(rand.nextFloat() * 0.23 + 51.41, rand.nextFloat() * 0.34 - 0.29),
                    SocketType.getRandomSocketType(),
                    ChargingType.getRandomChargingType(),
                    BatteryLevel.getRandomBatteryLevel(),
                    DistanceConstraint.getRandomDistanceConstraint(),
                    ElectricVehicle.getRandomWaitTime(),
                    CarModel.values()[rand.nextInt(30)]));
            evs.get(evs.size() - 1).setIndex(ElectricVehicle.lastIndex++);
            evs.get(evs.size() - 1).setWillingToPay(willingToPayPercentage);
//            evs.get(i).printEV();
//            printWriter.println();
        }
    }

    public static void readEVsFromFile(List<ElectricVehicle> evs, String filename) throws IOException {
        File file = new File(filename);
        BufferedReader br = new BufferedReader(new FileReader(file));

        Random rand = new Random();

        String st;
        while ((st = br.readLine()) != null) {
            String[] ev_data = st.split(" ");
            int index = Integer.parseInt(ev_data[0]);
            double origin_x = Double.parseDouble(ev_data[1].substring(1, ev_data[1].length() - 1));
            double origin_y = Double.parseDouble(ev_data[2].substring(0, ev_data[2].length() - 1));

            double destination_x = Double.parseDouble(ev_data[3].substring(1, ev_data[3].length() - 1));
            double destination_y = Double.parseDouble(ev_data[4].substring(0, ev_data[4].length() - 1));

            SocketType socketType = SocketType.getSocketType(ev_data[5]);
            ChargingType chargingType = ChargingType.getChargingTypeFromString(ev_data[6]);

            int batteryLevel = Integer.parseInt(ev_data[7]);
            double distanceConstraint = Double.parseDouble(ev_data[8]);
            boolean willingToPay = Boolean.parseBoolean(ev_data[9]);
            double waitTime = Double.parseDouble(ev_data[10]);
            String carModel = ev_data[11];

            ElectricVehicle ev = new ElectricVehicle(new Geolocation(origin_x, origin_y),
                    new Geolocation(destination_x, destination_y),
                    socketType,
                    chargingType,
                    batteryLevel,
                    distanceConstraint,
                    waitTime,
                    CarModel.values()[rand.nextInt(30)]);
            ev.setIndex(index);
            ev.setWillingToPayDirectly(willingToPay);

            evs.add(ev);
        }
    }

}

