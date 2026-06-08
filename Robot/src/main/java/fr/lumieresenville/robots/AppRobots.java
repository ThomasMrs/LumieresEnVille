package fr.lumieresenville.robots;                       // le package (dossier logique)

import java.net.URI;                                     // pour transformer une adresse texte en URL
import java.net.URLEncoder;                              // pour encoder le texte dans l'URL (espaces, accents...)
import java.net.http.HttpClient;                         // l'outil du JDK qui envoie des requetes HTTP
import java.net.http.HttpRequest;                        // represente la requete que l'on envoie
import java.net.http.HttpResponse;                       // represente la reponse renvoyee par le serveur
import java.nio.charset.StandardCharsets;                // pour dire "encode en UTF-8"
import java.time.Duration;                               // pour exprimer une duree (le delai d'attente)
import java.time.LocalTime;                              // pour recuperer l'heure actuelle
import java.util.List;                                   // pour ranger les robots dans une liste

/**
 * Affiche dans le TERMINAL une grille 10x10 avec une base en bas (qui depasse),
 * ajoute les robots au serveur, puis liste tous les robots toutes les 5 secondes.
 */
public class AppRobots {                                 // classe principale (console)

    private static final int LIGNES = 10;                // nombre de lignes de la grille
    private static final int COLONNES = 10;              // nombre de colonnes de la grille

    // Adresse du serveur a contacter (a modifier ici si besoin)
    private static final String SERVEUR = "http://192.168.1.100:8000";

    // Un seul client HTTP, cree une fois et reutilise pour toutes les requetes
    private static final HttpClient HTTP = HttpClient.newHttpClient();

    public static void main(String[] args) throws InterruptedException {

        // --- 1) On cree quelques robots ---
        Robot r1 = new Robot("Robot 1", 5, 10);          // robot sur la base (colonne 5, ligne 10 = sous la grille)
        Robot r2 = new Robot("Robot 2", 2, 3);           // robot sur la grille (colonne 2, ligne 3)
        r2.setEtat(EtatRobot.EN_MISSION);                // ce robot est en mission
        List<Robot> robots = List.of(r1, r2);            // la liste des robots

        // --- 2) On dessine la grille dans le terminal ---
        afficherGrille(robots);                          // appelle la methode qui dessine

        // --- 3) On AJOUTE chaque robot au serveur ---
        System.out.println("=== Ajout des robots au serveur (POST /api/add_robot) ===");
        for (Robot r : robots) {                         // pour chaque robot...
            System.out.println(r.getNom() + " : " + ajouterRobot(r)); // ...on l'ajoute et on affiche le resultat
        }

        // --- 4) Toutes les 5 secondes, on LISTE tous les robots du serveur ---
        System.out.println("=== Liste des robots sur le serveur toutes les 5 s (GET /api/list_robots) ===");
        while (true) {                                   // boucle infinie : tourne jusqu'a Ctrl+C
            System.out.println(LocalTime.now().withNano(0) + "  -  " + listerRobots()); // on affiche la liste recue
            Thread.sleep(5000);                          // on met le programme en pause 5 secondes
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
            if (ligne < LIGNES) {                        // si le robot est sur la grille...
                grille[ligne][col] = marque;             // ...on le pose dans la case
            } else {                                     // sinon il est sur la base (ligne 10)...
                base = marque;                           // ...on l'affiche sur la base
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

        // d) On affiche la base, alignee sous la colonne du milieu (elle "depasse")
        int colBase = COLONNES / 2;                      // colonne du milieu (5)
        StringBuilder ligneBase = new StringBuilder();   // la ligne de la base
        for (int col = 0; col < COLONNES; col++) {       // pour chaque colonne...
            ligneBase.append(col == colBase ? base : ' ').append(' '); // base au milieu, espace ailleurs
        }
        System.out.println(ligneBase);                   // on affiche la base

        // e) Une petite legende
        System.out.println("Legende : . = case vide,  1/2 = robots,  case du bas = base");
    }

    // Ajoute un robot au serveur (POST /api/add_robot)
    private static String ajouterRobot(Robot r) {
        try {                                            // on "essaie" (le reseau peut echouer)
            String url = SERVEUR + "/api/add_robot"      // l'adresse + le chemin d'ajout
                    + "?name=" + enc(r.getNom())         // parametre name (encode pour l'URL)
                    + "&state=" + enc(r.getEtat().name()) // parametre state = nom de l'etat (ex. DISPONIBLE)
                    + "&speed=1"                         // parametre speed = vitesse (1 pour l'instant)
                    + "&position_x=" + r.getX()          // parametre position_x
                    + "&position_y=" + r.getY();         // parametre position_y
            HttpResponse<String> reponse = HTTP.send(    // on envoie la requete POST...
                    HttpRequest.newBuilder()
                            .uri(URI.create(url))        // l'adresse complete avec les parametres
                            .timeout(Duration.ofSeconds(4)) // on abandonne apres 4 s sans reponse
                            .POST(HttpRequest.BodyPublishers.noBody()) // POST sans corps (tout est dans l'URL)
                            .build(),
                    HttpResponse.BodyHandlers.ofString());
            return reponse.statusCode() == 200           // si OK...
                    ? "ajoute OK"                        // ...message de succes
                    : "erreur HTTP " + reponse.statusCode(); // sinon le code d'erreur
        } catch (Exception e) {                          // en cas de probleme reseau...
            return "echec : " + e.getMessage();          // ...on renvoie le message d'erreur
        }
    }

    // Recupere la liste de TOUS les robots du serveur (GET /api/list_robots)
    private static String listerRobots() {
        try {                                            // on "essaie" (le reseau peut echouer)
            HttpResponse<String> reponse = HTTP.send(    // on envoie la requete GET...
                    HttpRequest.newBuilder()
                            .uri(URI.create(SERVEUR + "/api/list_robots")) // le chemin pour tout lister
                            .timeout(Duration.ofSeconds(4)) // on abandonne apres 4 s sans reponse
                            .GET()                       // requete GET (on lit des donnees)
                            .build(),
                    HttpResponse.BodyHandlers.ofString());
            return reponse.statusCode() == 200           // si OK...
                    ? reponse.body()                     // ...on renvoie le contenu brut (la liste JSON)
                    : "erreur HTTP " + reponse.statusCode(); // sinon le code d'erreur
        } catch (Exception e) {                          // en cas de probleme...
            return "echec : " + e.getMessage();          // ...on renvoie le message d'erreur
        }
    }

    // Encode un texte pour qu'il soit valide dans une URL (UTF-8)
    private static String enc(String texte) {
        return URLEncoder.encode(texte, StandardCharsets.UTF_8);
    }
}
