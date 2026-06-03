package fr.lumieresenville.robots;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.ListView;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.LocalTime;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Simulateur de robots.
 *
 * <p>Affiche les robots dans la fenêtre et se connecte au serveur <b>toutes
 * les 5 secondes</b>. Le résultat de chaque connexion est affiché dans le
 * terminal (la requête tourne dans un thread d'arrière-plan).</p>
 */
public class AppRobots extends Application {

    /** Adresse du serveur (à modifier si besoin). */
    private static final String SERVEUR = "http://192.168.1.100:8000";

    private final HttpClient http = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(3))
            .build();

    /** Tâche périodique (toutes les 5 s). */
    private ScheduledExecutorService minuteur;

    @Override
    public void start(Stage stage) {
        // --- Quelques robots de démonstration ---
        Robot r1 = new Robot("Robot 1", 0, 0);
        Robot r2 = new Robot("Robot 2", 0, 0);
        r2.setMission(new Mission("Sémaphore Nord", "A", 100, 50));
        r2.setEtat(EtatRobot.EN_MISSION);
        List<Robot> robots = List.of(r1, r2);

        ListView<String> listeRobots = new ListView<>();
        for (Robot robot : robots) {
            listeRobots.getItems().add(robot.toString());
        }

        VBox racine = new VBox(10, new Label("Robots :"), listeRobots);
        racine.setPadding(new Insets(15));

        stage.setTitle("Simulateur de robots");
        stage.setScene(new Scene(racine, 460, 220));
        stage.show();

        demarrerConnexionPeriodique();
    }

    /** Interroge le serveur toutes les 5 secondes et affiche le résultat dans le terminal. */
    private void demarrerConnexionPeriodique() {
        minuteur = Executors.newSingleThreadScheduledExecutor(tache -> {
            Thread t = new Thread(tache, "robot-connexion");
            t.setDaemon(true); // ne bloque pas la fermeture de l'appli
            return t;
        });
        minuteur.scheduleAtFixedRate(() -> {
            String ligne = LocalTime.now().withNano(0) + "  -  " + interrogerServeur();
            System.out.println(ligne);
        }, 0, 5, TimeUnit.SECONDS);
    }

    /** Une requête GET vers le serveur ; renvoie un message lisible. */
    private String interrogerServeur() {
        try {
            HttpResponse<String> rep = http.send(
                    HttpRequest.newBuilder()
                            .uri(URI.create(SERVEUR + "/get_semaphore"))
                            .timeout(Duration.ofSeconds(4))
                            .GET().build(),
                    HttpResponse.BodyHandlers.ofString());
            return rep.statusCode() == 200 ? "Connecte OK" : "Erreur HTTP " + rep.statusCode();
        } catch (Exception e) {
            return "Echec : " + e.getMessage();
        }
    }

    @Override
    public void stop() {
        if (minuteur != null) {
            minuteur.shutdownNow();
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
