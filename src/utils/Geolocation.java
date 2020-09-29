/*
 * Project: Evo-Sim
 * Developed by: Irina Danes
 */

package utils;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class Geolocation {
    private final double x;
    private final double y;

    public Geolocation(double x, double y) {
        this.x = x;
        this.y = y;
    }

    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

    public static double getDistance(Geolocation l1, Geolocation l2) {
        double lat1 = l1.getX();
        double lon1 = l1.getY();
        double lat2 = l2.getX();
        double lon2 = l2.getY();
        if ((lat1 == lat2) && (lon1 == lon2)) {
            return 0;
        } else {
            double theta = lon1 - lon2;
            double dist = Math.sin(Math.toRadians(lat1)) * Math.sin(Math.toRadians(lat2)) +
                    Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                            Math.cos(Math.toRadians(theta));
            dist = Math.acos(dist);
            dist = Math.toDegrees(dist);
            dist = dist * 60 * 1.1515;  // dist in MILES
            dist = dist * 1.609344;  // dist in KMS
            return Math.round(dist * 100.0) / 100.0;
        }
    }

    public static String getPostcode(Geolocation location) throws IOException, InterruptedException {
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

    public static String getOutwardCode(Geolocation location) throws IOException, InterruptedException {
        String uri = "https://api.postcodes.io/outcodes?lon=" + location.getY() + "&lat=" + location.getX() + "&limit=1";
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder().uri(URI.create(uri)).build();
        HttpResponse<String> response =
                client.send(request, HttpResponse.BodyHandlers.ofString());

        JsonObject jsonObject = new JsonParser().parse(response.body()).getAsJsonObject();
        int length = 2;
        String postcode = jsonObject.getAsJsonArray("result").getAsJsonArray().get(0).getAsJsonObject().get("outcode").getAsString();
        if (Character.isDigit(postcode.charAt(1))) {
            length = 1;
        }
        return postcode.substring(0, length);
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
    
    public static String generateRandomGeolocations(int number) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\"geolocations\" : [");
        for (int i = 0; i < number; i++) {
            Random rand = new Random();
            Geolocation location = new Geolocation(rand.nextFloat() * 0.44 + 51.28, rand.nextFloat() * 0.79 - 0.52);
            String loc = "{\"longitude\": " + location.getY() + ", \"latitude\": " + location.getX() + "}";
            sb.append(loc);
            sb.append(", ");
        }
        return sb.toString().substring(0, sb.toString().length() - 2) + "]}";
    }

    public static Map<Geolocation, String> bulkReverseGeocoding(int amount, String outcode) throws IOException, InterruptedException {
        Map<Geolocation, String> geolocationsPostcodes = new HashMap<>();
        int requestAmount = amount;
        if (amount > 100) {
            requestAmount = 100;
        }

        do {
            String body = generateRandomGeolocations(requestAmount);
            String uri = "https://api.postcodes.io/postcodes";


            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(uri))
                    .headers("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(body))
                    .build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

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

    public String printGeolocation() {
        return "(" + this.getX() + ", " + this.getY() + ")";
    }
}
