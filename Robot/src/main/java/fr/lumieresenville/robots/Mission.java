package fr.lumieresenville.robots;

// Cette classe represente une mission recue du serveur :
// elle contient l'id de la mission, le semaphore, le robot affecte, l'etat, les dates et la duree.
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

    // Ce constructeur cree une mission Java avec les informations lues dans le JSON du serveur.
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

    // Ces methodes permettent de lire les informations de la mission.
    public String getId()           { return id; }
    public String getNom()          { return nom; }
    public String getSemaphoreId()  { return semaphoreId; }
    public String getRobotId()      { return robotId; }
    public String getEtat()         { return etat; }
    public String getDebutMission() { return debutMission; }
    public String getFinMission()   { return finMission; }
    public String getTeam()         { return team; }
    public String getTempsMission() { return tempsMission; }

    public long getDureeSecondes() {
        if (tempsMission == null || tempsMission.isBlank()) {
            return 0;
        }
        try {
            return Math.max(0, Math.round(Double.parseDouble(tempsMission)));
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    // Cette methode demarre la mission :
    // elle ajoute l'id du robot, la date de debut et l'etat "In progress".
    public void demarrer(String robotId, String debutMission) {
        this.robotId = robotId;
        this.debutMission = debutMission;
        this.finMission = "";
        this.etat = "In progress";
    }

    // Cette methode termine la mission :
    // elle ajoute la date de fin et l'etat "Done".
    public void terminer(String finMission) {
        this.finMission = finMission;
        this.etat = "Done";
    }

    // Cette methode donne une version lisible de la mission dans le terminal.
    @Override
    public String toString() {
        return nom + "  id=" + id
                + "  semaphore_id=" + semaphoreId
                + "  robot_id=" + robotId
                + "  etat=" + etat
                + "  duree=" + tempsMission;
    }
}
