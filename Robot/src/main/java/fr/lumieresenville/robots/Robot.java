package fr.lumieresenville.robots;

/**
 * Modèle d'un robot : son nom, sa position, son état et sa mission en cours.
 */
public class Robot {

    private final String nom;
    private double x;            // position actuelle (horizontale)
    private double y;            // position actuelle (verticale)
    private EtatRobot etat;
    private Mission mission;     // null si le robot n'a pas de mission

    public Robot(String nom, double x, double y) {
        this.nom = nom;
        this.x = x;
        this.y = y;
        this.etat = EtatRobot.DISPONIBLE;
        this.mission = null;
    }

    public String getNom()      { return nom; }
    public double getX()        { return x; }
    public double getY()        { return y; }
    public EtatRobot getEtat()  { return etat; }
    public Mission getMission() { return mission; }

    public void setPosition(double x, double y) { this.x = x; this.y = y; }
    public void setEtat(EtatRobot etat)         { this.etat = etat; }
    public void setMission(Mission mission)     { this.mission = mission; }

    /** Texte simple décrivant le robot (utile pour l'affichage). */
    @Override
    public String toString() {
        String m = (mission == null)
                ? "aucune mission"
                : mission.getSymbole() + " -> " + mission.getSemaphore();
        return nom + "  (" + (int) x + ", " + (int) y + ")  [" + etat + "]  " + m;
    }
}
