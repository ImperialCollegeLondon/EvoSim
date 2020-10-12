/*
 * Project: Evo-Sim
 * Developed by: Irina Danes
 */

package evoSim;

import chargingStation.ChargingPoint;
import electricVehicle.ElectricVehicle;
import chargingInfrastructure.Status;
import utils.Geolocation;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import static evoSim.Main.*;
import static utils.Geolocation.getOutwardCode;

public class Static {
    public static HashMap<String, Integer> unallocatedEVs = new HashMap<>();

    public static void randomMap(List<ElectricVehicle> evs, final List<ChargingPoint> cps) {
        for (ElectricVehicle ev : evs) {
            double distance;
            ChargingPoint result = randomMapEVtoCP(cps, ev);
            if (result == null) {
//                printWriter.println(ev.getIndex() + "  No available charging points");
            } else {
//                ev.printEV();
//                printWriter.print(" -> ");
//                result.printCP();
                distance = Geolocation.getDistance(ev.getDestination(), result.getLocation());
                randomDistances.add(distance);
//                printWriter.print(" (distance: " + distance + ") ");
                map.put(result, Status.UNAVAILABLE);
            }
//            printWriter.println(" (random)");
        }
    }


    public static ChargingPoint randomMapEVtoCP(List<ChargingPoint> cps, ElectricVehicle ev) {
        Random rand = new Random();
        boolean matched = false;
        for (ChargingPoint cp : cps) {
            if (match(cp, ev)) {
                matched = true;
            }
        }
        if (!matched) {
            return null;
        } else {
            ChargingPoint cp = cps.get(rand.nextInt(cps.size()));
            while (!match(cp, ev)) {
                cp = cps.get(rand.nextInt(cps.size()));
            }
            return cp;
        }
    }

    public static void greedyMap(List<ElectricVehicle> evs, final List<ChargingPoint> cps) {
        for (ElectricVehicle ev : evs) {
            double distance;
            ChargingPoint result = greedyMapEVtoCP(cps, ev);
            if (result == null) {
//                printWriter.println(ev.getIndex() + "  No available charging points");
            } else {
//                ev.printEV();
//                printWriter.print(" -> ");
//                result.printCP();
                distance = Geolocation.getDistance(ev.getDestination(), result.getLocation());
                greedyDistances.add(distance);
//                printWriter.print(" (distance: " + distance + ") ");
                map.put(result, Status.UNAVAILABLE);
            }
//            printWriter.println(" (greedy)");
        }
    }

    public static ChargingPoint greedyMapEVtoCP(List<ChargingPoint> cps, ElectricVehicle ev) {
        ChargingPoint closestCP = null;
        double min = Double.MAX_VALUE;
        for (ChargingPoint cp : cps) {
            double dist = Geolocation.getDistance(cp.getLocation(), ev.getDestination());
            if (dist < min && match(cp, ev)) {
                min = dist;
                closestCP = cp;
            }
        }
        return closestCP;
    }

    public static void topKMap(List<ElectricVehicle> evs, List<ChargingPoint> cps) throws IOException, InterruptedException {
        Map<ElectricVehicle, ChargingPoint> evCp = new HashMap<>();
        for (ElectricVehicle ev : evs) {
            ChargingPoint result = greedyMapEVtoCP(cps, ev);

            if (result == null) {
//                printWriter.println(ev.getIndex() + "  No available charging points");
            } else {
                evCp.put(ev, result);
                map.put(result, Status.UNAVAILABLE);
            }
        }

        for (ChargingPoint cp : cps) {
            map.put(cp, cp.getStatus());
        }

        for (int k = 0; k < 3; k++) {
            for (int j = 0; j < evs.size() - 1; j++) {
                ElectricVehicle ev1 = evs.get(j);
                if (evCp.containsKey(ev1)) {
                    ChargingPoint cp1 = evCp.get(ev1);
                    for (int i = j + 1; i < evs.size(); i++) {
                        ElectricVehicle ev2 = evs.get(i);
                        if (evCp.containsKey(ev2)) {
                            ChargingPoint cp2 = evCp.get(ev2);
                            double initialSum = Geolocation.getDistance(cp1.getLocation(), ev1.getDestination()) + Geolocation.getDistance(cp2.getLocation(), ev2.getDestination());
                            double newSum = Geolocation.getDistance(cp1.getLocation(), ev2.getDestination()) + Geolocation.getDistance(cp2.getLocation(), ev1.getDestination());

                            if (match(cp2, ev1) && match(cp1, ev2) && newSum < initialSum) {
                                evCp.put(ev1, cp2);
                                evCp.put(ev2, cp1);
                                break;
                            }
                        }
                    }
                }
            }
        }


        for (Map.Entry<ElectricVehicle, ChargingPoint> entry : evCp.entrySet()) {
            ElectricVehicle ev = entry.getKey();
            ChargingPoint result = entry.getValue();

//            ev.printEV();
//            printWriter.print(" -> ");
//            result.printCP();
            double distance = Geolocation.getDistance(ev.getDestination(), result.getLocation());
            topkDistances.add(distance);
//            printWriter.print(" (distance: " + distance + ") ");
//            printWriter.println(" (topk)");
        }

//        countUnallocatedEVs(evs, evCp, unallocatedEVs);
    }

    public static void countUnallocatedEVs(List<ElectricVehicle> evs, Map<ElectricVehicle, ChargingPoint> evCp,
                                           HashMap<String, Integer> unallocatedEVs) throws IOException, InterruptedException {
        int unallocated_e = 0;
        int unallocated_ec = 0;
        int unallocated_n = 0;
        int unallocated_nw = 0;
        int unallocated_se = 0;
        int unallocated_sw = 0;
        int unallocated_w = 0;
        int unallocated_wc = 0;

        int unallocated_en = 0;
        int unallocated_ha = 0;
        int unallocated_ub = 0;
        int unallocated_tw = 0;
        int unallocated_kt = 0;
        int unallocated_sm = 0;
        int unallocated_cr = 0;
        int unallocated_br = 0;
        int unallocated_da = 0;
        int unallocated_rm = 0;
        int unallocated_ig = 0;
        int unallocated_tn = 0;
        int unallocated_wd = 0;

        int unallocated_total = 0;

        for (ElectricVehicle electricv : evs) {
            if (!evCp.containsKey(electricv)) {
                unallocated_total++;
                String pc_ev = getOutwardCode(electricv.getDestination());
                switch (pc_ev) {
                    case "EC":
                        unallocated_ec++;
                        break;
                    case "EN":
                        unallocated_en++;
                        break;
                    case "E":
                        unallocated_e++;
                        break;
                    case "NW":
                        unallocated_nw++;
                        break;
                    case "N":
                        unallocated_n++;
                        break;
                    case "SE":
                        unallocated_se++;
                        break;
                    case "SW":
                        unallocated_sw++;
                        break;
                    case "WC":
                        unallocated_wc++;
                        break;
                    case "W":
                        unallocated_w++;
                        break;
                    case "HA":
                        unallocated_ha++;
                        break;
                    case "UB":
                        unallocated_ub++;
                        break;
                    case "TW":
                        unallocated_tw++;
                        break;
                    case "KT":
                        unallocated_kt++;
                        break;
                    case "SM":
                        unallocated_sm++;
                        break;
                    case "CR":
                        unallocated_cr++;
                        break;
                    case "BR":
                        unallocated_br++;
                        break;
                    case "DA":
                        unallocated_da++;
                        break;
                    case "RM":
                        unallocated_rm++;
                        break;
                    case "IG":
                        unallocated_ig++;
                        break;
                    case "TN":
                        unallocated_tn++;
                        break;
                    default:
                        unallocated_wd++;
                        break;
                }
            }
        }

        unallocatedEVs.put("total", unallocated_total);

        unallocatedEVs.put("EC", unallocated_ec);
        unallocatedEVs.put("E", unallocated_e);
        unallocatedEVs.put("NW", unallocated_nw);
        unallocatedEVs.put("N", unallocated_n);
        unallocatedEVs.put("SE", unallocated_se);
        unallocatedEVs.put("SW", unallocated_sw);
        unallocatedEVs.put("WC", unallocated_wc);
        unallocatedEVs.put("W", unallocated_w);
        unallocatedEVs.put("EN", unallocated_en);
        unallocatedEVs.put("HA", unallocated_ha);
        unallocatedEVs.put("UB", unallocated_ub);
        unallocatedEVs.put("TW", unallocated_tw);
        unallocatedEVs.put("KT", unallocated_kt);
        unallocatedEVs.put("SM", unallocated_sm);
        unallocatedEVs.put("CR", unallocated_cr);
        unallocatedEVs.put("BR", unallocated_br);
        unallocatedEVs.put("DA", unallocated_da);
        unallocatedEVs.put("RM", unallocated_rm);
        unallocatedEVs.put("IG", unallocated_ig);
        unallocatedEVs.put("TN", unallocated_tn);
        unallocatedEVs.put("WD", unallocated_wd);
    }

    public static void printUnallocatedEVs(HashMap<String, Integer> unallocatedEVs) {
        printWriter.println();
        printWriter.println("Unallocated EVs:");
        for (Map.Entry<String, Integer> entry : unallocatedEVs.entrySet()) {
            printWriter.println(entry.getKey() + ": " + entry.getValue());
        }
    }

}