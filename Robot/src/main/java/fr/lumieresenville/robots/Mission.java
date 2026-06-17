package fr.lumieresenville.robots;
public class Mission {

    private final String id;
    private final String nom;
    private final String semaphoreId;
    private String robotId;
    private String etat;
    private final String team;


    public Mission(String id, String nom, String semaphoreId, String robotId,
                   String etat, String team) {
        this.id = id;
        this.nom = nom;
        this.semaphoreId = semaphoreId;
        this.robotId = robotId;
        this.etat = etat;
        this.team = team;
    }

    // lire les informations de la mission.
    public String getId()           { return id; }
    public String getNom()          { return nom; }
    public String getSemaphoreId()  { return semaphoreId; }
    public String getRobotId()      { return robotId; }
    public String getEtat()         { return etat; }
    public String getTeam()         { return team; }

    // Le robot prend la mission
    public void prendreEnChargeParRobot(String robotId) {
        this.robotId = robotId;
        this.etat = "Pending_robot";
    }

    public void signalerArriveeSemaphore() {
        this.etat = "Pending_semaphore";
    }

//affichage terminale
    @Override
    public String toString() {
        return nom + "  id=" + id
                + "  semaphore_id=" + semaphoreId
                + "  robot_id=" + robotId
                + "  etat=" + etat;
    }
}
