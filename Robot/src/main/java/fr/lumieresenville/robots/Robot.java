package fr.lumieresenville.robots;          // le package (dossier logique)

// Modele d'un robot : son nom, sa position, son etat et sa mission en cours.
public class Robot {

    private String id;                       // id renvoye par le serveur
    private final String nom;                // le nom du robot (ne change pas)
    private double vitesse;                  // vitesse du robot
    private double x;                        // position actuelle (horizontale)
    private double y;                        // position actuelle (verticale)
    private EtatRobot etat;                  // l'etat courant (voir EtatRobot)
    private Mission mission;                 // la mission en cours, ou null si aucune

    // Constructeur : cree un robot neuf, a la base, sans mission
    public Robot(String nom, double x, double y) {
        this.id = null;                      // l'id sera recupere apres l'ajout au serveur
        this.nom = nom;                      // on memorise le nom
        this.vitesse = 1.0;                  // vitesse par defaut
        this.x = x;                          // on memorise la position X
        this.y = y;                          // on memorise la position Y
        this.etat = EtatRobot.AVAILABLE;     // au depart : disponible
        this.mission = null;                 // au depart : pas de mission
    }

    public String getId()      { return id; }       // lire l'id serveur
    public String getNom()      { return nom; }      // lire le nom
    public double getVitesse()  { return vitesse; }  // lire la vitesse
    public double getX()        { return x; }        // lire la position X
    public double getY()        { return y; }        // lire la position Y
    public EtatRobot getEtat()  { return etat; }     // lire l'etat
    public Mission getMission() { return mission; }  // lire la mission

    public void setId(String id)                 { this.id = id; }           // enregistrer l'id serveur
    public void setVitesse(double vitesse)       { this.vitesse = vitesse; } // changer la vitesse
    public void setPosition(double x, double y) { this.x = x; this.y = y; } // changer la position
    public void setEtat(EtatRobot etat)         { this.etat = etat; }       // changer l'etat
    public void setMission(Mission mission)     { this.mission = mission; } // donner une mission

    // Texte lisible decrivant le robot (appele automatiquement par println)
    @Override
    public String toString() {
        String m = (mission == null)                                   // si le robot n'a pas de mission...
                ? "aucune mission"                                     // ...on ecrit "aucune mission"
                : "-> " + mission.getSemaphoreId();                    // sinon : -> semaphore a reveiller
        String texteId = (id == null) ? "id inconnu" : id;              // id lisible
        return nom + "  " + texteId + "  (" + (int) x + ", " + (int) y + ")  [" + etat + "]  " + m;
    }
}
