package fr.lumieresenville.robots;

/** Un sémaphore sur la carte : un nom et une position (x, y). */
public class Semaphore {

    private final String nom;
    private final double x;
    private final double y;

    public Semaphore(String nom, double x, double y) {
        this.nom = nom;
        this.x = x;
        this.y = y;
    }

    public String getNom() { return nom; }
    public double getX()   { return x; }
    public double getY()   { return y; }
}
