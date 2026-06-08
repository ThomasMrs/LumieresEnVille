package fr.lumieresenville.robots;

import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class AppRobots {

    /*
     * =========================
     * CONFIGURATION GENERALE
     * =========================
     *
     * SERVEUR : adresse du serveur FastAPI.
     * HTTP : objet Java qui envoie toutes les requetes au serveur.
     * FORMAT_DATE : format utilise pour start_date et end_date.
     */
    private static final String SERVEUR = "http://192.168.1.100:8000";
    private static final HttpClient HTTP = HttpClient.newHttpClient();
    private static final DateTimeFormatter FORMAT_DATE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    /*
     * =========================
     * PROGRAMME PRINCIPAL
     * =========================
     *
     * Ordre du programme :
     * 1. lire les robots deja presents sur le serveur
     * 2. chercher un robot disponible
     * 3. chercher une mission disponible
     * 4. faire la mission si tout existe
     * 5. afficher regulierement les robots et les missions
     */
    public static void main(String[] args) throws Exception {

        List<Robot> robots = lireRobotsDuServeur();

        if (robots.isEmpty()) {
            System.out.println("Aucun robot trouve sur le serveur.");
        } else {
            for (Robot robot : robots) {
                System.out.println("Robot trouve : " + robot);
            }
        }

        Robot robotDisponible = chercherRobotDisponible(robots);
        Mission mission = chercherMissionDisponible();

        if (mission == null) {
            System.out.println("Aucune mission disponible.");
        } else if (robotDisponible == null) {
            System.out.println("Aucun robot disponible.");
        } else {
            faireLaMission(robotDisponible, mission);
        }

        while (true) {
            System.out.println(LocalTime.now().withNano(0) + " robots   : " + get("/api/list_robots"));
            System.out.println(LocalTime.now().withNano(0) + " missions : " + get("/api/list_missions"));
            Thread.sleep(5000);
        }
    }

    /*
     * =========================
     * DEROULEMENT D'UNE MISSION
     * =========================
     *
     * Le robot prend une mission, passe en OCCUPIED, puis la mission passe
     * en "In progress". Apres une courte attente, la mission passe en "Done"
     * et le robot redevient AVAILABLE.
     */
    private static void faireLaMission(Robot robot, Mission mission) throws Exception {
        System.out.println("Mission choisie : " + mission);
        System.out.println("Semaphore lie   : " + get("/api/semaphore/" + enc(mission.getSemaphoreId())));

        mission.demarrer(robot.getId(), maintenant());
        robot.setEtat(EtatRobot.OCCUPIED);

        System.out.println("Debut mission : " + mission.getDebutMission());
        System.out.println("PUT robot     : " + modifierRobot(robot));
        System.out.println("PUT mission   : " + modifierMission(mission));

        Thread.sleep(2000);

        mission.terminer(maintenant());
        robot.setEtat(EtatRobot.AVAILABLE);

        System.out.println("Fin mission   : " + mission.getFinMission());
        System.out.println("PUT mission   : " + modifierMission(mission));
        System.out.println("PUT robot     : " + modifierRobot(robot));
    }

    /*
     * =========================
     * LECTURE DES ROBOTS
     * =========================
     *
     * Le serveur renvoie une liste JSON. Chaque objet JSON est transforme
     * en objet Robot Java pour pouvoir travailler plus simplement.
     */
    private static List<Robot> lireRobotsDuServeur() throws Exception {
        JsonArray liste = lireTableauJson("/api/list_robots");
        List<Robot> robots = new ArrayList<>();

        for (int i = 0; i < liste.size(); i++) {
            JsonObject objet = liste.get(i).getAsJsonObject();

            Robot robot = new Robot(
                    texte(objet, "name"),
                    nombre(objet, "position_x"),
                    nombre(objet, "position_y")
            );

            robot.setId(texte(objet, "id"));
            robot.setVitesse(nombre(objet, "speed"));
            robot.setEtat(etatRobot(texte(objet, "state")));
            robots.add(robot);
        }

        return robots;
    }

    /*
     * =========================
     * CHOIX DU ROBOT
     * =========================
     *
     * On prend le premier robot dont l'etat est AVAILABLE.
     */
    private static Robot chercherRobotDisponible(List<Robot> robots) {
        for (Robot robot : robots) {
            if (robot.getEtat() == EtatRobot.AVAILABLE) {
                return robot;
            }
        }

        return null;
    }

    /*
     * =========================
     * CHOIX DE LA MISSION
     * =========================
     *
     * On prend la premiere mission qui :
     * - n'a pas encore de robot_id
     * - n'est pas deja en cours
     * - n'est pas deja terminee
     */
    private static Mission chercherMissionDisponible() throws Exception {
        JsonArray liste = lireTableauJson("/api/list_missions");

        for (int i = 0; i < liste.size(); i++) {
            JsonObject objet = liste.get(i).getAsJsonObject();

            String robotId = texte(objet, "robot_id");
            String etat = texte(objet, "state");

            if (robotId.isBlank() && !etat.equals("In progress") && !etat.equals("Done")) {
                return new Mission(
                        texte(objet, "id"),
                        texte(objet, "name"),
                        texte(objet, "semaphore_id"),
                        robotId,
                        etat,
                        texte(objet, "start_date"),
                        texte(objet, "end_date"),
                        texte(objet, "team")
                );
            }
        }

        return null;
    }

    /*
     * =========================
     * MODIFICATION DU ROBOT
     * =========================
     *
     * Cette methode envoie un PUT au serveur pour sauvegarder l'etat actuel
     * du robot : nom, etat, vitesse et position.
     */
    private static String modifierRobot(Robot robot) throws Exception {
        String url = "/api/update_robot/" + enc(robot.getId())
                + "?name=" + enc(robot.getNom())
                + "&state=" + enc(robot.getEtat().name())
                + "&speed=" + robot.getVitesse()
                + "&position_x=" + robot.getX()
                + "&position_y=" + robot.getY();

        return put(url);
    }

    /*
     * =========================
     * MODIFICATION DE LA MISSION
     * =========================
     *
     * Cette methode envoie un PUT au serveur pour sauvegarder la mission :
     * robot affecte, etat, date de debut, date de fin et equipe.
     */
    private static String modifierMission(Mission mission) throws Exception {
        String url = "/api/update_mission/" + enc(mission.getId())
                + "?name=" + enc(mission.getNom())
                + "&semaphore_id=" + enc(mission.getSemaphoreId())
                + "&robot_id=" + enc(mission.getRobotId())
                + "&state=" + enc(mission.getEtat())
                + "&start_date=" + enc(mission.getDebutMission())
                + "&end_date=" + enc(mission.getFinMission())
                + "&team=" + enc(mission.getTeam());

        return put(url);
    }

    /*
     * =========================
     * LECTURE DU JSON
     * =========================
     *
     * Gson transforme le texte JSON du serveur en objets Java.
     * JsonArray = une liste JSON.
     * JsonObject = un objet dans cette liste.
     */
    private static JsonArray lireTableauJson(String chemin) throws Exception {
        String reponse = get(chemin);
        return JsonParser.parseString(reponse).getAsJsonArray();
    }

    private static String texte(JsonObject objet, String nomChamp) {
        if (!objet.has(nomChamp) || objet.get(nomChamp).isJsonNull()) {
            return "";
        }

        return objet.get(nomChamp).getAsString();
    }

    private static double nombre(JsonObject objet, String nomChamp) {
        if (!objet.has(nomChamp) || objet.get(nomChamp).isJsonNull()) {
            return 0;
        }

        return objet.get(nomChamp).getAsDouble();
    }

    /*
     * =========================
     * CONVERSION DE L'ETAT
     * =========================
     *
     * Le serveur renvoie l'etat sous forme de texte.
     * Cette methode transforme ce texte en valeur EtatRobot.
     */
    private static EtatRobot etatRobot(String texte) {
        try {
            return EtatRobot.valueOf(texte.toUpperCase());
        } catch (Exception e) {
            return EtatRobot.AVAILABLE;
        }
    }

    private static String get(String chemin) throws Exception {
        return requete("GET", chemin);
    }

    private static String put(String chemin) throws Exception {
        return requete("PUT", chemin);
    }

    /*
     * =========================
     * REQUETES HTTP
     * =========================
     *
     * Methode commune pour envoyer les requetes au serveur.
     * Elle recoit le type de requete (GET, PUT...) et le chemin de l'API.
     */
    private static String requete(String methode, String chemin) throws Exception {
        HttpRequest.Builder builder = HttpRequest.newBuilder()
                .uri(URI.create(SERVEUR + chemin))
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

        if (reponse.statusCode() != 200) {
            return "erreur HTTP " + reponse.statusCode() + " : " + reponse.body();
        }

        if (reponse.body() == null || reponse.body().equals("null")) {
            return "OK";
        }

        return reponse.body();
    }

    /*
     * =========================
     * PETITS OUTILS
     * =========================
     *
     * maintenant() donne la date actuelle.
     * enc() rend un texte utilisable dans une URL.
     */
    private static String maintenant() {
        return LocalDateTime.now().format(FORMAT_DATE);
    }

    private static String enc(String texte) {
        return URLEncoder.encode(texte == null ? "" : texte, StandardCharsets.UTF_8);
    }

}
