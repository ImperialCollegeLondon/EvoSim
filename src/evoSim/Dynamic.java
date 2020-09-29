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
import java.util.*;

import static evoSim.Main.*;
import static evoSim.Static.greedyMapEVtoCP;

public class Dynamic {
    public static final List<Double> times = new ArrayList<>();
    public static HashMap<String, Integer> unallocatedEVs = new HashMap<>();
    static int unallocated = 0;

    public static void schedule(List<ElectricVehicle> evs, List<ChargingPoint> cps, double requestTime) throws IOException, InterruptedException {
        Map<ElectricVehicle, ChargingPoint> evCp = new HashMap<>();
        evs.sort(Comparator.comparingDouble(ElectricVehicle::getWaitTime));

        double[][] est = new double[evs.size() + 2][cps.size() + 2];
        for (ElectricVehicle ev : evs) {
            for (ChargingPoint cp : cps) {
                if (!match(cp, ev)) {
                    est[ev.getIndex()][cp.getIndex()] = -1;
                } else {
                    double arrivalTime = requestTime + Geolocation.getDistance(ev.getOrigin(), cp.getLocation()) * 6 / 5;
                    est[ev.getIndex()][cp.getIndex()] = arrivalTime;
                }
            }
        }

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

            times.add(0.0);

//            ev.printEV();
//            printWriter.print(" -> ");
//            result.printCP();
            double distance = Geolocation.getDistance(ev.getDestination(), result.getLocation());
            dynamicDistances.add(distance);
//            printWriter.print(" (distance: " + distance + ") ");
//            printWriter.println(" (topk)");

            for (ElectricVehicle ev2 : evs) {
                if (est[ev2.getIndex()][result.getIndex()] != -1) {
                    est[ev2.getIndex()][result.getIndex()] = Math.max(est[ev.getIndex()][result.getIndex()] + ev.timeToCharge() * 60, requestTime + Geolocation.getDistance(ev2.getOrigin(), result.getLocation()) * 6 / 5);
                }
            }
            evs.remove(ev);
        }

        ElectricVehicle nextEv;
        ChargingPoint nextCp;

        do {
            double min = Double.MAX_VALUE;
            double minDist = Double.MAX_VALUE;
            nextEv = null;
            nextCp = null;

            for (ElectricVehicle ev : evs) {
                for (ChargingPoint cp : cps) {
                    if (est[ev.getIndex()][cp.getIndex()] != -1 && est[ev.getIndex()][cp.getIndex()] <= min &&
                            Geolocation.getDistance(ev.getDestination(), cp.getLocation()) <= minDist
                            && (!timeConstraint || ev.getWaitTime() >= est[ev.getIndex()][cp.getIndex()] - Geolocation.getDistance(ev.getOrigin(), cp.getLocation()) * 6 / 5)) {
                        min = est[ev.getIndex()][cp.getIndex()];
                        minDist = Geolocation.getDistance(ev.getDestination(), cp.getLocation());

                        nextEv = ev;
                        nextCp = cp;
                    }
                }
            }

            if (nextEv != null) {
                evCp.put(nextEv, nextCp);
                evs.remove(nextEv);

                times.add(est[nextEv.getIndex()][nextCp.getIndex()] - Geolocation.getDistance(nextEv.getOrigin(), nextCp.getLocation()) * 6 / 5);

//                nextEv.printEV();
//                printWriter.print(" -> ");
//                nextCp.printCP();
                double distance = Geolocation.getDistance(nextEv.getDestination(), nextCp.getLocation());
//                printWriter.print(" (distance: " + distance + ", time: " + est[nextEv.getIndex()][nextCp.getIndex()] + ") ");
                dynamicDistances.add(distance);
//                printWriter.println(" (dynamic)");

                for (ElectricVehicle ev : evs) {
                    if (est[ev.getIndex()][nextCp.getIndex()] != -1) {
                        est[ev.getIndex()][nextCp.getIndex()] = Math.max(est[nextEv.getIndex()][nextCp.getIndex()] + nextEv.timeToCharge() * 60, requestTime + Geolocation.getDistance(ev.getOrigin(), nextCp.getLocation()) * 6 / 5);
                    }
                }

                for (ChargingPoint cp : cps) {
                    est[nextEv.getIndex()][cp.getIndex()] = -1;
                }
            }

//            countUnallocatedEVs(evs, evCp, unallocatedEVs);
//            unallocated = 0;
//
//            for (String k : unallocatedEVs.keySet()) {
//                Integer v = unallocatedEVs.get(k);
//                if (v != 0 && !k.equals("total")) {
//                    try {
//                        unallocated += v;
//                        generateCPsInArea(cps, k, v);
//                    } catch (IOException | InterruptedException e) {
//                        e.printStackTrace();
//                    }
//                }
//            }

        } while (nextCp != null);
//        } while (unallocated > 0);


    }
}
