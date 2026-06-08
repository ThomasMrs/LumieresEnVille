package fr.lumieresenville.robots;                       // le package (dossier logique)

import java.net.URI;                                     // pour transformer une adresse texte en URL
import java.net.URLEncoder;                              // pour encoder le texte dans l'URL
import java.net.http.HttpClient;                         // l'outil du JDK qui envoie des requetes HTTP
import java.net.http.HttpRequest;                        // represente la requete que l'on envoie
import java.net.http.HttpResponse;                       // represente la reponse renvoyee par le serveur
import java.nio.charset.StandardCharsets;                // pour dire "encode en UTF-8"
import java.time.Duration;                               // pour exprimer une duree
import java.time.LocalDateTime;                          // pour dater le debut et la fin de mission
import java.time.LocalTime;                              // pour recuperer l'heure actuelle
import java.time.format.DateTimeFormatter;               // pour formater les dates
import java.util.ArrayList;                              // pour construire une liste
import java.util.List;                                   // pour ranger les robots dans une liste

public class AppRobots {                                 // classe principale (console)

    private static final int LIGNES = 10;                // nombre de lignes de la grille
    private static final int COLONNES = 10;              // nombre de colonnes de la grille
    private static final DateTimeFormatter FORMAT_DATE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"); // format envoye au serveur

    // Adresse du serveur a contacter (a modifier ici si besoin)
    private static final String SERVEUR = "http://192.168.1.100:8000";

    // Un seul client HTTP, cree une fois et reutilise pour toutes les requetes
    private static final HttpClient HTTP = HttpClient.newHttpClient();

    public static void main(String[] args) throws InterruptedException {

        // --- 1) On cree quelques robots ---
        Robot r1 = new Robot("Robot 1", 5, 10);          // robot sur la base
        Robot r2 = new Robot("Robot 2", 2, 3);           // robot sur la grille
        List<Robot> robots = List.of(r1, r2);            // la liste des robots

        // --- 2) On dessine la grille dans le terminal ---
        afficherGrille(robots);                          // appelle la methode qui dessine

        // --- 3) On nettoie les anciens robots de test sur le serveur ---
        System.out.println("=== Nettoyage des robots sur le serveur (DELETE /api/delete_robots) ===");
        System.out.println(supprimerRobots());

        // --- 4) On ajoute les robots au serveur ---
        System.out.println("=== Ajout des robots au serveur (POST /api/add_robot) ===");
        for (Robot r : robots) {                         // pour chaque robot...
            System.out.println(r.getNom() + " : " + ajouterRobot(r)); // ...on l'ajoute
        }

        // --- 5) On recupere les ids generes par le serveur ---
        System.out.println("=== Recuperation des ids robots (GET /api/list_robots) ===");
        recupererIdsRobots(robots);
        for (Robot r : robots) {
            System.out.println(r);
        }

        // --- 6) On recupere une mission et on met a jour son etat avec PUT ---
        System.out.println("=== Recuperation et traitement d'une mission (GET/PUT /api/list_missions) ===");
        traiterPremiereMission(robots);

        // --- 7) Toutes les 5 secondes, on liste robots et missions ---
        System.out.println("=== Surveillance toutes les 5 s ===");
        while (true) {                                   // boucle infinie : tourne jusqu'a Ctrl+C
            System.out.println(LocalTime.now().withNano(0) + "  robots   -  " + listerRobots());
            System.out.println(LocalTime.now().withNano(0) + "  missions -  " + listerMissions());
            Thread.sleep(5000);                          // pause 5 secondes
        }
    }

    // Dessine la grille 10x10 + la base, avec les robots dessus
    private static void afficherGrille(List<Robot> robots) {

        // a) On prepare une grille remplie de points '.'
        char[][] grille = new char[LIGNES][COLONNES];    // un tableau 10x10 de caracteres
        for (int ligne = 0; ligne < LIGNES; ligne++) {   // pour chaque ligne...
            for (int col = 0; col < COLONNES; col++) {   // ...et chaque colonne...
                grille[ligne][col] = '.';                // on met un point = case vide
            }
        }

        char base = 'B';                                 // la case base (vide = lettre 'B')

        // b) On place chaque robot (numerote 1, 2, ...) sur la grille ou la base
        for (int i = 0; i < robots.size(); i++) {        // pour chaque robot de la liste...
            Robot r = robots.get(i);                     // le robot courant
            char marque = (char) ('1' + i);              // son symbole : '1' pour le 1er, '2' pour le 2e...
            int col = (int) r.getX();                    // sa colonne (position X)
            int ligne = (int) r.getY();                  // sa ligne (position Y)
            if (ligne >= 0 && ligne < LIGNES && col >= 0 && col < COLONNES) {
                grille[ligne][col] = marque;             // on le pose dans la case
            } else {                                     // sinon il est sur la base ou hors grille
                base = marque;                           // on l'affiche sur la base
            }
        }

        // c) On affiche la grille, ligne par ligne
        System.out.println("=== Grille des robots ===");
        for (int ligne = 0; ligne < LIGNES; ligne++) {   // pour chaque ligne...
            StringBuilder texte = new StringBuilder();   // on construit la ligne de texte
            for (int col = 0; col < COLONNES; col++) {   // pour chaque colonne...
                texte.append(grille[ligne][col]).append(' '); // on ajoute la case + un espace
            }
            System.out.println(texte);                   // on affiche la ligne
        }

        // d) On affiche la base, alignee sous la colonne du milieu
        int colBase = COLONNES / 2;                      // colonne du milieu (5)
        StringBuilder ligneBase = new StringBuilder();   // la ligne de la base
        for (int col = 0; col < COLONNES; col++) {       // pour chaque colonne...
            ligneBase.append(col == colBase ? base : ' ').append(' '); // base au milieu
        }
        System.out.println(ligneBase);                   // on affiche la base

        // e) Une petite legende
        System.out.println("Legende : . = case vide,  1/2 = robots,  case du bas = base");
    }

    // Recupere les ids des robots apres leur ajout, car POST /api/add_robot ne renvoie pas l'id
    private static void recupererIdsRobots(List<Robot> robots) {
        String json = listerRobots();                    // on lit tous les robots du serveur
        for (String objet : objetsJson(json)) {          // pour chaque objet JSON recu...
            String id = champJson(objet, "id");          // id serveur
            String nom = champJson(objet, "name");       // nom du robot
            for (Robot r : robots) {
                if (r.getNom().equals(nom)) {
                    r.setId(id);                         // on relie l'objet Java a l'id serveur
                }
            }
        }
    }

    // Recupere une mission disponible, affecte un robot, puis met debut/fin a jour
    private static void traiterPremiereMission(List<Robot> robots) throws InterruptedException {
        Mission mission = recupererMissionDisponible();  // mission a faire
        if (mission == null) {
            System.out.println("Aucune mission disponible.");
            return;
        }

        Robot robot = premierRobotDisponible(robots);    // robot a affecter
        if (robot == null || estVide(robot.getId())) {
            System.out.println("Aucun robot disponible avec id serveur.");
            return;
        }

        System.out.println("Mission recuperee : " + mission);
        System.out.println("Semaphore recupere : " + lireSemaphore(mission.getSemaphoreId()));

        // Debut de mission : robot OCCUPIED, mission In progress, date de debut remplie
        String debut = maintenant();
        robot.setEtat(EtatRobot.OCCUPIED);
        robot.setMission(mission);
        mission.demarrer(robot.getId(), debut);

        System.out.println("Debut mission robot : " + debut);
        System.out.println("PUT robot debut   : " + modifierRobot(robot));
        System.out.println("PUT mission debut : " + modifierMission(mission));
        System.out.println("Mission du robot  : " + listerMissionsRobot(robot.getId()));

        // Petite simulation : le robot termine la mission quelques secondes apres
        Thread.sleep(2000);

        // Fin de mission : robot AVAILABLE, mission Done, date de fin remplie
        String fin = maintenant();
        mission.terminer(fin);
        robot.setEtat(EtatRobot.AVAILABLE);

        System.out.println("Fin mission robot : " + fin);
        System.out.println("PUT mission fin   : " + modifierMission(mission));
        robot.setMission(null);
        System.out.println("PUT robot fin     : " + modifierRobot(robot));
    }

    // Choisit la premiere mission qui n'est pas encore affectee et pas terminee
    private static Mission recupererMissionDisponible() {
        String json = listerMissions();                  // GET /api/list_missions
        for (String objet : objetsJson(json)) {
            String etat = champJson(objet, "state");
            String robotId = champJson(objet, "robot_id");
            if (estVide(robotId) && !etat.equalsIgnoreCase("Done") && !etat.equalsIgnoreCase("In progress")) {
                String team = champJson(objet, "team");
                if (estVide(team)) {
                    team = champJson(objet, "team_id");
                }
                return new Mission(
                        champJson(objet, "id"),
                        champJson(objet, "name"),
                        champJson(objet, "semaphore_id"),
                        robotId,
                        etat,
                        champJson(objet, "start_date"),
                        champJson(objet, "end_date"),
                        team
                );
            }
        }
        return null;
    }

    // Choisit le premier robot disponible dans la liste locale
    private static Robot premierRobotDisponible(List<Robot> robots) {
        for (Robot robot : robots) {
            if (robot.getEtat() == EtatRobot.AVAILABLE) {
                return robot;
            }
        }
        return null;
    }

    // Supprime tous les anciens robots du serveur (DELETE /api/delete_robots)
    private static String supprimerRobots() {
        String resultat = envoyer("DELETE", SERVEUR + "/api/delete_robots");
        return resultat.equals("OK") ? "anciens robots supprimes" : resultat;
    }

    // Ajoute un robot au serveur (POST /api/add_robot)
    private static String ajouterRobot(Robot r) {
        String url = SERVEUR + "/api/add_robot"
                + "?name=" + enc(r.getNom())
                + "&state=" + enc(r.getEtat().name())
                + "&speed=" + r.getVitesse()
                + "&position_x=" + r.getX()
                + "&position_y=" + r.getY();
        String resultat = envoyer("POST", url);
        return resultat.equals("OK") ? "ajoute OK" : resultat;
    }

    // Modifie l'etat et la position d'un robot (PUT /api/update_robot/{id})
    private static String modifierRobot(Robot r) {
        String url = SERVEUR + "/api/update_robot/" + enc(r.getId())
                + "?name=" + enc(r.getNom())
                + "&state=" + enc(r.getEtat().name())
                + "&speed=" + r.getVitesse()
                + "&position_x=" + r.getX()
                + "&position_y=" + r.getY();
        return envoyer("PUT", url);
    }

    // Modifie l'etat, le robot affecte, le debut et la fin d'une mission
    private static String modifierMission(Mission mission) {
        String url = SERVEUR + "/api/update_mission/" + enc(mission.getId())
                + "?name=" + enc(mission.getNom())
                + "&semaphore_id=" + enc(mission.getSemaphoreId())
                + "&robot_id=" + enc(mission.getRobotId())
                + "&state=" + enc(mission.getEtat())
                + "&start_date=" + enc(mission.getDebutMission())
                + "&end_date=" + enc(mission.getFinMission())
                + "&team=" + enc(mission.getTeam());
        return envoyer("PUT", url);
    }

    // Recupere la liste de tous les robots du serveur (GET /api/list_robots)
    private static String listerRobots() {
        return envoyer("GET", SERVEUR + "/api/list_robots");
    }

    // Recupere la liste de toutes les missions du serveur (GET /api/list_missions)
    private static String listerMissions() {
        return envoyer("GET", SERVEUR + "/api/list_missions");
    }

    // Recupere les missions affectees a un robot (GET /api/robot/{id}/mission)
    private static String listerMissionsRobot(String robotId) {
        return envoyer("GET", SERVEUR + "/api/robot/" + enc(robotId) + "/mission");
    }

    // Recupere le semaphore lie a une mission (GET /api/semaphore/{id})
    private static String lireSemaphore(String semaphoreId) {
        if (estVide(semaphoreId)) {
            return "aucun semaphore_id";
        }
        return envoyer("GET", SERVEUR + "/api/semaphore/" + enc(semaphoreId));
    }

    // Envoie une requete HTTP simple sans corps
    private static String envoyer(String methode, String url) {
        try {
            HttpRequest.Builder builder = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .timeout(Duration.ofSeconds(4));

            if ("GET".equals(methode)) {
                builder.GET();
            } else if ("POST".equals(methode)) {
                builder.POST(HttpRequest.BodyPublishers.noBody());
            } else if ("PUT".equals(methode)) {
                builder.PUT(HttpRequest.BodyPublishers.noBody());
            } else if ("DELETE".equals(methode)) {
                builder.DELETE();
            } else {
                return "methode HTTP inconnue : " + methode;
            }

            HttpResponse<String> reponse = HTTP.send(builder.build(), HttpResponse.BodyHandlers.ofString());
            String body = reponse.body() == null ? "" : reponse.body().trim();
            if (reponse.statusCode() == 200) {
                return body.isEmpty() || body.equals("null") ? "OK" : body;
            }
            return "erreur HTTP " + reponse.statusCode() + " : " + body;
        } catch (Exception e) {
            return "echec : " + e.getMessage();
        }
    }

    // Extrait les objets JSON contenus dans une liste JSON
    private static List<String> objetsJson(String json) {
        List<String> objets = new ArrayList<>();
        if (json == null) {
            return objets;
        }

        boolean dansTexte = false;
        boolean echappe = false;
        int profondeur = 0;
        int debut = -1;

        for (int i = 0; i < json.length(); i++) {
            char c = json.charAt(i);

            if (dansTexte) {
                if (echappe) {
                    echappe = false;
                } else if (c == '\\') {
                    echappe = true;
                } else if (c == '"') {
                    dansTexte = false;
                }
                continue;
            }

            if (c == '"') {
                dansTexte = true;
            } else if (c == '{') {
                if (profondeur == 0) {
                    debut = i;
                }
                profondeur++;
            } else if (c == '}') {
                profondeur--;
                if (profondeur == 0 && debut >= 0) {
                    objets.add(json.substring(debut, i + 1));
                    debut = -1;
                }
            }
        }
        return objets;
    }

    // Lit une valeur simple dans un objet JSON plat
    private static String champJson(String objet, String champ) {
        String cle = "\"" + champ + "\":";
        int position = objet.indexOf(cle);
        if (position < 0) {
            return "";
        }

        int debut = position + cle.length();
        while (debut < objet.length() && Character.isWhitespace(objet.charAt(debut))) {
            debut++;
        }

        if (debut >= objet.length() || objet.startsWith("null", debut)) {
            return "";
        }

        if (objet.charAt(debut) == '"') {
            StringBuilder valeur = new StringBuilder();
            boolean echappe = false;
            for (int i = debut + 1; i < objet.length(); i++) {
                char c = objet.charAt(i);
                if (echappe) {
                    valeur.append(c);
                    echappe = false;
                } else if (c == '\\') {
                    echappe = true;
                } else if (c == '"') {
                    return valeur.toString();
                } else {
                    valeur.append(c);
                }
            }
            return valeur.toString();
        }

        int fin = debut;
        while (fin < objet.length() && objet.charAt(fin) != ',' && objet.charAt(fin) != '}') {
            fin++;
        }
        return objet.substring(debut, fin).trim();
    }

    // Date/heure actuelle envoyee dans start_date et end_date
    private static String maintenant() {
        return LocalDateTime.now().format(FORMAT_DATE);
    }

    // Teste les valeurs absentes dans les reponses JSON
    private static boolean estVide(String texte) {
        return texte == null || texte.isBlank() || texte.equalsIgnoreCase("null");
    }

    // Encode un texte pour qu'il soit valide dans une URL (UTF-8)
    private static String enc(String texte) {
        return URLEncoder.encode(texte == null ? "" : texte, StandardCharsets.UTF_8);
    }
}
