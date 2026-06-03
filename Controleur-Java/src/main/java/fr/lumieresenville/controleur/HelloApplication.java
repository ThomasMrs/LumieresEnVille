package fr.lumieresenville.controleur;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;

import java.net.HttpURLConnection;
import java.net.URL;

public class HelloApplication extends Application {

    @Override
    public void start(Stage primaryStage) {
        Button btnEnvoie = new Button("Envoyer l'ordre au serveur");

        btnEnvoie.setOnAction(e -> {
            try {
                // L'adresse exacte confirmée par ton pote
                String adresse = "http://192.168.1.100:8000/get_semaphore" +
                        "?nom=Semaphore1" +
                        "&caractere_affiche=a" +
                        "&disponible=1" +
                        "&etat=allume";

                System.out.println("Tentative d'envoi vers : " + adresse);

                // On prépare la connexion HTTP classique
                URL url = new URL(adresse);
                HttpURLConnection connexion = (HttpURLConnection) url.openConnection();
                
                // On utilise la méthode GET exigée par le serveur Python
                connexion.setRequestMethod("GET");

                // On tape à la porte du serveur et on attend sa réponse
                int codeReponse = connexion.getResponseCode();
                
                if (codeReponse == 200) {
                    System.out.println("✅ SUCCÈS ! Le serveur Python a bien reçu la commande (Code 200).");
                } else {
                    System.out.println("❌ Le serveur a répondu avec une erreur : " + codeReponse);
                }

            } catch (Exception erreur) {
                System.out.println("Impossible de joindre le serveur : " + erreur.getMessage());
            }
        });

        StackPane root = new StackPane();
        root.getChildren().add(btnEnvoie);

        Scene scene = new Scene(root, 350, 200);

        primaryStage.setTitle("Contrôleur - Jalon 1");
        primaryStage.setScene(scene);
        primaryStage.show();
    }
}