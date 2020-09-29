/*
 * Project: Evo-Sim
 * Developed by: Irina Danes
 */

package chargingInfrastructure;

import chargingStation.ChargingPoint;
import utils.ChargingType;
import utils.Geolocation;
import utils.SocketType;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

import static evoSim.Main.printWriter;

public class SupplyGenerator {

    public static void generateCPs(List<ChargingPoint> cps, int amount) {
        final int[] priceConstraints = new int[]{0, 5, 10};

        Random rand = new Random();
        for (int i = 0; i < amount; i++) {
            cps.add(new ChargingPoint(new Geolocation(rand.nextFloat() * 0.45 + 51.25, rand.nextFloat() * 0.75 - 0.50),
                    SocketType.values()[rand.nextInt(6)],
                    ChargingType.getRandomChargingType(),
                    priceConstraints[rand.nextInt(2)],
                    Status.AVAILABLE));
//                    Status.values()[rand.nextInt(3)]));
            cps.get(cps.size() - 1).setIndex(ChargingPoint.lastIndex++);
            printWriter.println(cps.get(cps.size() - 1).getLocation().getX() + ", " + cps.get(cps.size() - 1).getLocation().getY());

//            cps.get(cps.size() - 1).printCP();
//            printWriter.println();
        }
    }


    public static void generateCPfromFile(List<ChargingPoint> cps, String dateAndTime) throws IOException, ParseException {
        Map<Integer, Status> january = new HashMap<>();
        Map<Integer, List<String[]>> socketsMap = new HashMap<>();

        SimpleDateFormat sdformat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        Date dateTime = sdformat.parse(dateAndTime);

        File sockets = new File("data/sockets");
        BufferedReader br1 = new BufferedReader(new FileReader(sockets));
        String st1;
        while ((st1 = br1.readLine()) != null) {
            String[] socket_data = st1.split("\\s+");
            int socket_id = Integer.parseInt(socket_data[4]);
            if (!socketsMap.containsKey(socket_id)) {
                socketsMap.put(socket_id, new ArrayList<>());
            }
            socketsMap.get(socket_id).add(socket_data);

            Status status;
            if (socket_data[6].equals("1")) {
                status = Status.AVAILABLE;
            } else if (socket_data[6].equals("0")) {
                status = Status.UNAVAILABLE;
            } else {
                status = Status.OUT_OF_ORDER;
            }

            january.put(Integer.parseInt(socket_data[0]), status);
        }

        File statuses = new File("data/socketStatus");
        BufferedReader br3 = new BufferedReader(new FileReader(statuses));
        String st3;
        while ((st3 = br3.readLine()) != null) {
            String[] statuses_data = st3.split("\\s+");

            String date = statuses_data[1];
            String time = statuses_data[2];
            Date currentDateTime = sdformat.parse(date + " " + time);

            int id_status = Integer.parseInt(statuses_data[4]);
            Status status;
            if (statuses_data[3].equals("1")) {
                status = Status.AVAILABLE;
            } else if (statuses_data[3].equals("0")) {
                status = Status.UNAVAILABLE;
            } else {
                status = Status.OUT_OF_ORDER;
            }

            if (currentDateTime.before(dateTime)) {
                january.put(id_status, status);
            }
        }

        File stations = new File("data/stations");
        BufferedReader br2 = new BufferedReader(new FileReader(stations));
        String st2;
        while ((st2 = br2.readLine()) != null) {
            String[] station_data = st2.split("\\s+");
            double l = Double.parseDouble(station_data[1]);
            double r = Double.parseDouble(station_data[2]);

            Geolocation location = new Geolocation(l, r);
            int id = Integer.parseInt(station_data[0]);
            if (socketsMap.containsKey(id)) {
                for (String[] data : socketsMap.get(id)) {
                    SocketType socket_type = SocketType.getSocketType(data[1]);

                    ChargingType charging_type = ChargingType.convertKWsToChargingType(Double.parseDouble(data[3]));
                    double price = Double.parseDouble(data[2]);
                    if (price < 0) {
                        price = 0;
                    }

                    Status status = january.get(Integer.parseInt(data[0]));

                    String postcode = station_data[station_data.length - 2] + " " + station_data[station_data.length - 1];

                    ChargingPoint chargingP = new ChargingPoint(location, socket_type, charging_type, price, status);
                    chargingP.setPostcode(postcode);
                    cps.add(chargingP);
                    cps.get(cps.size() - 1).setIndex(ChargingPoint.lastIndex++);
                }
            }
        }
    }

    public static void generateCPsInArea(List<ChargingPoint> cps, String outcode, int amount) throws IOException, InterruptedException {
        Random rand = new Random();
        final int[] priceConstraints = new int[]{0, 5, 10};

        Map<Geolocation, String> locationsPostcodes = Geolocation.bulkReverseGeocoding(amount, outcode);
        List<Geolocation> keys = new ArrayList<>(locationsPostcodes.keySet());

        printWriter.println("Generated charging points in area: " + outcode);
        int no = 0;
        int cps_initial_size = cps.size();
        while (cps.size() - cps_initial_size < amount) {
            if (no >= amount) {
                locationsPostcodes = Geolocation.bulkReverseGeocoding(amount, outcode);
                keys = new ArrayList<>(locationsPostcodes.keySet());
                no = 0;
            }
            Geolocation location = keys.get(no);
            while (locationsPostcodes.get(location) == null) {
                location = keys.get(no);
                no++;
                if (no >= amount) {
                    locationsPostcodes = Geolocation.bulkReverseGeocoding(amount, outcode);
                    keys = new ArrayList<>(locationsPostcodes.keySet());
                    no = 0;
                }
            }
            String postcode = locationsPostcodes.get(location);
            String generatedOutcode = Geolocation.getOutwardCode(location);

            if (postcode != null && outcode.equals(generatedOutcode) && !postcode.equals("other")) {
                cps.add(new ChargingPoint(location,
                        SocketType.values()[rand.nextInt(6)],
                        ChargingType.getRandomChargingType(),
                        priceConstraints[rand.nextInt(2)],
                        Status.AVAILABLE));
                cps.get(cps.size() - 1).setPostcode(postcode);
                cps.get(cps.size() - 1).setIndex(++ChargingPoint.lastIndex);
                printWriter.println(cps.get(cps.size() - 1).getLocation().getX() + ", " + cps.get(cps.size() - 1).getLocation().getY());
            }
            no++;
        }
    }

}
