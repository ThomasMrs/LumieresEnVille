package fr.lumieresenville.robots;
public class Mission {

    private final String id;
    private final String nom;
    private final String semaphoreId;
    private String robotId;
    private String etat;
    private String debutMission;
    private String finMission;
    private final String team;
    private final String tempsMission;


    public Mission(String id, String nom, String semaphoreId, String robotId,
                   String etat, String debutMission, String finMission, String team, String tempsMission) {
        this.id = id;
        this.nom = nom;
        this.semaphoreId = semaphoreId;
        this.robotId = robotId;
        this.etat = etat;
        this.debutMission = debutMission;
        this.finMission = finMission;
        this.team = team;
        this.tempsMission = tempsMission;
    }

    // lire les informations de la mission.
    public String getId()           { return id; }
    public String getNom()          { return nom; }
    public String getSemaphoreId()  { return semaphoreId; }
    public String getRobotId()      { return robotId; }
    public String getEtat()         { return etat; }
    public String getDebutMission() { return debutMission; }
    public String getFinMission()   { return finMission; }
    public String getTeam()         { return team; }
    public String getTempsMission() { return tempsMission; }

    // Le robot prend la mission 
    public void prendreEnChargeParRobot(String robotId, String debutMission) {
        this.robotId = robotId;
        this.debutMission = debutMission;
        this.finMission = "";
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
                + "  etat=" + etat
                + "  duree=" + tempsMission;
    }
}
