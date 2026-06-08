package fr.lumieresenville.robots;          // le package (dossier logique)

// Une mission recue du serveur : elle lie un robot a un semaphore.
public class Mission {

    private final String id;                 // id de la mission
    private final String nom;                // nom de la mission
    private final String semaphoreId;        // id du semaphore a allumer
    private String robotId;                  // id du robot affecte
    private String etat;                     // Pending, In progress, Done...
    private String debutMission;             // date/heure de debut
    private String finMission;               // date/heure de fin
    private final String team;               // equipe liee a la mission

    // Constructeur : on fournit les infos lues depuis le serveur
    public Mission(String id, String nom, String semaphoreId, String robotId,
                   String etat, String debutMission, String finMission, String team) {
        this.id = id;
        this.nom = nom;
        this.semaphoreId = semaphoreId;
        this.robotId = robotId;
        this.etat = etat;
        this.debutMission = debutMission;
        this.finMission = finMission;
        this.team = team;
    }

    public String getId()             { return id; }             // lire l'id mission
    public String getNom()            { return nom; }            // lire le nom
    public String getSemaphoreId()    { return semaphoreId; }    // lire l'id semaphore
    public String getRobotId()        { return robotId; }        // lire l'id robot
    public String getEtat()           { return etat; }           // lire l'etat
    public String getDebutMission()   { return debutMission; }   // lire le debut
    public String getFinMission()     { return finMission; }     // lire la fin
    public String getTeam()           { return team; }           // lire l'equipe

    // Marque la mission comme demarree par un robot
    public void demarrer(String robotId, String debutMission) {
        this.robotId = robotId;
        this.debutMission = debutMission;
        this.finMission = "";
        this.etat = "In progress";
    }

    // Marque la mission comme terminee
    public void terminer(String finMission) {
        this.finMission = finMission;
        this.etat = "Done";
    }

    @Override
    public String toString() {
        return nom + "  id=" + id
                + "  semaphore_id=" + semaphoreId
                + "  robot_id=" + robotId
                + "  etat=" + etat;
    }
}
