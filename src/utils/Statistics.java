/*
 * Project: Evo-Sim
 * Developed by: Irina Danes
 */

package utils;

import java.io.PrintWriter;
import java.util.Collections;
import java.util.List;

public class Statistics {

    private static double computeMedian(List<Double> list) {
        double median = 0.0;
        if (list != null && list.size() != 0) {
            if (list.size() % 2 == 1) {
                median = list.get((list.size() - 1) / 2);
            } else {
                median = (list.get((list.size() - 1) / 2) + list.get(list.size() / 2)) / 2;
            }
        }
        return Math.round(median * 100.0) / 100.0;
    }

    private static void computeQuartiles(List<Double> list, PrintWriter printWriter) {
        if (list != null && list.size() != 0) {
            List<Double> firstHalf;
            List<Double> secondHalf;
            if (list.size() % 2 == 1) {
                firstHalf = list.subList(0, list.size() / 2);
                secondHalf = list.subList(list.size() / 2 + 1, list.size());
            } else {
                firstHalf = list.subList(0, list.size() / 2);
                secondHalf = list.subList(list.size() / 2, list.size());
            }

            printWriter.println(" - quartiles: ");
            printWriter.println("     - q1: " + computeMedian(firstHalf));
            printWriter.println("     - q2: " + computeMedian(list));
            printWriter.println("     - q3: " + computeMedian(secondHalf));
        }
    }

    public static void computeStatistics(List<Double> list, PrintWriter printWriter) {
        if (list != null && list.size() != 0) {
            Collections.sort(list);

            printWriter.println("- min: " + Collections.min(list));
            printWriter.println("- max: " + Collections.max(list));
            printWriter.println("- median: " + computeMedian(list));

            computeQuartiles(list, printWriter);
            double sum = 0.0;
            for (double d : list) {
                sum += d;
            }

            printWriter.println("- average: " + Math.round(sum /list.size() * 100.0) / 100.0);

            printWriter.println("Total: " + Math.round(sum * 100.0) / 100.0);
        } else {
            printWriter.println("No optimal solution");
        }
    }

}
