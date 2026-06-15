package fr.lumieresenville.robots;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.Pane;
import javafx.scene.layout.StackPane;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.stage.Stage;

// Apercu graphique JavaFX de la grille (robots, semaphores, base), rafraichi toutes les 0,5 s.
// Tout le style est deporte dans src/main/resources/grille.css.
public class ApercuGrilleRobots {

    private static String SERVEUR = "http://192.168.1.18:8000";
    private static final HttpClient HTTP = HttpClient.newHttpClient();
    private static final AtomicBoolean CHARGEMENT = new AtomicBoolean(false);

    private static Pane zoneGrille;
    private static Label entete;
    private static EtatGrille dernierEtat = new EtatGrille();

    public static void main(String[] args) {
        lancer(args.length > 0 ? args[0] : SERVEUR);
    }

    public static void lancer(String serveur) {
        if (serveur != null && !serveur.isBlank()) {
            SERVEUR = serveur;
        }
        // Demarre le moteur JavaFX (une seule fois) puis construit la fenetre sur le thread FX.
        try {
            Platform.startup(ApercuGrilleRobots::construireFenetre);
        } catch (IllegalStateException dejaDemarre) {
            Platform.runLater(ApercuGrilleRobots::construireFenetre);
        }
    }

    // A appeler a la fin du programme pour arreter proprement le moteur JavaFX.
    public static void fermer() {
        try {
            Platform.exit();
        } catch (Exception ignore) {
        }
    }

    private static void construireFenetre() {
        // La fermeture de la fenetre ne doit pas tuer la console (et inversement).
        Platform.setImplicitExit(false);

        entete = new Label("Chargement...");
        entete.getStyleClass().add("entete");

        zoneGrille = new Pane();
        zoneGrille.getStyleClass().add("grille");
        // On redessine a chaque redimensionnement de la zone.
        zoneGrille.widthProperty().addListener((o, a, b) -> redessiner());
        zoneGrille.heightProperty().addListener((o, a, b) -> redessiner());

        BorderPane racine = new BorderPane();
        racine.getStyleClass().add("racine");
        racine.setTop(entete);
        racine.setCenter(zoneGrille);

        Scene scene = new Scene(racine, 760, 640);
        var css = ApercuGrilleRobots.class.getResource("/grille.css");
        if (css != null) {
            scene.getStylesheets().add(css.toExternalForm());
        }

        Stage fenetre = new Stage();
        fenetre.setTitle("Apercu - Robots et grille");
        fenetre.setScene(scene);
        fenetre.show();

        Timeline rythme = new Timeline(new KeyFrame(javafx.util.Duration.seconds(0.5), e -> rafraichir()));
        rythme.setCycleCount(Timeline.INDEFINITE);
        rythme.play();
        rafraichir();
    }

    // Va chercher les donnees serveur dans un thread de fond, puis met a jour l'UI sur le thread FX.
    private static void rafraichir() {
        if (!CHARGEMENT.compareAndSet(false, true)) {
            return;
        }
        Thread thread = new Thread(() -> {
            try {
                EtatGrille etat = lireEtatGrille();
                Platform.runLater(() -> {
                    dernierEtat = etat;
                    entete.setText(etat.message);
                    redessiner();
                });
            } finally {
                CHARGEMENT.set(false);
            }
        }, "apercu-grille-refresh");
        thread.setDaemon(true);
        thread.start();
    }

    private static void redessiner() {
        if (zoneGrille == null) {
            return;
        }
        double largeur = zoneGrille.getWidth();
        double hauteur = zoneGrille.getHeight();
        if (largeur < 60 || hauteur < 60) {
            return;
        }

        EtatGrille etat = dernierEtat;
        int colonnes = Math.max(1, etat.largeur);
        int lignes = Math.max(1, etat.hauteur);

        double marge = 60;
        double taille = Math.max(40, Math.min(
                (largeur - 2 * marge) / colonnes,
                (hauteur - 2 * marge) / lignes));
        double origineX = (largeur - (colonnes - 1) * taille) / 2;   // colonne x = 0
        double origineY = hauteur - marge;                            // base en bas, axe y vers le haut

        List<Node> elements = new ArrayList<>();

        // Mailles + noeuds seulement a partir de y = 1 (comme le schema officiel)
        dessinerSegments(elements, origineX, origineY, taille, colonnes, lignes);
        dessinerNoeuds(elements, origineX, origineY, taille, colonnes, lignes);

        // La base (0;0) est detachee sous la grille, reliee a (0;1) par un seul segment
        if (lignes > 1) {
            elements.add(segment(origineX, origineY, origineX, origineY - taille));
        }
        elements.add(marqueur("base", "BASE", origineX, origineY, taille));

        for (SemaphoreVue s : etat.semaphores) {
            elements.add(marqueur("semaphore", s.nom().isBlank() ? "S" : s.nom(),
                    origineX + s.x() * taille, origineY - s.y() * taille, taille));
        }

        // Robots au repos en (0;0) : alignes SOUS la base pour rester visibles (comme l'image)
        int totalBase = 0;
        for (RobotVue r : etat.robots) {
            if (r.x() == 0 && r.y() == 0) {
                totalBase++;
            }
        }
        int indexBase = 0;
        for (RobotVue r : etat.robots) {
            String classe = r.etat().equalsIgnoreCase("Occupied") ? "robot robot-occupe" : "robot robot-libre";
            double cx;
            double cy;
            if (r.x() == 0 && r.y() == 0) {
                double pas = Math.max(30, taille * 0.6);
                cx = origineX + (indexBase - (totalBase - 1) / 2.0) * pas;
                cy = origineY + taille * 0.55;
                indexBase++;
            } else {
                cx = origineX + r.x() * taille;
                cy = origineY - r.y() * taille;
            }
            elements.add(marqueur(classe, r.nom().isBlank() ? "R" : r.nom(), cx, cy, taille));
        }
        zoneGrille.getChildren().setAll(elements);
    }

    private static void dessinerSegments(List<Node> sortie, double ox, double oy, double taille,
                                         int colonnes, int lignes) {
        for (int y = 1; y < lignes; y++) {   // a partir de y = 1 : y = 0 est reserve a la base
            for (int x = 0; x < colonnes; x++) {
                double px = ox + x * taille;
                double py = oy - y * taille;
                if (x + 1 < colonnes) {
                    sortie.add(segment(px, py, ox + (x + 1) * taille, py));
                }
                if (y + 1 < lignes) {
                    sortie.add(segment(px, py, px, oy - (y + 1) * taille));
                }
            }
        }
    }

    private static Line segment(double x1, double y1, double x2, double y2) {
        Line ligne = new Line(x1, y1, x2, y2);
        ligne.getStyleClass().add("segment");
        return ligne;
    }

    private static void dessinerNoeuds(List<Node> sortie, double ox, double oy, double taille,
                                       int colonnes, int lignes) {
        for (int y = 1; y < lignes; y++) {   // y = 0 n'affiche que la base
            for (int x = 0; x < colonnes; x++) {
                double px = ox + x * taille;
                double py = oy - y * taille;

                Circle point = new Circle(px, py, 3);
                point.getStyleClass().add("noeud");
                sortie.add(point);

                Label coord = new Label("(" + x + ";" + y + ")");
                coord.getStyleClass().add("coord");
                coord.setLayoutX(px + 6);
                coord.setLayoutY(py - 22);
                sortie.add(coord);
            }
        }
    }

    // Pastille (StackPane) centree sur (cx, cy), stylee par CSS via ses classes.
    private static StackPane marqueur(String classes, String texte, double cx, double cy, double taille) {
        double cote = Math.max(26, taille * 0.55);
        StackPane pastille = new StackPane();
        for (String classe : classes.split(" ")) {
            pastille.getStyleClass().add(classe);
        }
        Label libelle = new Label(texte);
        libelle.getStyleClass().add("marqueur-texte");
        pastille.getChildren().add(libelle);
        pastille.setPrefSize(cote, cote);
        pastille.setLayoutX(cx - cote / 2);
        pastille.setLayoutY(cy - cote / 2);
        return pastille;
    }

    // === Lecture serveur (Java pur) ===

    private static EtatGrille lireEtatGrille() {
        EtatGrille etat = new EtatGrille();

        String grilleJson = get("/api/get_grille");
        if (grilleJson.startsWith("ERREUR") || grilleJson.startsWith("erreur HTTP")) {
            etat.message = grilleJson;
            return etat;
        }
        int largeur = (int) nombre(grilleJson, "nombre_x");
        int hauteur = (int) nombre(grilleJson, "nombre_y");
        if (largeur > 0) {
            etat.largeur = largeur;
        }
        if (hauteur > 0) {
            etat.hauteur = hauteur;
        }

        String semaphoresJson = get("/api/list_semaphore");
        if (!semaphoresJson.startsWith("ERREUR") && !semaphoresJson.startsWith("erreur HTTP")) {
            for (String objet : objets(semaphoresJson)) {
                etat.semaphores.add(new SemaphoreVue(
                        champ(objet, "name"),
                        (int) nombre(objet, "coord_x"),
                        (int) nombre(objet, "coord_y"),
                        champ(objet, "state")));
            }
        }

        String robotsJson = get("/api/list_robots");
        if (!robotsJson.startsWith("ERREUR") && !robotsJson.startsWith("erreur HTTP")) {
            for (String objet : objets(robotsJson)) {
                etat.robots.add(new RobotVue(
                        champ(objet, "name"),
                        (int) Math.round(nombre(objet, "position_x")),
                        (int) Math.round(nombre(objet, "position_y")),
                        champ(objet, "state"),
                        nombre(objet, "speed")));
            }
        }

        etat.message = "Serveur " + SERVEUR + "   |   grille " + etat.largeur + " x " + etat.hauteur
                + "   |   " + etat.semaphores.size() + " semaphore(s)   |   "
                + etat.robots.size() + " robot(s)   |   " + LocalTime.now().withNano(0);
        return etat;
    }

    private static String get(String chemin) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(SERVEUR + chemin))
                    .timeout(Duration.ofSeconds(3))
                    .GET()
                    .build();
            HttpResponse<String> response = HTTP.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200) {
                return "erreur HTTP " + response.statusCode() + " : " + response.body();
            }
            return response.body() == null ? "" : response.body();
        } catch (Exception e) {
            return "ERREUR: serveur injoignable (" + e.getMessage() + ")";
        }
    }

    private static List<String> objets(String json) {
        List<String> liste = new ArrayList<>();
        int profondeur = 0;
        int debut = -1;
        for (int i = 0; i < json.length(); i++) {
            char c = json.charAt(i);
            if (c == '{') {
                if (profondeur == 0) {
                    debut = i;
                }
                profondeur++;
            } else if (c == '}') {
                profondeur--;
                if (profondeur == 0 && debut >= 0) {
                    liste.add(json.substring(debut, i + 1));
                }
            }
        }
        return liste;
    }

    private static String champ(String objet, String nom) {
        int i = objet.indexOf("\"" + nom + "\"");
        if (i < 0) {
            return "";
        }
        i = objet.indexOf(':', i) + 1;
        while (i < objet.length() && objet.charAt(i) == ' ') {
            i++;
        }
        if (i >= objet.length()) {
            return "";
        }
        if (objet.charAt(i) == '"') {
            return objet.substring(i + 1, objet.indexOf('"', i + 1));
        }
        int fin = i;
        while (fin < objet.length() && objet.charAt(fin) != ',' && objet.charAt(fin) != '}') {
            fin++;
        }
        String valeur = objet.substring(i, fin).trim();
        return valeur.equals("null") ? "" : valeur;
    }

    private static double nombre(String objet, String nom) {
        String valeur = champ(objet, nom);
        return valeur.isBlank() ? 0 : Double.parseDouble(valeur);
    }

    private static final class EtatGrille {
        int largeur = 10;
        int hauteur = 10;
        String message = "Chargement...";
        List<SemaphoreVue> semaphores = new ArrayList<>();
        List<RobotVue> robots = new ArrayList<>();
    }

    private record SemaphoreVue(String nom, int x, int y, String etat) {
    }

    private record RobotVue(String nom, int x, int y, String etat, double vitesse) {
    }
}
