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
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class AppRobots {

    private static final String SERVEUR = "http://192.168.1.100:8000";
    private static final HttpClient HTTP = HttpClient.newHttpClient();
    private static final DateTimeFormatter FORMAT_DATE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static void main(String[] args) throws Exception {

        Robot robot1 = new Robot("Robot 1", 5, 10);
        Robot robot2 = new Robot("Robot 2", 2, 3);
        List<Robot> robots = List.of(robot1, robot2);

        System.out.println("Suppression des anciens robots : " + supprimerTousLesRobots());

        for (Robot robot : robots) {
            System.out.println("Ajout " + robot.getNom() + " : " + ajouterRobot(robot));
        }

        recupererIdsRobots(robots);
        System.out.println("Robot 1 id = " + robot1.getId());
        System.out.println("Robot 2 id = " + robot2.getId());

        Mission mission = chercherMissionDisponible();
        if (mission == null) {
            System.out.println("Aucune mission disponible.");
        } else {
            faireLaMission(robot1, mission);
        }

        while (true) {
            System.out.println(LocalTime.now().withNano(0) + " robots   : " + get("/api/list_robots"));
            System.out.println(LocalTime.now().withNano(0) + " missions : " + get("/api/list_missions"));
            Thread.sleep(5000);
        }
    }

    // Exemple simple : le robot commence puis termine une mission.
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

    // Le serveur ne renvoie pas l'id quand on ajoute un robot.
    // Donc on relit la liste des robots, puis on retrouve l'id grace au nom.
    private static void recupererIdsRobots(List<Robot> robots) throws Exception {
        JsonArray liste = lireTableauJson("/api/list_robots");

        for (Robot robot : robots) {
            for (int i = 0; i < liste.size(); i++) {
                JsonObject objet = liste.get(i).getAsJsonObject();

                if (robot.getNom().equals(texte(objet, "name"))) {
                    robot.setId(texte(objet, "id"));
                }
            }
        }
    }

    // On prend la premiere mission qui n'a pas encore de robot.
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

    private static String supprimerTousLesRobots() throws Exception {
        return delete("/api/delete_robots");
    }

    private static String ajouterRobot(Robot robot) throws Exception {
        String url = "/api/add_robot"
                + "?name=" + enc(robot.getNom())
                + "&state=" + enc(robot.getEtat().name())
                + "&speed=" + robot.getVitesse()
                + "&position_x=" + robot.getX()
                + "&position_y=" + robot.getY();

        return post(url);
    }

    private static String modifierRobot(Robot robot) throws Exception {
        String url = "/api/update_robot/" + enc(robot.getId())
                + "?name=" + enc(robot.getNom())
                + "&state=" + enc(robot.getEtat().name())
                + "&speed=" + robot.getVitesse()
                + "&position_x=" + robot.getX()
                + "&position_y=" + robot.getY();

        return put(url);
    }

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

    private static String get(String chemin) throws Exception {
        return requete("GET", chemin);
    }

    private static String post(String chemin) throws Exception {
        return requete("POST", chemin);
    }

    private static String put(String chemin) throws Exception {
        return requete("PUT", chemin);
    }

    private static String delete(String chemin) throws Exception {
        return requete("DELETE", chemin);
    }

    // Methode commune pour envoyer GET, POST, PUT ou DELETE.
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

    private static String maintenant() {
        return LocalDateTime.now().format(FORMAT_DATE);
    }

    private static String enc(String texte) {
        return URLEncoder.encode(texte == null ? "" : texte, StandardCharsets.UTF_8);
    }

}
