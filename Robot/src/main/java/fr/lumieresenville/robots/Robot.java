package fr.lumieresenville.robots;          // le package (dossier logique)

// Modele d'un robot : son nom, sa position, son etat et sa mission en cours.
public class Robot {

    private final String nom;                // le nom du robot (ne change pas)
    private double x;                        // position actuelle (horizontale)
    private double y;                        // position actuelle (verticale)
    private EtatRobot etat;                  // l'etat courant (voir EtatRobot)
    private Mission mission;                 // la mission en cours, ou null si aucune

    // Constructeur : cree un robot neuf, a la base, sans mission
    public Robot(String nom, double x, double y) {
        this.nom = nom;                      // on memorise le nom
        this.x = x;                          // on memorise la position X
        this.y = y;                          // on memorise la position Y
        this.etat = EtatRobot.DISPONIBLE;    // au depart : disponible
        this.mission = null;                 // au depart : pas de mission
    }

    public String getNom()      { return nom; }      // lire le nom
    public double getX()        { return x; }        // lire la position X
    public double getY()        { return y; }        // lire la position Y
    public EtatRobot getEtat()  { return etat; }     // lire l'etat
    public Mission getMission() { return mission; }  // lire la mission

    public void setPosition(double x, double y) { this.x = x; this.y = y; } // changer la position
    public void setEtat(EtatRobot etat)         { this.etat = etat; }       // changer l'etat
    public void setMission(Mission mission)     { this.mission = mission; } // donner une mission

    // Texte lisible decrivant le robot (appele automatiquement par println)
    @Override
    public String toString() {
        String m = (mission == null)                                   // si le robot n'a pas de mission...
                ? "aucune mission"                                     // ...on ecrit "aucune mission"
                : "-> " + mission.getSemaphore();                      // sinon : -> semaphore a reveiller
        return nom + "  (" + (int) x + ", " + (int) y + ")  [" + etat + "]  " + m; // la ligne complete
    }
}
