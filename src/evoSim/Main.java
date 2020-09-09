package evoSim;

import java.io.*;
import java.text.ParseException;
import java.util.*;

import chargingStation.ChargingPoint;
import chargingStation.Geolocation;
import chargingStation.Status;
import scheduler.OptimalSolution;
import vehicle.ElectricVehicle;

import static scheduler.Dynamic.*;
import static scheduler.Static.*;
import static scheduler.OptimalSolution.*;
import static chargingDemand.DemandGenerator.*;
import static chargingInfrastructure.SupplyGenerator.*;
import static chargingStation.Statistics.*;

public class Main {

    static final double willingToPayPercentage = 100.0;

    public static final List<Double> randomDistances = new ArrayList<>();
    public static final List<Double> greedyDistances = new ArrayList<>();
    public static final List<Double> heuristicDistances3 = new ArrayList<>();
    public static final List<Double> dynamicDistances = new ArrayList<>();

    public static boolean distanceConstraint = false;
    public static boolean timeConstraint = false;

    // TODO: remove map (used to store initial status of CPs to evaluate all 3 approaches
    //  because after allocating the EV, its status changes to UNAVAILABLE.

    public static final Map<ChargingPoint, Status> map = new HashMap();
    public static FileWriter fileWriter;
    public static PrintWriter printWriter;

    public static void main(String[] args) throws IOException, InterruptedException, ParseException {
    	   	
    	String directory = args[0];
    	
    	String nbEvsParameter = args[1];
    	String[] nbEvsList = nbEvsParameter.split(";");
        int[] experiments = new int[nbEvsList.length];
        for (int i = 0; i < nbEvsList.length; i++) {
            experiments[i] = Integer.parseInt(nbEvsList[i]);
        }
        String date = args[2];
        String time = args[3];
        
        String constraint = args[4];
        switch (constraint) {
                case "distance":
                    distanceConstraint = true;
                    break;
                case "time":
                    timeConstraint = true;
                    break;
                case "both":
                    distanceConstraint = true;
                    timeConstraint = true;
                    break;
        }
         
        for (int number : experiments) {
        	
        	System.out.println(number);
        	
            try {
            	fileWriter = new FileWriter("results_" + number + "_" + 
            						date + "_" + 
            						time.replace(":", "") + "_" + 
            						constraint + ".txt");
            } catch (IOException e) {
            	e.printStackTrace();
            }
            printWriter = new PrintWriter(fileWriter);

            randomDistances.clear();
            greedyDistances.clear();
            heuristicDistances3.clear();
            dynamicDistances.clear();
//            OptimalSolution.binPackingDistances.clear();

            List<ChargingPoint> cps = new ArrayList<>();
            List<ElectricVehicle> evs = new ArrayList<>();

            Long random_execution_time;
            Long greedy_execution_time;
            Long topk_execution_time;
            Long dynamic_execution_time;

//            ElectricVehicle.printEVheadings();
//            readEVsFromFile(evs,"data/correct" + number + ".txt");
            generateEVs(evs, number, willingToPayPercentage);
            evs.sort(Comparator.comparingDouble(ElectricVehicle::getWaitTime));
//            for (ElectricVehicle ev : evs) {
//                ev.printEV();
//                printWriter.println();
//            }

//            ChargingPoint.printCPheadings();
            generateCPfromFile(directory, cps, date + " " + time);

            System.out.println(evs.size() + " EVs, " + cps.size() + " CPs.");

            printWriter.println(evs.size() + " EVs, " + cps.size() + " CPs.");
            printWriter.println();

//            generateCPs(cps, 8000);

//            HashMap<String, Integer> cpareasmap = getCpAreas(cps);
//            cpareasmap.forEach((k,v) -> {
//                try {
//                generateCPsInArea(cps, k, v);
//            } catch (IOException | InterruptedException ex) {
//                ex.printStackTrace();
//            }
//        });
//
////            generateCPsInArea(cps, "SW", 100);
//            getCpAreas(cps);


            for (ChargingPoint cp : cps) {
                map.put(cp, cp.getStatus());
            }

            long startTime = System.currentTimeMillis();
            System.out.println("Running random algorithm - static version");
            randomMap(evs, cps);
            long endTime = System.currentTimeMillis();
            random_execution_time = endTime - startTime;


            for (ChargingPoint cp : cps) {
                map.put(cp, cp.getStatus());
            }

            startTime = System.currentTimeMillis();
            System.out.println("Running greedy algorithm - static version");
            greedyMap(evs, cps);
            endTime = System.currentTimeMillis();
            greedy_execution_time = endTime - startTime;


            for (ChargingPoint cp : cps) {
                map.put(cp, cp.getStatus());
            }

            startTime = System.currentTimeMillis();
            System.out.println("Running top-k algorithm - static version");
            heuristicMap(evs, cps);
            endTime = System.currentTimeMillis();
            topk_execution_time = endTime - startTime;


            for (ChargingPoint cp : cps) {
                map.put(cp, cp.getStatus());
            }

            startTime = System.currentTimeMillis();
            System.out.println("Running scheduling algorithm - dynamic version");
            schedule(evs, cps, 0);
            endTime = System.currentTimeMillis();
            dynamic_execution_time = endTime - startTime;

//            startTime = System.currentTimeMillis();
//            optimisation(cps, evs);
//            endTime = System.currentTimeMillis();
//            optimal_execution_times.add(endTime - startTime);


            printWriter.println("Random: (in kms)");
            printWriter.println("Allocated: " + Math.round((double) randomDistances.size() / number * 100 * 100.0) / 100.0 + "% (" + randomDistances.size() + "/" + number + ")");
            computeStatistics(randomDistances, printWriter);
            printWriter.println();
            printWriter.println();

            printWriter.println("Greedy: (in kms)");
            printWriter.println("Allocated: " + Math.round((double) greedyDistances.size() / number * 100 * 100.0) / 100.0 + "% (" + greedyDistances.size() + "/" + number + ")");
            computeStatistics(greedyDistances, printWriter);
            printWriter.println();
            printWriter.println();

            printWriter.println("Top-k: (in kms)");
            printWriter.println("Allocated: " + Math.round((double) heuristicDistances3.size() / number * 100 * 100.0) / 100.0 + "% (" + heuristicDistances3.size() + "/" + number + ")");
            computeStatistics(heuristicDistances3, printWriter);
//            printUnallocatedEVs(Static.unallocatedEVs);
            printWriter.println();
            printWriter.println();

            printWriter.println("Dynamic: (in kms)");
            printWriter.println("Allocated: " + Math.round((double) dynamicDistances.size() / number * 100 * 100.0) / 100.0 + "% (" + dynamicDistances.size() + "/" + number + ")");
            computeStatistics(dynamicDistances, printWriter);
            printWriter.println("Time: (in minutes)");
            computeStatistics(max, printWriter);
//            printUnallocatedEVs(Dynamic.unallocatedEVs);
            printWriter.println();
            printWriter.println();


//            printWriter.println("Optimal: ");
//            printWriter.println("Allocated: " + Math.round((double) OptimalSolution.binPackingDistances.size() / number * 100 * 100.0) / 100.0 + "% (" + OptimalSolution.binPackingDistances.size() + "/" + number + ")");
//            computeStatistics(OptimalSolution.binPackingDistances);


            printWriter.println("Random distances:");
            printWriter.println(randomDistances);
            printWriter.println("Greedy distances:");
            printWriter.println(greedyDistances);
            printWriter.println("Top-k distances:");
            printWriter.println(heuristicDistances3);

            printWriter.println();
            printWriter.println("Execution times: ");
            printWriter.println("Random: " + random_execution_time);
            printWriter.println("Greedy: " + greedy_execution_time);
            printWriter.println("Top-k: " + topk_execution_time);
            printWriter.println("Dynamic: " + dynamic_execution_time);

//            Process p = Runtime.getRuntime().exec("python3 /home/ubuntu/Desktop/ev_project/src/ev_project/plots.py");
//            int exitVal = p.waitFor();

            ElectricVehicle.lastIndex = 0;
            ChargingPoint.lastIndex = 0;
            fileWriter.close();
        }

        printWriter.close();
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

    public static void optimisation(List<ChargingPoint> cps, List<ElectricVehicle> evs) {
        OptimalSolution.optimal(cps, evs);
    }

    public static boolean match(ChargingPoint cp, ElectricVehicle ev) {
        return map.get(cp) == Status.AVAILABLE &&
                cp.getChargingType() == ev.getChargingType() &&
                ((cp.getPrice() > 0 && ev.getWillingToPay()) || (cp.getPrice() == 0))
                && (!distanceConstraint || getDistance(cp.getLocation(), ev.getDestination()) <= ev.getDistanceConstraint());
    }

}
