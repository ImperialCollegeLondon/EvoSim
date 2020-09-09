package chargingStation;

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

    public String printGeolocation() {
        return "(" + this.getX() + ", " + this.getY() + ")";
    }
}
