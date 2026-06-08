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

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class AppRobots {

    // Adresse du serveur FastAPI utilise par le programme.
    private static final String SERVEUR = "http://192.168.1.100:8000";

    // Objet Java utilise pour envoyer les requetes HTTP au serveur.
    private static final HttpClient HTTP = HttpClient.newHttpClient();

    // Scanner utilise pour lire le numero de mission tape dans le terminal.
    private static final Scanner CLAVIER = new Scanner(System.in);

    // Format utilise pour envoyer start_date et end_date au serveur.
    private static final DateTimeFormatter FORMAT_DATE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    // Methode principale :
    // lit les robots du serveur, choisit un robot disponible,
    // demande une mission dans le terminal, puis lance la mission.
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

    // Cette methode simule le deroulement d'une mission :
    // le robot passe en OCCUPIED, la mission passe en "In progress",
    // puis apres 2 secondes la mission passe en "Done" et le robot redevient AVAILABLE.
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

    // Cette methode recupere les robots deja presents sur le serveur :
    // elle lit le JSON de /api/list_robots et transforme chaque robot JSON en objet Robot Java.
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

    // Cette methode cherche le premier robot disponible dans la liste.
    private static Robot chercherRobotDisponible(List<Robot> robots) {
        for (Robot robot : robots) {
            if (robot.getEtat() == EtatRobot.AVAILABLE) {
                return robot;
            }
        }

        return null;
    }

    // Cette methode affiche les missions disponibles dans le terminal :
    // l'utilisateur choisit une mission en tapant son numero.
    private static Mission choisirMissionDansTerminal() throws Exception {
        List<Mission> missions = lireMissionsDisponibles();

        if (missions.isEmpty()) {
            return null;
        }

        System.out.println("=== Missions disponibles ===");
        for (int i = 0; i < missions.size(); i++) {
            Mission mission = missions.get(i);
            System.out.println((i + 1) + " - "
                    + mission.getNom()
                    + " | semaphore : " + mission.getSemaphoreId()
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
                // Si l'utilisateur n'a pas tape un nombre, on redemande.
            }

            System.out.println("Numero invalide.");
        }
    }

    // Cette methode recupere les missions disponibles :
    // elle garde seulement les missions sans robot affecte,
    // pas encore en cours et pas encore terminees.
    private static List<Mission> lireMissionsDisponibles() throws Exception {
        JsonArray liste = lireTableauJson("/api/list_missions");
        List<Mission> missions = new ArrayList<>();

        for (int i = 0; i < liste.size(); i++) {
            JsonObject objet = liste.get(i).getAsJsonObject();

            String robotId = texte(objet, "robot_id");
            String etat = texte(objet, "state");

            if (robotId.isBlank() && !etat.equalsIgnoreCase("In progress") && !etat.equalsIgnoreCase("Done")) {
                Mission mission = new Mission(
                        texte(objet, "id"),
                        texte(objet, "name"),
                        texte(objet, "semaphore_id"),
                        robotId,
                        etat,
                        texte(objet, "start_date"),
                        texte(objet, "end_date"),
                        texte(objet, "team")
                );

                missions.add(mission);
            }
        }

        return missions;
    }

    // Cette methode envoie un PUT au serveur pour sauvegarder le robot :
    // nom, etat, vitesse, position_x et position_y.
    private static String modifierRobot(Robot robot) throws Exception {
        String url = "/api/update_robot/" + enc(robot.getId())
                + "?name=" + enc(robot.getNom())
                + "&state=" + enc(robot.getEtat().name())
                + "&speed=" + robot.getVitesse()
                + "&position_x=" + robot.getX()
                + "&position_y=" + robot.getY();

        return put(url);
    }

    // Cette methode envoie un PUT au serveur pour sauvegarder la mission :
    // robot affecte, etat, date de debut, date de fin et equipe.
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

    // Cette methode lit une route qui renvoie une liste JSON :
    // exemple /api/list_robots ou /api/list_missions.
    private static JsonArray lireTableauJson(String chemin) throws Exception {
        String reponse = get(chemin);
        return JsonParser.parseString(reponse).getAsJsonArray();
    }

    // Cette methode lit un texte dans un objet JSON :
    // si le champ est absent ou null, elle renvoie une chaine vide.
    private static String texte(JsonObject objet, String nomChamp) {
        if (!objet.has(nomChamp) || objet.get(nomChamp).isJsonNull()) {
            return "";
        }

        return objet.get(nomChamp).getAsString();
    }

    // Cette methode lit un nombre dans un objet JSON :
    // si le champ est absent ou null, elle renvoie 0.
    private static double nombre(JsonObject objet, String nomChamp) {
        if (!objet.has(nomChamp) || objet.get(nomChamp).isJsonNull()) {
            return 0;
        }

        return objet.get(nomChamp).getAsDouble();
    }

    // Cette methode transforme le texte recu du serveur en EtatRobot.
    private static EtatRobot etatRobot(String texte) {
        try {
            return EtatRobot.valueOf(texte.toUpperCase());
        } catch (Exception e) {
            return EtatRobot.AVAILABLE;
        }
    }

    // Cette methode envoie une requete GET.
    private static String get(String chemin) throws Exception {
        return requete("GET", chemin);
    }

    // Cette methode envoie une requete PUT.
    private static String put(String chemin) throws Exception {
        return requete("PUT", chemin);
    }

    // Cette methode envoie une requete HTTP au serveur :
    // elle construit la requete, l'envoie, puis renvoie le texte de la reponse.
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

    // Cette methode donne la date actuelle au format attendu par le serveur.
    private static String maintenant() {
        return LocalDateTime.now().format(FORMAT_DATE);
    }

    // Cette methode encode un texte pour qu'il soit utilisable dans une URL.
    private static String enc(String texte) {
        return URLEncoder.encode(texte == null ? "" : texte, StandardCharsets.UTF_8);
    }
}
