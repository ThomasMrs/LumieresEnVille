package fr.lumieresenville.robots;

public class Robot {

    private String id;
    private final String nom;
    private double vitesse;
    private double x;
    private double y;
    private String type;
    private EtatRobot etat;
    private Mission mission;


    public Robot(String nom, double x, double y) {
        this.id = null;
        this.nom = nom;
        this.vitesse = 1.0;
        this.x = x;
        this.y = y;
        this.type = "";
        this.etat = EtatRobot.AVAILABLE;
        this.mission = null;
    }

    public String getId()      { return id; }
    public String getNom()     { return nom; }
    public double getVitesse() { return vitesse; }
    public double getX()       { return x; }
    public double getY()       { return y; }
    public EtatRobot getEtat() { return etat; }

    public void setId(String id)             { this.id = id; }
    public void setVitesse(double vitesse)   { this.vitesse = vitesse; }
    public void setPosition(double x, double y) { this.x = x; this.y = y; }
    public void setType(String type)         { this.type = type == null ? "" : type; }
    public void setEtat(EtatRobot etat)      { this.etat = etat; }
    public void setMission(Mission mission)  { this.mission = mission; }

    public boolean estVolant() {
        return type.equalsIgnoreCase("volant");
    }
}
