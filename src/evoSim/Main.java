/*
 * Project: Evo-Sim
 * Developed by: Irina Danes
 */

package evoSim;

import chargingInfrastructure.Status;
import chargingStation.ChargingPoint;
import electricVehicle.ElectricVehicle;
import utils.*;

import java.io.*;
import java.text.ParseException;
import java.util.*;

import static chargingDemand.DemandGenerator.*;
import static evoSim.Dynamic.*;
import static evoSim.Static.*;
import static chargingInfrastructure.SupplyGenerator.*;
import static utils.Statistics.*;

public class Main {

    static final double willingToPayPercentage = 100.0;

    static final List<Double> randomDistances = new ArrayList<>();
    static final List<Double> greedyDistances = new ArrayList<>();
    static final List<Double> topkDistances = new ArrayList<>();
    static final List<Double> dynamicDistances = new ArrayList<>();

    static boolean distanceConstraint = false;
    static boolean timeConstraint = false;

    static final HashMap<ChargingPoint, Status> map = new HashMap<>();
    public static FileWriter fileWriter;
    public static PrintWriter printWriter;

    public static void main(String[] args) throws IOException, InterruptedException, ParseException {

        int numberOfExperiments = Integer.parseInt(args[0]);
        int[] experiments = new int[numberOfExperiments];
        for (int i = 1; i <= numberOfExperiments; i++) {
            experiments[i - 1] = Integer.parseInt(args[i]);
        }
        String date = args[numberOfExperiments + 1];
        String time = args[numberOfExperiments + 2];

        String time_distance = "none";
        if (args.length > numberOfExperiments + 3) {
            time_distance = args[numberOfExperiments + 3];
            if (args.length > numberOfExperiments + 4) {
                time_distance = "both";
            }

            switch (time_distance) {
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
        }

        for (int number : experiments) {
            try {
                fileWriter = new FileWriter("results_" + number + "_" + date + "_" + time + "_" + time_distance + ".txt");
            } catch (IOException e) {
                e.printStackTrace();
            }
            printWriter = new PrintWriter(fileWriter);

            randomDistances.clear();
            greedyDistances.clear();
            topkDistances.clear();
            dynamicDistances.clear();
            OptimalSolution.binPackingDistances.clear();

            List<ChargingPoint> cps = new ArrayList<>();
            List<ElectricVehicle> evs = new ArrayList<>();

            long random_execution_time;
            long greedy_execution_time;
            long topk_execution_time;
            long dynamic_execution_time;
            long optimal_execution_times;

//            ElectricVehicle.printEVheadings();
//            readEVsFromFile(evs,"data/correct" + number + ".txt");
            generateEVs(evs, number, willingToPayPercentage);
            evs.sort(Comparator.comparingDouble(ElectricVehicle::getWaitTime));
//            for (ElectricVehicle ev : evs) {
//                ev.printEV();
//                printWriter.println();
//            }

//            ChargingPoint.printCPheadings();
            generateCPfromFile(cps, date + " " + time);


            System.out.println(evs.size() + " EVs, " + cps.size() + " CPs.");
            printWriter.println(evs.size() + " EVs, " + cps.size() + " CPs.");
            printWriter.println();


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
            topKMap(evs, cps);
            endTime = System.currentTimeMillis();
            topk_execution_time = endTime - startTime;

            for (ChargingPoint cp : cps) {
                map.put(cp, cp.getStatus());
            }

//            startTime = System.currentTimeMillis();
//            System.out.println("Running optimal algorithm");
//            optimisation(cps, evs);
//            endTime = System.currentTimeMillis();
//            optimal_execution_times = endTime - startTime;

            startTime = System.currentTimeMillis();
            System.out.println("Running scheduling algorithm - dynamic version");
            schedule(evs, cps, 0);
            endTime = System.currentTimeMillis();
            dynamic_execution_time = endTime - startTime;


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
            printWriter.println("Allocated: " + Math.round((double) topkDistances.size() / number * 100 * 100.0) / 100.0 + "% (" + topkDistances.size() + "/" + number + ")");
            computeStatistics(topkDistances, printWriter);
//            printUnallocatedEVs(Static.unallocatedEVs);
            printWriter.println();
            printWriter.println();

            printWriter.println("Dynamic: (in kms)");
            printWriter.println("Allocated: " + Math.round((double) dynamicDistances.size() / number * 100 * 100.0) / 100.0 + "% (" + dynamicDistances.size() + "/" + number + ")");
            computeStatistics(dynamicDistances, printWriter);
            printWriter.println("Time: (in minutes)");
            computeStatistics(times, printWriter);
//            printUnallocatedEVs(Dynamic.unallocatedEVs);
            printWriter.println();
            printWriter.println();


//            printWriter.println("Optimal: ");
//            printWriter.println("Allocated: " + Math.round((double) OptimalSolution.binPackingDistances.size() / number * 100 * 100.0) / 100.0 + "% (" + OptimalSolution.binPackingDistances.size() + "/" + number + ")");
//            computeStatistics(OptimalSolution.binPackingDistances, printWriter);


            printWriter.println("Random distances:");
            printWriter.println(randomDistances);
            printWriter.println("Greedy distances:");
            printWriter.println(greedyDistances);
            printWriter.println("Top-k distances:");
            printWriter.println(topkDistances);

//            printWriter.println("Optimal distances:");
//            printWriter.println(OptimalSolution.binPackingDistances);
            printWriter.println();
            printWriter.println("Dynamic distances:");
            printWriter.println(dynamicDistances);
            printWriter.println("Dynamic times:");
            printWriter.println(times);

            printWriter.println();
            printWriter.println("Execution times: ");
            printWriter.println("Random: " + random_execution_time);
            printWriter.println("Greedy: " + greedy_execution_time);
            printWriter.println("Top-k: " + topk_execution_time);
            printWriter.println("Dynamic: " + dynamic_execution_time);
//            printWriter.println("Optimal: " + optimal_execution_times);

            ElectricVehicle.lastIndex = 0;
            ChargingPoint.lastIndex = 0;
            fileWriter.close();
        }

        printWriter.close();
    }

    public static void optimisation(List<ChargingPoint> cps, List<ElectricVehicle> evs) {
        OptimalSolution.optimal(cps, evs);
    }

    public static boolean match(ChargingPoint cp, ElectricVehicle ev) {
        return map.get(cp) == Status.AVAILABLE &&
                cp.getChargingType() == ev.getChargingType() &&
                ((cp.getPrice() > 0 && ev.getWillingToPay()) || (cp.getPrice() == 0))
                && (!distanceConstraint || Geolocation.getDistance(cp.getLocation(), ev.getDestination()) <= ev.getDistanceConstraint());
    }

}