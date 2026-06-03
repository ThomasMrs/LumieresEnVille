package fr.lumieresenville.robots;

/**
 * Une mission : aller au sémaphore indiqué et y afficher un symbole.
 */
public class Mission {

    private final String semaphore; // nom du sémaphore à allumer
    private final String symbole;   // caractère à afficher
    private final double x;          // position du sémaphore
    private final double y;

    public Mission(String semaphore, String symbole, double x, double y) {
        this.semaphore = semaphore;
        this.symbole = symbole;
        this.x = x;
        this.y = y;
    }

    public String getSemaphore() { return semaphore; }
    public String getSymbole()   { return symbole; }
    public double getX()         { return x; }
    public double getY()         { return y; }
}
