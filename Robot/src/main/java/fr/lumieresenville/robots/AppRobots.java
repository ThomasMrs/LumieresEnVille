package fr.lumieresenville.robots;                          // le package (dossier logique) de la classe
import java.net.URI;                                         // pour transformer une adresse texte en URL
import java.net.URLEncoder;                                  // pour encoder le texte dans l'URL (espaces, accents...)
import java.net.http.HttpClient;                             // l'outil du JDK qui envoie des requetes HTTP
import java.net.http.HttpRequest;                            // represente la requete que l'on envoie
import java.net.http.HttpResponse;                           // represente la reponse renvoyee par le serveur
import java.nio.charset.StandardCharsets;                    // pour dire "encode en UTF-8"
import java.time.Duration;                                   // pour exprimer une duree (le delai d'attente)
import java.time.LocalTime;                                  // pour recuperer l'heure actuelle
import java.util.List;                                       // pour ranger les robots dans une liste

public class AppRobots {                                     // debut de la classe principale
    private static final String SERVEUR = "http://192.168.1.100:8000";
    private static final HttpClient HTTP = HttpClient.newHttpClient();
    public static void main(String[] args) throws InterruptedException {

        // --- 1) On cree quelques robots (on utilise le modele) ---
        Robot r1 = new Robot("Robot 1", 0, 0);               // un robot a la base (position 0,0), sans mission
        Robot r2 = new Robot("Robot 2", 0, 0);               // un deuxieme robot
        r2.setMission(new Mission("Semaphore Nord", "A", 100, 50)); // on lui confie une mission
        r2.setEtat(EtatRobot.EN_MISSION);                    // et on passe son etat a EN_MISSION
        List<Robot> robots = List.of(r1, r2);                // on range les deux robots dans une liste

        // --- 2) On affiche les robots dans le terminal ---
        System.out.println("=== Robots ===");                // un titre
        for (Robot r : robots) {                             // pour chaque robot de la liste...
            System.out.println(r);                           // ...on l'affiche (Java appelle son toString())
        }

        // --- 3) Toutes les 5 secondes, chaque robot envoie son etat au serveur ---
        System.out.println("=== Envoi au serveur toutes les 5 s (Ctrl+C pour arreter) ===");
        while (true) {                                       // boucle infinie : tourne jusqu'a Ctrl+C
            for (Robot r : robots) {                         // pour chaque robot...
                String resultat = envoyerRobot(r);           // ...on envoie son etat au serveur
                System.out.println(LocalTime.now().withNano(0) + "  -  " + r.getNom() + " : " + resultat); // heure + nom + resultat
            }
            Thread.sleep(5000);                              // on met le programme en pause 5000 ms = 5 secondes
        }
    }

    // Envoie l'etat d'un robot au serveur via POST /post_robots
    private static String envoyerRobot(Robot r) {
        try {                                                // on "essaie" (le reseau peut echouer)
            String url = SERVEUR + "/post_robots"            // l'adresse du serveur + le chemin
                    + "?nom=" + enc(r.getNom())              // parametre nom (encode pour l'URL)
                    + "&position_x=" + r.getX()              // parametre position_x
                    + "&position_y=" + r.getY()              // parametre position_y
                    + "&statut=" + enc(r.getEtat().name())   // parametre statut = nom de l'etat (ex. DISPONIBLE)
                    + "&disponible=" + (r.getEtat() == EtatRobot.DISPONIBLE ? 1 : 0); // 1 si dispo, sinon 0
            HttpRequest requete = HttpRequest.newBuilder()   // on commence a construire la requete
                    .uri(URI.create(url))                    // l'adresse complete avec les parametres
                    .timeout(Duration.ofSeconds(4))          // on abandonne s'il n'y a pas de reponse en 4 s
                    .POST(HttpRequest.BodyPublishers.noBody()) // requete POST, sans corps (tout est dans l'URL)
                    .build();                                // la requete est terminee
            HttpResponse<String> reponse =                   // on envoie la requete et on stocke la reponse
                    HTTP.send(requete, HttpResponse.BodyHandlers.ofString());
            return reponse.statusCode() == 200               // si le code de reponse vaut 200 (= OK)...
                    ? "envoye OK"                            // ...message de succes
                    : "erreur HTTP " + reponse.statusCode(); // sinon on montre le code recu
        } catch (Exception e) {                              // si une erreur survient (serveur eteint, etc.)
            return "echec : " + e.getMessage();              // on renvoie le message d'erreur
        }
    }

    // Encode un texte pour qu'il soit valide dans une URL (UTF-8)
    private static String enc(String texte) {
        return URLEncoder.encode(texte, StandardCharsets.UTF_8);
    }
}
