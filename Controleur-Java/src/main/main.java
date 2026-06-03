import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;

public class FenetreDeTest extends Application {

    @Override
    public void start(Stage primaryStage) {
        Button btnEnvoie = new Button("envoie");

        btnEnvoie.setOnAction(e -> System.out.println("Boum ! Tu as cliqué sur envoie."));

        StackPane root = new StackPane();
        root.getChildren().add(btnEnvoie);

        Scene scene = new Scene(root, 200, 200);

        primaryStage.setTitle("Test");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}