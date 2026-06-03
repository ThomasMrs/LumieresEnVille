package fr.lumieresenville.robots;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.ListView;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.util.List;

/**
 * Simulateur de robots — point de départ.
 *
 * <p>Pour l'instant : on crée quelques robots et on affiche leur état sous
 * forme de texte. L'affichage graphique, les threads et la connexion au
 * serveur viendront dans les sous-parties suivantes.</p>
 */
public class AppRobots extends Application {

    @Override
    public void start(Stage stage) {
        // --- Quelques robots de démonstration (utilise le modèle) ---
        Robot r1 = new Robot("Robot 1", 0, 0);

        Robot r2 = new Robot("Robot 2", 0, 0);
        r2.setMission(new Mission("Sémaphore Nord", "A", 100, 50));
        r2.setEtat(EtatRobot.EN_MISSION);

        List<Robot> robots = List.of(r1, r2);

        // --- Affichage texte simple ---
        ListView<String> liste = new ListView<>();
        for (Robot robot : robots) {
            liste.getItems().add(robot.toString());
        }

        VBox racine = new VBox(10, new Label("Robots :"), liste);
        racine.setPadding(new Insets(15));

        stage.setTitle("Simulateur de robots");
        stage.setScene(new Scene(racine, 460, 220));
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
