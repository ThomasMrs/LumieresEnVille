package fr.lumieresenville.robots;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.layout.Pane;
import javafx.stage.Stage;

import java.util.List;

/**
 * Simulateur de robots — affichage graphique de la carte.
 *
 * <p>On dessine la base, les routes, les sémaphores et les robots.
 * Les threads, la récupération des missions depuis le serveur et le
 * déplacement viendront dans les sous-parties suivantes.</p>
 */
public class AppRobots extends Application {

    @Override
    public void start(Stage stage) {
        // --- La base (point de départ des robots) ---
        double baseX = 80;
        double baseY = 250;

        // --- Les sémaphores : un nom et une position sur le plan ---
        List<Semaphore> semaphores = List.of(
                new Semaphore("Sémaphore Nord", 350, 80),
                new Semaphore("Sémaphore Est", 620, 200),
                new Semaphore("Sémaphore Sud", 400, 430),
                new Semaphore("Sémaphore Ouest", 560, 340));

        // --- Les robots ---
        Robot r1 = new Robot("Robot 1", baseX, baseY);              // à la base
        Robot r2 = new Robot("Robot 2", 215, 165);                 // en route vers le Nord
        r2.setMission(new Mission("Sémaphore Nord", "A", 350, 80));
        r2.setEtat(EtatRobot.EN_MISSION);
        List<Robot> robots = List.of(r1, r2);

        // --- Construction de la carte ---
        Pane plan = VueCarte.construire(baseX, baseY, semaphores, robots);

        stage.setTitle("Simulateur de robots — carte");
        stage.setScene(new Scene(plan, 720, 500));
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
