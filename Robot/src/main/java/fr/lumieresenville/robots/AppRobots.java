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
import java.util.concurrent.atomic.AtomicBoolean;

public class AppRobots {

    private static final String SERVEUR_DEFAUT = "http://192.168.1.18:8000";
    private static String SERVEUR = SERVEUR_DEFAUT;
    private static final int BASE_X = 0;
    private static final int BASE_Y = 0;
    private static final long INTERVALLE_RECHERCHE_MS = 2000;
    private static final HttpClient HTTP = HttpClient.newHttpClient();
    private static final Scanner CLAVIER = new Scanner(System.in);
    private static final DateTimeFormatter FORMAT_DATE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    // un seul robot a la fois peut prendre une mission,
    // pour eviter que deux robots prennent la meme
    private static final Object VERROU_MISSIONS = new Object();
    private static final AtomicBoolean EN_MARCHE = new AtomicBoolean(true);

    public static void main(String[] args) throws Exception {
        SERVEUR = resoudreServeur(args);
        System.out.println("Serveur utilise : " + SERVEUR);

        ApercuGrilleRobots.lancer(SERVEUR);
        System.out.println("Apercu graphique de la grille lance.");

        if (get("/api/list_robots").startsWith("ERREUR")) {
            System.out.println("Serveur injoignable (" + SERVEUR + ").");
            System.out.println("Demarre le serveur FastAPI, puis relance.");
            return;
        }

        List<Robot> robots = lireRobotsDuServeur();
        if (robots.isEmpty()) {
            System.out.println("Aucun robot enregistre sur le serveur.");
            System.out.println("Cree des robots depuis l'IHM du serveur, puis relance.");
            return;
        }

        // Un thread par robot
        List<Thread> threads = new ArrayList<>();
        for (Robot robot : robots) {
            Thread t = new Thread(new RobotWorker(robot), "robot-" + robot.getNom());
            threads.add(t);
            t.start();
        }
        System.out.println(robots.size() + " robot demarre, chacun dans son thread.");
        System.out.println("Appuie sur Entree pour arreter.");

        try {
            CLAVIER.nextLine();
        } catch (Exception ignore) {
        }

        System.out.println("Arret demande, on attend la fin des deplacements en cours...");
        EN_MARCHE.set(false);
        for (Thread t : threads) {
            t.interrupt();
        }
        for (Thread t : threads) {
            t.join();
        }
        System.out.println("Tous les robots sont arretes. Au revoir.");
    }

    //un robot par tyhread, qui tourne en boucle pour chercher une mission, l'executer, puis revenir a la base.
    private static final class RobotWorker implements Runnable {
        private final Robot robot;

        RobotWorker(Robot robot) {
            this.robot = robot;
        }

        @Override
        public void run() {
            robot.setEtat(EtatRobot.AVAILABLE);
            try {
                modifierRobot(robot);
            } catch (Exception e) {
                log("initialisation impossible : " + e.getMessage());
            }

            while (EN_MARCHE.get()) {
                try {
                    Mission mission = reclamerProchaineMission(robot);
                    if (mission == null) {
                        Thread.sleep(INTERVALLE_RECHERCHE_MS); 
                        continue;
                    }
                    executerMission(robot, mission);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                } catch (Exception e) {
                    log("erreur pendant la mission : " + e.getMessage());
                    remettreDisponible(robot);
                }
            }
            log("thread termine.");
        }

        private void log(String message) {
            System.out.println("[" + robot.getNom() + "] " + message);
        }
    }

    // Reclame threads, la prochaine mission disponible.
    // Renvoie null si aucune mission n'est disponible.
    private static Mission reclamerProchaineMission(Robot robot) throws Exception {
        synchronized (VERROU_MISSIONS) {
            List<Mission> disponibles = lireMissionsDisponibles();
            if (disponibles.isEmpty()) {
                return null;
            }
            Mission mission = disponibles.get(0);
            // Le robot s'approprie la mission : robot_id + etat Pending_robot.
            mission.prendreEnChargeParRobot(robot.getId(), maintenant());
            robot.setEtat(EtatRobot.OCCUPIED);
            robot.setMission(mission);
            modifierMission(mission);
            modifierRobot(robot);
            System.out.println("[" + robot.getNom() + "] prend la mission " + mission.getNom()
                    + " (semaphore " + mission.getSemaphoreId() + ").");
            return mission;
        }
    }

    // Deroule une mission : aller au semaphore, signaler l'arrivee, rentrer a la base.
    private static void executerMission(Robot robot, Mission mission) throws Exception {
        String semaphoreJson = get("/api/semaphore/" + enc(mission.getSemaphoreId()));
        double coordX = nombre(semaphoreJson, "coord_x");
        double coordY = nombre(semaphoreJson, "coord_y");

        Grille.deplacer(robot, coordX, coordY);
        mission.signalerArriveeSemaphore();
        modifierMission(mission);
        System.out.println("[" + robot.getNom() + "] arrive au semaphore, mission transmise.");

        Grille.deplacer(robot, BASE_X, BASE_Y);
        remettreDisponible(robot);
        System.out.println("[" + robot.getNom() + "] rentre a la base, de nouveau disponible.");
    }

    private static void remettreDisponible(Robot robot) {
        robot.setEtat(EtatRobot.AVAILABLE);
        robot.setMission(null);
        try {
            modifierRobot(robot);
        } catch (Exception e) {
            System.out.println("[" + robot.getNom() + "] MAJ etat impossible : " + e.getMessage());
        }
    }

    // === Lectures serveur ===

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

    // missions en etat Awaiting et sans robot assigne.
    private static List<Mission> lireMissionsDisponibles() throws Exception {
        List<Mission> missions = new ArrayList<>();
        for (String objet : objets(get("/api/missions/available"))) {
            missions.add(new Mission(
                    champ(objet, "id"), champ(objet, "name"), champ(objet, "semaphore_id"),
                    champ(objet, "robot_id"), champ(objet, "state"),
                    champ(objet, "start_date"), champ(objet, "end_date"),
                    champ(objet, "team"), champ(objet, "time")));
        }
        return missions;
    }

    // === MAJ serveur ===

    static String modifierRobot(Robot robot) throws Exception {
        String url = "/api/update_robot/" + enc(robot.getId())
                + "?name=" + enc(robot.getNom())
                + "&state=" + enc(etatServeur(robot.getEtat()))
                + "&speed=" + (float) Math.round(robot.getVitesse())
                + "&position_x=" + (float) Math.round(robot.getX())
                + "&position_y=" + (float) Math.round(robot.getY());
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
                + "&team=" + enc(mission.getTeam())
                + "&time=" + enc(mission.getTempsMission());
        return put(url);
    }

    // === Resolution de l'adresse serveur (configurable) ===

    private static String resoudreServeur(String[] args) {
        if (args != null && args.length > 0 && !args[0].isBlank()) {
            return normaliserUrl(args[0]);
        }
        String env = System.getenv("LEV_SERVEUR");
        if (env != null && !env.isBlank()) {
            return normaliserUrl(env);
        }
        System.out.print("Adresse du serveur [" + SERVEUR_DEFAUT + "] : ");
        String saisie;
        try {
            saisie = CLAVIER.nextLine();
        } catch (Exception e) {
            saisie = "";
        }
        if (saisie != null && !saisie.isBlank()) {
            return normaliserUrl(saisie.trim());
        }
        return SERVEUR_DEFAUT;
    }

    private static String normaliserUrl(String url) {
        String u = url.trim();
        if (!u.startsWith("http://")) {
            u = "http://" + u;
        }
        while (u.endsWith("/")) {
            u = u.substring(0, u.length() - 1);
        }
        return u;
    }


    // Decoupe un tableau JSON 
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
// recup valeur d'un json
    private static String champ(String objet, String nom) {
        int i = objet.indexOf("\"" + nom + "\"");
        if (i < 0) return "";
        i = objet.indexOf(':', i) + 1;
        while (i < objet.length() && objet.charAt(i) == ' ') i++;
        if (i >= objet.length()) return "";
        if (objet.charAt(i) == '"') {                      
            return objet.substring(i + 1, objet.indexOf('"', i + 1));
        }
        int fin = i;                                       
        while (fin < objet.length() && objet.charAt(fin) != ',' && objet.charAt(fin) != '}') fin++;
        String valeur = objet.substring(i, fin).trim();
        return valeur.equals("null") ? "" : valeur;
    }

    static double nombre(String objet, String nom) {
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
    private static String etatServeur(EtatRobot etat) {
        String n = etat.name();
        return n.charAt(0) + n.substring(1).toLowerCase();
    }


//helper
    static String get(String chemin) throws Exception {
        return requete("GET", chemin);
    }

    private static String put(String chemin) throws Exception {
        return requete("PUT", chemin);
    }

    private static String requete(String methode, String chemin) {
        String urlComplete = SERVEUR + chemin;
        try {
            HttpRequest.Builder builder = HttpRequest.newBuilder()
                    .uri(URI.create(urlComplete))
                    .timeout(Duration.ofSeconds(4));
            switch (methode) {
                case "GET" -> builder.GET();
                case "POST" -> builder.POST(HttpRequest.BodyPublishers.noBody());
                case "PUT" -> builder.PUT(HttpRequest.BodyPublishers.noBody());
                case "DELETE" -> builder.DELETE();
                default -> builder.GET();
            }

            HttpResponse<String> reponse = HTTP.send(builder.build(), HttpResponse.BodyHandlers.ofString());
            if (reponse.statusCode() != 200) {
                return "erreur HTTP " + reponse.statusCode() + " : " + reponse.body();
            }
            if (reponse.body() == null || reponse.body().equals("null")) {
                return "OK";
            }
            return reponse.body();
        } catch (Exception e) {                              
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
