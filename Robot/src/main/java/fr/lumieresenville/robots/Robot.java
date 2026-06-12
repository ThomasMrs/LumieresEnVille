package fr.lumieresenville.robots;

public class Robot {

    private String id;
    private final String nom;
    private double vitesse;
    private double x;
    private double y;
    private EtatRobot etat;
    private Mission mission;

    // Ce constructeur cree un robot Java avec un nom et une position.
    // L'id reste null au debut car il vient du serveur.
    public Robot(String nom, double x, double y) {
        this.id = null;
        this.nom = nom;
        this.vitesse = 1.0;
        this.x = x;
        this.y = y;
        this.etat = EtatRobot.AVAILABLE;
        this.mission = null;
    }

    // lire info robot
    public String getId()      { return id; }
    public String getNom()     { return nom; }
    public double getVitesse() { return vitesse; }
    public double getX()       { return x; }
    public double getY()       { return y; }
    public EtatRobot getEtat() { return etat; }
    public Mission getMission() { return mission; }

    // modif info robot
    public void setId(String id)             { this.id = id; }
    public void setVitesse(double vitesse)   { this.vitesse = vitesse; }
    public void setPosition(double x, double y) { this.x = x; this.y = y; }
    public void setEtat(EtatRobot etat)      { this.etat = etat; }
    public void setMission(Mission mission)  { this.mission = mission; }


    @Override
    public String toString() {
        String texteMission = (mission == null)
                ? "aucune mission"
                : "-> " + mission.getSemaphoreId();

        String texteId = (id == null) ? "id inconnu" : id;

        return nom + "  " + texteId + "  (" + (int) x + ", " + (int) y + ")  [" + etat + "]  " + texteMission;
    }
}
