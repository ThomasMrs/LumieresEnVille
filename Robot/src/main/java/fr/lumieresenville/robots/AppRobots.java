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
import java.util.Scanner;

public class AppRobots {

    private static final String SERVEUR = "http://192.168.1.14:8000";
    private static final HttpClient HTTP = HttpClient.newHttpClient();
    private static final Scanner CLAVIER = new Scanner(System.in);
    private static final DateTimeFormatter FORMAT_DATE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static void main(String[] args) throws Exception {
        if (get("/api/list_robots").startsWith("ERREUR")) {
            System.out.println("Serveur injoignable (" + SERVEUR + ").");
            System.out.println("Demarre le serveur FastAPI, puis relance.");
            return;
        }

        List<Robot> robots = lireRobotsDuServeur();

        if (robots.isEmpty()) {
            System.out.println("Aucun robot trouve sur le serveur.");
        } else {
            for (Robot robot : robots) {
                System.out.println("Robot trouve : " + robot);
            }
        }

        Robot robotDisponible = chercherRobotDisponible(robots);
        Mission mission = choisirMissionDansTerminal();

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

    // Deroulement d'une mission : robot -> OCCUPIED et mission -> "In progress",
    // puis apres 2 s mission -> "Done" et robot -> AVAILABLE.
    // Chaque changement est sauvegarde sur le serveur (PUT).
    private static void faireLaMission(Robot robot, Mission mission) throws Exception {
        System.out.println("Mission choisie : " + mission);
        System.out.println("Semaphore lie   : " + get("/api/semaphore/" + enc(mission.getSemaphoreId())));

        mission.demarrer(robot.getId(), maintenant());
        robot.setEtat(EtatRobot.OCCUPIED);
        System.out.println("PUT robot   : " + modifierRobot(robot));
        System.out.println("PUT mission : " + modifierMission(mission));

        Thread.sleep(2000);

        mission.terminer(maintenant());
        robot.setEtat(EtatRobot.AVAILABLE);
        System.out.println("PUT mission : " + modifierMission(mission));
        System.out.println("PUT robot   : " + modifierRobot(robot));
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

    private static Mission choisirMissionDansTerminal() throws Exception {
        List<Mission> missions = lireMissions();
        if (missions.isEmpty()) {
            return null;
        }

        System.out.println("=== Missions (" + missions.size() + ") ===");
        for (int i = 0; i < missions.size(); i++) {
            Mission mission = missions.get(i);
            String libre = mission.getRobotId().isBlank() ? "libre" : "occupee";
            System.out.println((i + 1) + " - " + mission.getNom()
                    + " | etat : " + mission.getEtat()
                    + " | " + libre
                    + " | equipe : " + mission.getTeam());
        }

        while (true) {
            System.out.print("Choisis une mission (1 a " + missions.size() + ") : ");
            String reponse = CLAVIER.nextLine();
            try {
                int numero = Integer.parseInt(reponse);
                if (numero >= 1 && numero <= missions.size()) {
                    return missions.get(numero - 1);
                }
            } catch (NumberFormatException e) {
                // entree non numerique : on redemande
            }
            System.out.println("Numero invalide.");
        }
    }

    private static List<Mission> lireMissions() throws Exception {
        List<Mission> missions = new ArrayList<>();
        for (String objet : objets(get("/api/list_missions"))) {
            missions.add(new Mission(
                    champ(objet, "id"), champ(objet, "name"), champ(objet, "semaphore_id"),
                    champ(objet, "robot_id"), champ(objet, "state"),
                    champ(objet, "start_date"), champ(objet, "end_date"), champ(objet, "team")));
        }
        return missions;
    }

    private static String modifierRobot(Robot robot) throws Exception {
        String url = "/api/update_robot/" + enc(robot.getId())
                + "?name=" + enc(robot.getNom())
                + "&state=" + enc(robot.getEtat().name())
                + "&speed=" + (int) Math.round(robot.getVitesse()) // le serveur veut un entier
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

    private static String get(String chemin) throws Exception {
        return requete("GET", chemin);
    }

    private static String put(String chemin) throws Exception {
        return requete("PUT", chemin);
    }

    // Construit la requete selon la methode (GET/POST/PUT/DELETE), l'envoie, et renvoie
    // le corps, "OK", "erreur HTTP ..." ou "ERREUR:..." si le serveur est injoignable.
    private static String requete(String methode, String chemin) {
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
        try {
            HttpResponse<String> reponse = HTTP.send(builder.build(), HttpResponse.BodyHandlers.ofString());
            if (reponse.statusCode() != 200) {
                return "erreur HTTP " + reponse.statusCode() + " : " + reponse.body();
            }
            if (reponse.body() == null || reponse.body().equals("null")) {
                return "OK";
            }
            return reponse.body();
        } catch (Exception e) {                              // serveur eteint, mauvaise IP, reseau coupe...
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
