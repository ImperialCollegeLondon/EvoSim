/*
 * Project: Evo-Sim
 * Developed by: Irina Danes
 */

package experiments.heatmap;

import java.io.*;

public class Locations {

    public static void main(String[] args) throws IOException {
        File stations = new File("../data/stations");
        BufferedReader br2 = new BufferedReader(new FileReader(stations));
        String st2;

        FileWriter fileWriter = new FileWriter("geolocations.csv");
        PrintWriter printWriter = new PrintWriter(fileWriter);
        printWriter.println("Latitude,Longitude");
        while ((st2 = br2.readLine()) != null) {
            String[] station_data = st2.split("\\s+");
            String l = station_data[1];
            String r = station_data[2];
            if (Double.parseDouble(l) < 51.7 && Double.parseDouble(r) > -1) {
                printWriter.println(l + "," + r);
            }
        }
    }
}
