package chargingInfrastructure;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import chargingStation.ChargingPoint;
import chargingStation.Geolocation;
import chargingStation.SocketType;
import chargingStation.Status;
import vehicle.ChargingType;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
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
            cps.get(cps.size() - 1).printCP();
            printWriter.println();
        }
    }


    public static void generateCPfromFile(String directory, List<ChargingPoint> cps, String dateAndTime) 
    		throws IOException, ParseException {
        Map<Integer, Status> january = new HashMap<>();
        Map<Integer, List<String[]>> socketsMap = new HashMap<>();

        SimpleDateFormat sdformat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        Date dateTime = sdformat.parse(dateAndTime);
        
        File sockets = new File(directory + "/data/sockets");
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

        File statuses = new File(directory + "/data/socketStatus");
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
        
        File stations = new File(directory + "/data/stations");
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

                    ChargingType charging_type = ChargingType.getChargingType(Double.parseDouble(data[3]));
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
//                    printWriter.println(data[0] + " ");
//                    cps.get(cps.size() - 1).printCP();
//
//                    printWriter.println();
                }
            }
        }
    }

    // generates a location within the given distance (kms) from the given location
    public static Geolocation generateLocationWithinDistance(Geolocation location, double distance) {
        Random rand = new Random();

        double lat = Math.toRadians(location.getX());
        double lon = Math.toRadians(location.getY());

        double distanceInRadians = distance / 6371; //earth's radius is 6371 kms
        double newLat = lat + rand.nextDouble() * distanceInRadians;
        double newLon = lon + rand.nextDouble() * distanceInRadians;

        return new Geolocation(Math.toDegrees(newLat), Math.toDegrees(newLon));
    }

    public static String getOutwardCodeFromGeolocation(Geolocation location) throws IOException, InterruptedException {
        String uri = "https://api.postcodes.io/outcodes?lon=" + location.getY() + "&lat=" + location.getX() + "&limit=1";
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder().uri(URI.create(uri)).build();
        HttpResponse<String> response =
                client.send(request, HttpResponse.BodyHandlers.ofString());

        JsonObject jsonObject = new JsonParser().parse(response.body()).getAsJsonObject();
        String outwardCode = jsonObject.getAsJsonArray("result").getAsJsonArray().get(0).getAsJsonObject().get("outcode").getAsString().substring(0, 2);
        return outwardCode;
    }

    public static Geolocation generateGeolocationInArea(String postcode) throws IOException, InterruptedException {
        String outwardCode;
        Geolocation location;
        Random rand = new Random();
        do {
            location = new Geolocation(rand.nextFloat() * 0.44 + 51.28, rand.nextFloat() * 0.79 - 0.52);
            String uri = "https://api.postcodes.io/outcodes?lon=" + location.getY() + "&lat=" + location.getX() + "&limit=1";
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder().uri(URI.create(uri)).build();
            HttpResponse<String> response =
                    client.send(request, HttpResponse.BodyHandlers.ofString());

            JsonObject jsonObject = new JsonParser().parse(response.body()).getAsJsonObject();
            if (jsonObject.get("result").isJsonNull()) {
                outwardCode = "";
            } else {
                outwardCode = jsonObject.getAsJsonArray("result").getAsJsonArray().get(0).getAsJsonObject().get("outcode").getAsString().substring(0, 2);
                if (Character.isDigit(outwardCode.charAt(1))) {
                    outwardCode = outwardCode.substring(0, 1);
                }
            }
        } while (!outwardCode.equals(postcode));
        return location;
    }

    public static String getPostcodeFromLocation(Geolocation location) throws IOException, InterruptedException {
        String uri = "https://api.postcodes.io/postcodes?lon=" + location.getY() + "&lat=" + location.getX() + "&limit=1";
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder().uri(URI.create(uri)).build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        JsonObject jsonObject = new JsonParser().parse(response.body()).getAsJsonObject();
        if (jsonObject.get("result").isJsonNull()) {
            return null;
        } else {
            return jsonObject.getAsJsonArray("result").getAsJsonArray().get(0).getAsJsonObject().get("postcode").getAsString();
        }
    }

    public static void generateCPsInArea(List<ChargingPoint> cps, String outcode, int amount) throws IOException, InterruptedException {
        Random rand = new Random();
        final int[] priceConstraints = new int[]{0, 5, 10};

        Map<Geolocation, String> locationsPostcodes = bulkReverseGeocoding(amount, outcode);
        List<Geolocation> keys = new ArrayList<Geolocation>(locationsPostcodes.keySet());

        printWriter.println("GENERATED CPS IN " + outcode + " AREA");

        int no = 0;
        while (no < amount) {
            Geolocation location = keys.get(no);
            String postcode = locationsPostcodes.get(location);

            if (postcode != null && postcode.startsWith(outcode)) {
                cps.add(new ChargingPoint(location,
                        SocketType.values()[rand.nextInt(6)],
                        ChargingType.getRandomChargingType(),
                        priceConstraints[rand.nextInt(2)],
                        Status.AVAILABLE));
//                    Status.values()[rand.nextInt(3)]));
                cps.get(cps.size() - 1).setPostcode(postcode);
                cps.get(cps.size() - 1).setIndex(++ChargingPoint.lastIndex);
                cps.get(cps.size() - 1).printCP();
                printWriter.println();
                no++;
            }
        }
    }

    public static HashMap<String, Integer> getCpAreas(List<ChargingPoint> cps) {
        HashMap<String, Integer> cpAreas = new HashMap<>();

        int e = 0;
        int ec = 0;
        int n = 0;
        int nw = 0;
        int se = 0;
        int sw = 0;
        int w = 0;
        int wc = 0;

        int en = 0;
        int ha = 0;
        int ub = 0;
        int tw = 0;
        int kt = 0;
        int sm = 0;
        int cr = 0;
        int br = 0;
        int da = 0;
        int rm = 0;
        int ig = 0;
        int tn = 0;
        int other = 0;

        for (ChargingPoint cp : cps) {
            String pc = cp.getPostcode();
            if (pc.startsWith("EC")) {
                ec++;
            } else if (pc.startsWith("EN")) {
                en++;
            } else if (pc.startsWith("E")) {
                e++;
            } else if (pc.startsWith("NW")) {
                nw++;
            } else if (pc.startsWith("N")) {
                n++;
            } else if (pc.startsWith("SE")) {
                se++;
            } else if (pc.startsWith("SW")) {
                sw++;
            } else if (pc.startsWith("WC")) {
                wc++;
            } else if (pc.startsWith("W")) {
                w++;
            } else if (pc.startsWith("HA")) {
                ha++;
            } else if (pc.startsWith("UB")) {
                ub++;
            } else if (pc.startsWith("TW")) {
                tw++;
            } else if (pc.startsWith("KT")) {
                kt++;
            } else if (pc.startsWith("SM")) {
                sm++;
            } else if (pc.startsWith("CR")) {
                cr++;
            } else if (pc.startsWith("BR")) {
                br++;
            } else if (pc.startsWith("DA")) {
                da++;
            } else if (pc.startsWith("RM")) {
                rm++;
            } else if (pc.startsWith("IG")) {
                ig++;
            } else if (pc.startsWith("TN")) {
                tn++;
            } else {
                other++;
            }
        }

        cpAreas.put("EC", ec);
        cpAreas.put("E", e);
        cpAreas.put("NW", nw);
        cpAreas.put("N", n);
        cpAreas.put("SE", se);
        cpAreas.put("SW", sw);
        cpAreas.put("WC", wc);
        cpAreas.put("W", w);
        cpAreas.put("EN", en);
        cpAreas.put("HA", ha);
        cpAreas.put("UB", ub);
        cpAreas.put("TW", tw);
        cpAreas.put("KT", kt);
        cpAreas.put("SM", sm);
        cpAreas.put("CR", cr);
        cpAreas.put("BR", br);
        cpAreas.put("DA", da);
        cpAreas.put("RM", rm);
        cpAreas.put("IG", ig);
        cpAreas.put("TN", tn);
//        cpAreas.put("other", other);

        cpAreas.forEach((k,v) -> System.out.println(k + " " + v));
//            try {
//                generateCPsInArea(cps, k, 5);
//            } catch (IOException | InterruptedException ex) {
//                ex.printStackTrace();
//            }
//        });

        return cpAreas;
    }

    public static String generateGeolocations(int number) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\"geolocations\" : [");
        for (int i = 0; i < number; i++) {
            Random rand = new Random();
            Geolocation location = new Geolocation(rand.nextFloat() * 0.44 + 51.28, rand.nextFloat() * 0.79 - 0.52);
            String loc = "{\"longitude\": " + location.getY() + ", \"latitude\": " + location.getX() + "}";
            sb.append(loc);
            sb.append(", ");
        }
        String body = sb.toString().substring(0, sb.toString().length() - 2) + "]}";
        return body;
    }

    public static Map<Geolocation, String> bulkReverseGeocoding(int amount, String outcode) throws IOException, InterruptedException {
        Map<Geolocation, String> geolocationsPostcodes = new HashMap<>();
        int requestAmount = amount;
        if (amount > 100) {
            requestAmount = 100;
        }

        do {
            String body = generateGeolocations(requestAmount);
            String uri = "https://api.postcodes.io/postcodes";


            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(uri))
                    .headers("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(body))
                    .build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

//            System.out.println(response.body());
            JsonObject jsonObject = new JsonParser().parse(response.body()).getAsJsonObject();
            if (!jsonObject.get("result").isJsonNull()) {
                JsonArray res = jsonObject.getAsJsonArray("result");

                for (int i = 0; i < res.size(); i++) {
                    JsonObject query = res.get(i).getAsJsonObject().getAsJsonObject("query");
                    double longitude = query.get("longitude").getAsDouble();
                    double latitude = query.get("latitude").getAsDouble();

                    if (!res.get(i).getAsJsonObject().get("result").isJsonNull()) {
                        JsonArray result = res.get(i).getAsJsonObject().getAsJsonArray("result");
                        String postcode = result.get(0).getAsJsonObject().get("postcode").getAsString();
                        if (postcode.startsWith(outcode)) {
                            geolocationsPostcodes.put(new Geolocation(latitude, longitude), postcode);
                            System.out.println(latitude + ", " + longitude + ", " + postcode);
                        }
                        if (geolocationsPostcodes.size() >= amount) {
                            break;
                        }
                    }
                }
            }
        } while (geolocationsPostcodes.size() < amount);

        return geolocationsPostcodes;
    }
}

