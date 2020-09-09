package scheduler;

import java.io.IOException;
import java.util.*;

import chargingStation.ChargingPoint;
import chargingStation.Status;
import vehicle.ElectricVehicle;

import static evoSim.Main.*;
import static scheduler.Static.greedyMapEVtoCP;

public class Dynamic {
    public static List<Double> max = new ArrayList<>();
    public static HashMap<String, Integer> unallocatedEVs = new HashMap<>();

    public static void schedule(List<ElectricVehicle> evs, List<ChargingPoint> cps, double requestTime) throws IOException, InterruptedException {
        Map<ElectricVehicle, ChargingPoint> evCp = new HashMap<>();
        evs.sort(Comparator.comparingDouble(ElectricVehicle::getWaitTime));

        double[][] est = new double[evs.size() + 2][cps.size() + 2];
        for (ElectricVehicle ev : evs) {
            for (ChargingPoint cp : cps) {
                if (!match(cp, ev)) {
                    est[ev.getIndex()][cp.getIndex()] = -1;
                } else {
                    double arrivalTime = requestTime + getDistance(ev.getOrigin(), ev.getDestination()) * 6 / 5;
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
                            double initialSum = getDistance(cp1.getLocation(), ev1.getDestination()) + getDistance(cp2.getLocation(), ev2.getDestination());
                            double newSum = getDistance(cp1.getLocation(), ev2.getDestination()) + getDistance(cp2.getLocation(), ev1.getDestination());

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

            max.add(0.0);

//            ev.printEV();
//            printWriter.print(" -> ");
//            result.printCP();
            double distance = getDistance(ev.getDestination(), result.getLocation());
            dynamicDistances.add(distance);
//            printWriter.print(" (distance: " + distance + ") ");
//            printWriter.println(" (heuristic)");

            for (ElectricVehicle ev2 : evs) {
                if (est[ev2.getIndex()][result.getIndex()] != -1) {
                    // WHEN FIRST EV STARTS CHARGING + HOW LONG IT CHARGES FOR ... OR WHEN SECOND EV ARRIVES AT CP
                    est[ev2.getIndex()][result.getIndex()] = Math.max(est[ev.getIndex()][result.getIndex()] + ev.timeToCharge() * 60, requestTime + getDistance(ev2.getOrigin(), result.getLocation()) * 6 / 5);
                }
            }
            evs.remove(ev);
        }

        ElectricVehicle nextEv = null;
        ChargingPoint nextCp = null;

        do {
            double min = Double.MAX_VALUE;
            double minDist = Double.MAX_VALUE;
            nextEv = null;
            nextCp = null;

            for (ElectricVehicle ev : evs) {
                for (ChargingPoint cp : cps) {
                    if (est[ev.getIndex()][cp.getIndex()] != -1 && est[ev.getIndex()][cp.getIndex()] <= min &&
                            getDistance(ev.getDestination(), cp.getLocation()) <= minDist
                                && (!timeConstraint || ev.getWaitTime() >= est[ev.getIndex()][cp.getIndex()] - getDistance(ev.getOrigin(), cp.getLocation()) * 6/5)) {
                        min = est[ev.getIndex()][cp.getIndex()];
                        minDist = getDistance(ev.getDestination(), cp.getLocation());

                        nextEv = ev;
                        nextCp = cp;
                    }
                }
            }

            if (nextEv != null) {
                evCp.put(nextEv, nextCp);
                evs.remove(nextEv);

                max.add(est[nextEv.getIndex()][nextCp.getIndex()] - getDistance(nextEv.getOrigin(), nextCp.getLocation()) * 6 / 5);

//                nextEv.printEV();
//                printWriter.print(" -> ");
//                nextCp.printCP();
                double distance = getDistance(nextEv.getDestination(), nextCp.getLocation());
//                printWriter.print(" (distance: " + distance + ", time: " + est[nextEv.getIndex()][nextCp.getIndex()] + ") ");
                dynamicDistances.add(distance);
//                printWriter.println(" (dynamic)");

                for (ElectricVehicle ev : evs) {
                    if (est[ev.getIndex()][nextCp.getIndex()] != -1) {
                        est[ev.getIndex()][nextCp.getIndex()] = Math.max(est[nextEv.getIndex()][nextCp.getIndex()] + nextEv.timeToCharge() * 60, requestTime + getDistance(ev.getOrigin(), nextCp.getLocation()) * 6 / 5);
                    }
                }

                for (ChargingPoint cp : cps) {
                    est[nextEv.getIndex()][cp.getIndex()] = -1;
                }
            }
        } while (nextEv != null);

//        countUnallocatedEVs(evs, evCp, unallocatedEVs);
    }
}

