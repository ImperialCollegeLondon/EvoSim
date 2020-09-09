package scheduler;

import com.google.ortools.linearsolver.MPConstraint;
import com.google.ortools.linearsolver.MPObjective;
import com.google.ortools.linearsolver.MPSolver;
import com.google.ortools.linearsolver.MPVariable;

import chargingStation.ChargingPoint;
import chargingStation.Status;
import evoSim.Main;
import vehicle.ElectricVehicle;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

import static evoSim.Main.fileWriter;

public class OptimalSolution {
    private static final PrintWriter printWriter = new PrintWriter(fileWriter);

    static protected final List<Double> binPackingDistances = new ArrayList<>();

    static {
        System.loadLibrary("jniortools");
    }

    public static void optimal(List<ChargingPoint> cps, List<ElectricVehicle> evs) {
        final int numEVs = evs.size();
        final int numCPs = cps.size();
        int[] availability = new int[cps.size()];
        int[][] matchInt = new int[evs.size()][cps.size()];

        for (int i = 0; i < cps.size(); i++) {
            availability[i] = (cps.get(i).getStatus() == Status.AVAILABLE ? 1 : 0);
        }

        MPSolver solver = new MPSolver(
                "OptimisationProblem", MPSolver.OptimizationProblemType.GLOP_LINEAR_PROGRAMMING);
        MPVariable[][] x = new MPVariable[numEVs][numCPs];
        for (int i = 0; i < numEVs; ++i) {
            for (int j = 0; j < numCPs; ++j) {
                x[i][j] = solver.makeIntVar(0, 1, "");
            }
        }

        for (int i = 0; i < numEVs; i++) {
            for (int j = 0; j < numCPs; j++) {
                matchInt[i][j] = ((
                        evs.get(i).getSocketType() == cps.get(j).getSocketType() &&
                        ((evs.get(i).getWillingToPay() && cps.get(j).getPrice() > 0) ||
                            cps.get(j).getPrice() == 0) &&
                        cps.get(j).getStatus() == Status.AVAILABLE) ? 1 : 0);
            }
        }

        // each EV can only be assigned to a CP if they match
        for (int i = 0; i < numEVs; i++) {
            for (int j = 0; j < numCPs; j++) {
                MPConstraint ct = solver.makeConstraint(0, matchInt[i][j], "");
                ct.setCoefficient(x[i][j], 1);
            }
        }

        // each EV must be assigned to one CP
        for (int i = 0; i < numEVs; ++i) {
            MPConstraint constraint = solver.makeConstraint(1, 1, "");
            for (int j = 0; j < numCPs; ++j) {
                constraint.setCoefficient(x[i][j], 1);
            }
        }

        // each CP can receive maximum 1 EV
        for (int i = 0; i < numCPs; ++i) {
            MPConstraint constraint = solver.makeConstraint(0, 1, "");
            for (int j = 0; j < numEVs; ++j) {
                constraint.setCoefficient(x[j][i], 1);
            }
        }

        MPObjective objective = solver.objective();
        for (int i = 0; i < numEVs; ++i) {
            for (int j = 0; j < numCPs; ++j) {
                objective.setCoefficient(x[i][j], Main.getDistance(evs.get(i).getDestination(), cps.get(j).getLocation()));
            }
        }
        //objective.setMaximization();
        objective.setMinimization();

        final MPSolver.ResultStatus resultStatus = solver.solve();


        // Check that the problem has an optimal solution.
        if (resultStatus == MPSolver.ResultStatus.OPTIMAL) {
            for (int j = 0; j < numCPs; ++j) {
                for (int i = 0; i < numEVs; ++i) {
                    if (x[i][j].solutionValue() == 1) {
//                        evs.get(i).printEV();
//                        printWriter.print(" -> ");
//                        cps.get(j).printCP();
//                        printWriter.print("OPTIMAL");
//                        printWriter.println();

//                        evs.get(i).printEV();
                        double distance = Main.getDistance(evs.get(i).getDestination(), cps.get(j).getLocation());
//                        System.out.println("distance: " + distance);
                        binPackingDistances.add(distance);
                    }
                }
            }
        } else {
            System.err.println("The problem does not have an optimal solution.");
        }
    }

}
