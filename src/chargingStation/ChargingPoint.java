package chargingStation;

import java.io.PrintWriter;

import vehicle.ChargingType;

import static evoSim.Main.fileWriter;

public class ChargingPoint {
    private static final PrintWriter printWriter = new PrintWriter(fileWriter);

    public static int lastIndex = 0;
    private int index;

    private final Geolocation location;
    private final ChargingType chargingType; // standard, fast, super-fast
    private final SocketType socketType;
    private final double price;
    private Status status;       // available, not available, not working
    private String postcode;

    public ChargingPoint(Geolocation location, SocketType socketType, ChargingType chargingType,
                         double price, Status status) {
        this.location = location;
        this.socketType = socketType;
        this.chargingType = chargingType;
        this.price = price;
        this.status = status;
    }

    public int getIndex() {
        return index;
    }

    public void setIndex(int index) {
        this.index = index;
    }

    public Geolocation getLocation() {
        return location;
    }

    public SocketType getSocketType() {
        return socketType;
    }

    public ChargingType getChargingType() {
        return chargingType;
    }

    public double getPrice() {
        return price;
    }

    public Status getStatus() {
        return status;
    }

    public void setStatus(Status status) {
        this.status = status;
    }

    public void setPostcode(String postcode) {
        this.postcode = postcode;
    }

    public String getPostcode() {
        return postcode;
    }

    public static void printCPheadings() {
        printWriter.println();
        printWriter.println("location    socketType    chargingType       price      status");
        printWriter.println();
    }

    public void printCP() {
        printWriter.print(this.getIndex() + "    " +
                this.getLocation().printGeolocation() +  "    " +
                this.getSocketType() + "    " +
                this.getChargingType() + "   " +
                this.getPrice() + "   " +
                this.getStatus());
    }
}

