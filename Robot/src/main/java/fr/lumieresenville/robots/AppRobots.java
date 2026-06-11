package fr.lumieresenville.robots;

import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class AppRobots {
    private static final String SERVEUR = "http://192.168.1.14:8000";
    private static final int BASE_X = 0;
    private static final int BASE_Y = 0;
    private static final HttpClient HTTP = HttpClient.newHttpClient();
    private static final Scanner CLAVIER = new Scanner(System.in);
    private static final DateTimeFormatter FORMAT_DATE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static void main(String[] args) throws Exception {
        ApercuGrilleRobots.lancer();
        System.out.println("Apercu graphique de la grille lance.");

        if (get("/api/list_robots").startsWith("ERREUR")) {
            System.out.println("Serveur injoignable (" + SERVEUR + ").");
            System.out.println("Demarre le serveur FastAPI, puis relance.");
            return;
        }

        // Boucle : on affiche la liste des missions (relue a chaque tour), tu en choisis une,
        // le robot l'execute, puis on recommence (0 pour quitter).
        while (true) {
            Robot robotDisponible = chercherRobotDisponible(lireRobotsDuServeur());
            Mission mission = choisirMissionDansTerminal();

            if (mission == null) {
                System.out.println("Au revoir.");
                break;
            } else if (robotDisponible == null) {
                System.out.println("Aucun robot disponible.");
            } else {
                faireLaMission(robotDisponible, mission);
            }
        }
    }

    // Cycle d'une mission :
    //  - le robot reclame la mission (mission -> Pending_robot),
    //  - il recupere les coordonnees du semaphore et s'y deplace selon sa vitesse,
    //  - quand il est arrive, il passe Occupied,
    //  - il signale l'arrivee au semaphore (mission -> Pending_semaphore),
    //  - il rentre a la base : robot Available et position (0, 0).
    private static void faireLaMission(Robot robot, Mission mission) throws Exception {
        System.out.println("Mission choisie : " + mission);

        mission.prendreEnChargeParRobot(robot.getId(), maintenant());
        System.out.println("Mission reclamee par le robot.");
        System.out.println("PUT mission    : " + modifierMission(mission));

        String semaphoreJson = get("/api/semaphore/" + enc(mission.getSemaphoreId()));
        System.out.println("Semaphore lie   : " + semaphoreJson);

        // Le robot se teleporte sur les coordonnees (x, y) du semaphore
        double coordX = nombre(semaphoreJson, "coord_x");
        double coordY = nombre(semaphoreJson, "coord_y");

        deplacerRobot(robot, coordX, coordY);

        robot.setEtat(EtatRobot.OCCUPIED);
        System.out.println("Robot arrive, passage en Occupied.");
        System.out.println("PUT robot      : " + modifierRobot(robot));

        mission.signalerArriveeSemaphore();
        System.out.println("Mission transmise au semaphore.");
        System.out.println("PUT mission    : " + modifierMission(mission));

        deplacerRobot(robot, BASE_X, BASE_Y);

        robot.setEtat(EtatRobot.AVAILABLE);
        System.out.println("Robot arrive a la base, passage en Available.");
        System.out.println("PUT robot      : " + modifierRobot(robot));
    }

    private static void deplacerRobot(Robot robot, double destinationX, double destinationY) throws Exception {
        int cibleX = (int) Math.round(destinationX);
        int cibleY = (int) Math.round(destinationY);
        int x = (int) Math.round(robot.getX());
        int y = (int) Math.round(robot.getY());

        verifierPositionDansGrille(cibleX, cibleY);
        System.out.println("Deplacement robot -> depart=(" + x + ", " + y + ")"
                + ", destination=(" + cibleX + ", " + cibleY + ")"
                + ", vitesse=" + robot.getVitesse() + " case(s)/s");

        while (x != cibleX || y != cibleY) {
            if (x < cibleX) {
                x++;
            } else if (x > cibleX) {
                x--;
            } else if (y < cibleY) {
                y++;
            } else {
                y--;
            }

            robot.setPosition(x, y);
            System.out.println("Robot avance -> (" + x + ", " + y + ")");
            System.out.println("PUT robot      : " + modifierRobot(robot));
            attendreSelonVitesse(robot);
        }
    }

    private static void verifierPositionDansGrille(int x, int y) throws Exception {
        String grilleJson = get("/api/get_grille");
        if (grilleJson.startsWith("ERREUR") || grilleJson.startsWith("erreur HTTP")) {
            System.out.println("Grille non verifiee : " + grilleJson);
            return;
        }

        int largeur = (int) nombre(grilleJson, "nombre_x");
        int hauteur = (int) nombre(grilleJson, "nombre_y");
        if (largeur <= 0 || hauteur <= 0) {
            System.out.println("Grille non verifiee : dimensions inconnues.");
            return;
        }
        if (x < 0 || y < 0 || x >= largeur || y >= hauteur) {
            System.out.println("Attention : destination hors grille (" + x + ", " + y
                    + ") pour une grille " + largeur + "x" + hauteur + ".");
        }
    }

    private static void attendreSelonVitesse(Robot robot) throws InterruptedException {
        double vitesse = robot.getVitesse();
        if (vitesse <= 0) {
            vitesse = 1.0;
        }
        long delaiMs = Math.max(100, Math.round(1000.0 / vitesse));
        Thread.sleep(delaiMs);
    }

    private static List<Robot> lireRobotsDuServeur() throws Exception {
        List<Robot> robots = new ArrayList<>();
        for (String objet : objets(get("/api/list_robots"))) {
            Robot robot = new Robot(champ(objet, "name"), nombre(objet, "position_x"), nombre(objet, "position_y"));
            robot.setId(champ(objet, "id"));
            robot.setVitesse(nombre(objet, "speed"));
            robot.setEtat(etatRobot(champ(objet, "state")));
            robots.add(robot);
        }
        return robots;
    }

    private static Robot chercherRobotDisponible(List<Robot> robots) {
        for (Robot robot : robots) {
            if (robot.getEtat() == EtatRobot.AVAILABLE) {
                return robot;
            }
        }
        return null;
    }

    // Affiche les missions Awaiting encore libres et demande d'en choisir une au clavier.
    private static Mission choisirMissionDansTerminal() throws Exception {
        List<Mission> missions = lireMissionsAwaiting();
        if (missions.isEmpty()) {
            System.out.println("Aucune mission Awaiting disponible.");
            return null;
        }

        System.out.println("=== Missions Awaiting (" + missions.size() + ") ===");
        for (int i = 0; i < missions.size(); i++) {
            Mission mission = missions.get(i);
            System.out.println((i + 1) + " - " + mission.getNom()
                    + " | etat : " + mission.getEtat()
                    + " | equipe : " + mission.getTeam()
                    + " | duree : " + mission.getTempsMission());
        }

        while (true) {
            System.out.print("Choisis une mission (1 a " + missions.size() + ", 0 pour quitter) : ");
            String reponse = CLAVIER.nextLine();
            try {
                int numero = Integer.parseInt(reponse);
                if (numero == 0) return null;
                if (numero >= 1 && numero <= missions.size()) {
                    return missions.get(numero - 1);
                }
            } catch (NumberFormatException e) {
                // entree non numerique : on redemande
            }
            System.out.println("Numero invalide.");
        }
    }

    private static List<Mission> lireMissionsAwaiting() throws Exception {
        List<Mission> missionsAwaiting = new ArrayList<>();
        for (Mission mission : lireMissions()) {
            if (missionDisponiblePourRobot(mission)) {
                missionsAwaiting.add(mission);
            }
        }
        return missionsAwaiting;
    }

    private static boolean missionDisponiblePourRobot(Mission mission) {
        return mission.getEtat().equalsIgnoreCase("Awaiting")
                && mission.getRobotId().isBlank()
                && mission.getFinMission().isBlank();
    }

    private static List<Mission> lireMissions() throws Exception {
        List<Mission> missions = new ArrayList<>();
        for (String objet : objets(get("/api/list_missions"))) {
            missions.add(new Mission(
                    champ(objet, "id"), champ(objet, "name"), champ(objet, "semaphore_id"),
                    champ(objet, "robot_id"), champ(objet, "state"),
                    champ(objet, "start_date"), champ(objet, "end_date"),
                    champ(objet, "team"), champ(objet, "time")));
        }
        return missions;
    }

    private static String modifierRobot(Robot robot) throws Exception {
        System.out.println("Changement robot -> id=" + robot.getId()
                + ", state=" + etatServeur(robot.getEtat())
                + ", speed=" + (int) Math.round(robot.getVitesse())
                + ", position=(" + robot.getX() + ", " + robot.getY() + ")");
        String url = "/api/update_robot/" + enc(robot.getId())
                + "?name=" + enc(robot.getNom())
                + "&state=" + enc(etatServeur(robot.getEtat()))
                + "&speed=" + (int) Math.round(robot.getVitesse()) // le serveur veut un entier
                + "&position_x=" + (int) Math.round(robot.getX())
                + "&position_y=" + (int) Math.round(robot.getY());
        return put(url);
    }

    private static String modifierMission(Mission mission) throws Exception {
        System.out.println("Changement mission -> id=" + mission.getId()
                + ", robot_id=" + mission.getRobotId()
                + ", state=" + mission.getEtat()
                + ", start_date=" + mission.getDebutMission()
                + ", end_date=" + mission.getFinMission()
                + ", time=" + mission.getTempsMission());
        String url = "/api/update_mission/" + enc(mission.getId())
                + "?name=" + enc(mission.getNom())
                + "&semaphore_id=" + enc(mission.getSemaphoreId())
                + "&robot_id=" + enc(mission.getRobotId())
                + "&state=" + enc(mission.getEtat())
                + "&start_date=" + enc(mission.getDebutMission())
                + "&end_date=" + enc(mission.getFinMission())
                + "&team=" + enc(mission.getTeam())
                + "&time=" + enc(mission.getTempsMission());
        return put(url);
    }

    // Decoupe un tableau JSON [ {...}, {...} ] en objets, en suivant la profondeur des accolades.
    private static List<String> objets(String json) {
        List<String> liste = new ArrayList<>();
        int profondeur = 0;
        int debut = -1;
        for (int i = 0; i < json.length(); i++) {
            char c = json.charAt(i);
            if (c == '{') {
                if (profondeur == 0) debut = i;
                profondeur++;
            } else if (c == '}') {
                profondeur--;
                if (profondeur == 0) liste.add(json.substring(debut, i + 1));
            }
        }
        return liste;
    }

    // Extrait la valeur d'un champ d'un objet JSON plat : "champ":"texte" ou "champ":nombre.
    private static String champ(String objet, String nom) {
        int i = objet.indexOf("\"" + nom + "\"");
        if (i < 0) return "";
        i = objet.indexOf(':', i) + 1;
        while (i < objet.length() && objet.charAt(i) == ' ') i++;
        if (i >= objet.length()) return "";
        if (objet.charAt(i) == '"') {                       // valeur texte : entre guillemets
            return objet.substring(i + 1, objet.indexOf('"', i + 1));
        }
        int fin = i;                                        // valeur nombre/null : jusqu'a , ou }
        while (fin < objet.length() && objet.charAt(fin) != ',' && objet.charAt(fin) != '}') fin++;
        String valeur = objet.substring(i, fin).trim();
        return valeur.equals("null") ? "" : valeur;
    }

    private static double nombre(String objet, String nom) {
        String valeur = champ(objet, nom);
        return valeur.isBlank() ? 0 : Double.parseDouble(valeur);
    }

    private static EtatRobot etatRobot(String texte) {
        try {
            return EtatRobot.valueOf(texte.toUpperCase());
        } catch (Exception e) {
            return EtatRobot.AVAILABLE;
        }
    }

    // Le serveur attend "Available"/"Occupied"/"Disabled" (1re lettre majuscule, reste minuscule),
    // alors que l'enum donne "AVAILABLE". On convertit avant l'envoi.
    private static String etatServeur(EtatRobot etat) {
        String n = etat.name();
        return n.charAt(0) + n.substring(1).toLowerCase();
    }

    private static String get(String chemin) throws Exception {
        return requete("GET", chemin);
    }

    private static String put(String chemin) throws Exception {
        return requete("PUT", chemin);
    }

    private static String post(String chemin) throws Exception {
        return requete("POST", chemin);
    }

    // Construit la requete selon la methode (GET/POST/PUT/DELETE), l'envoie, et renvoie
    // le corps, "OK", "erreur HTTP ..." ou "ERREUR:..." si le serveur est injoignable.
    private static String requete(String methode, String chemin) {
        String urlComplete = SERVEUR + chemin;
        System.out.println();
        System.out.println("----- HTTP " + methode + " -----");
        System.out.println("URL     : " + urlComplete);
        System.out.println("Chemin  : " + chemin);
        System.out.println("Body    : <vide>");

        try {
            HttpRequest.Builder builder = HttpRequest.newBuilder()
                    .uri(URI.create(urlComplete))
                    .timeout(Duration.ofSeconds(4));
            if (methode.equals("GET")) {
                builder.GET();
            } else if (methode.equals("POST")) {
                builder.POST(HttpRequest.BodyPublishers.noBody());
            } else if (methode.equals("PUT")) {
                builder.PUT(HttpRequest.BodyPublishers.noBody());
            } else if (methode.equals("DELETE")) {
                builder.DELETE();
            }

            HttpResponse<String> reponse = HTTP.send(builder.build(), HttpResponse.BodyHandlers.ofString());
            System.out.println("Status  : " + reponse.statusCode());
            System.out.println("Reponse : " + (reponse.body() == null ? "<null>" : reponse.body()));
            System.out.println("----------------------");

            if (reponse.statusCode() != 200) {
                return "erreur HTTP " + reponse.statusCode() + " : " + reponse.body();
            }
            if (reponse.body() == null || reponse.body().equals("null")) {
                return "OK";
            }
            return reponse.body();
        } catch (Exception e) {                              // serveur eteint, mauvaise IP, reseau coupe...
            System.out.println("Erreur  : " + e.getMessage());
            System.out.println("----------------------");
            return "ERREUR: serveur injoignable (" + e.getMessage() + ")";
        }
    }

    private static String maintenant() {
        return LocalDateTime.now().format(FORMAT_DATE);
    }

    private static String enc(String texte) {
        return URLEncoder.encode(texte == null ? "" : texte, StandardCharsets.UTF_8);
    }
}
