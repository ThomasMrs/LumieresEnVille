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
// Grille centree sur x = 0 : la base (0;0) est detachee en bas, le maillage commence a y = 1.
// Tout le style est deporte dans src/main/resources/grille.css.
public class ApercuGrilleRobots {

    private static String SERVEUR = "http://192.168.1.96:8000";
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
        // Fermer la fenetre ne doit pas tuer la console (et inversement).
        Platform.setImplicitExit(false);

        entete = new Label("Chargement...");
        entete.getStyleClass().add("entete");

        zoneGrille = new Pane();
        zoneGrille.getStyleClass().add("grille");
        zoneGrille.widthProperty().addListener((o, a, b) -> redessiner());
        zoneGrille.heightProperty().addListener((o, a, b) -> redessiner());

        BorderPane racine = new BorderPane();
        racine.getStyleClass().add("racine");
        racine.setTop(entete);
        racine.setCenter(zoneGrille);

        Scene scene = new Scene(racine, 760, 660);
        var css = ApercuGrilleRobots.class.getResource("/grille.css");
        if (css != null) {
            scene.getStylesheets().add(css.toExternalForm());
        }

        Stage fenetre = new Stage();
        fenetre.setTitle("Apercu - Robots et grille");
        fenetre.setScene(scene);
        fenetre.show();

        Timeline rythme = new Timeline(new KeyFrame(javafx.util.Duration.seconds(0.2), e -> rafraichir()));
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

        // Grille centree sur x = 0 : colonnes de xmin a xmax (ex. nombre_x=5 -> -2..2)
        int xmin = -(colonnes / 2);
        int xmax = xmin + colonnes - 1;

        double marge = 60;
        double demiColonnes = Math.max(1, Math.max(Math.abs(xmin), xmax));
        double taille = Math.max(40, Math.min(
                (largeur / 2 - marge) / demiColonnes,
                (hauteur - 2 * marge) / Math.max(1, lignes)));
        double origineX = largeur / 2;        // x = 0 au centre de la fenetre
        double origineY = hauteur - marge;    // base en bas, axe y vers le haut

        List<Node> elements = new ArrayList<>();

        // Maillage + noeuds a partir des segments exposes par l'API
        dessinerSegments(elements, origineX, origineY, taille, etat.segments);
        dessinerNoeuds(elements, origineX, origineY, taille, xmin, xmax, lignes);

        elements.add(marqueur("base", "BASE", origineX, origineY, taille));

        for (SemaphoreVue s : etat.semaphores) {
            elements.add(marqueur("semaphore", s.nom().isBlank() ? "S" : s.nom(),
                    origineX + s.x() * taille, origineY - s.y() * taille, taille));
        }

        // Robots au repos en (0;0) : alignes SOUS la base pour rester visibles
        int totalBase = 0;
        for (RobotVue r : etat.robots) {
            if (estALaBase(r)) {
                totalBase++;
            }
        }
        int indexBase = 0;
        for (RobotVue r : etat.robots) {
            String classe = r.etat().equalsIgnoreCase("Occupied") ? "robot robot-occupe" : "robot robot-libre";
            if (r.estVolant()) {
                classe += " robot-volant";
            }
            double cx;
            double cy;
            if (estALaBase(r)) {
                double pas = Math.max(30, taille * 0.6);
                cx = origineX + (indexBase - (totalBase - 1) / 2.0) * pas;
                cy = origineY + Math.min(36, taille * 0.5);
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
                                         List<SegmentVue> segments) {
        for (SegmentVue s : segments) {
            sortie.add(segment(
                    ox + s.ax() * taille,
                    oy - s.ay() * taille,
                    ox + s.bx() * taille,
                    oy - s.by() * taille));
        }
    }

    private static Line segment(double x1, double y1, double x2, double y2) {
        Line ligne = new Line(x1, y1, x2, y2);
        ligne.getStyleClass().add("segment");
        return ligne;
    }

    private static void dessinerNoeuds(List<Node> sortie, double ox, double oy, double taille,
                                       int xmin, int xmax, int lignes) {
        for (int y = 1; y <= lignes; y++) {
            for (int x = xmin; x <= xmax; x++) {
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
        if (classes.contains("robot-volant")) {
            Line aileGauche = new Line(0, cote * 0.35, -cote * 0.55, 0);
            aileGauche.getStyleClass().add("aile");
            aileGauche.setTranslateX(-cote * 0.35);
            Line aileDroite = new Line(0, cote * 0.35, cote * 0.55, 0);
            aileDroite.getStyleClass().add("aile");
            aileDroite.setTranslateX(cote * 0.35);
            pastille.getChildren().addAll(aileGauche, aileDroite);
        }
        pastille.getChildren().add(libelle);
        pastille.setPrefSize(cote, cote);
        pastille.setLayoutX(cx - cote / 2);
        pastille.setLayoutY(cy - cote / 2);
        return pastille;
    }

    // === Lecture serveur (Java pur) ===

    private static EtatGrille lireEtatGrille() {
        EtatGrille etat = new EtatGrille();

        String configJson = get("/api/get_config");
        if (configJson.startsWith("ERREUR") || configJson.startsWith("erreur HTTP")) {
            etat.message = configJson;
            return etat;
        }
        int largeur = lireDimension(configJson, "nombre_x", "nbr_x");
        int hauteur = lireDimension(configJson, "nombre_y", "nbr_y");
        if (largeur > 0) {
            etat.largeur = largeur;
        }
        if (hauteur > 0) {
            etat.hauteur = hauteur;
        }

        String segmentsJson = get("/api/list_segment");
        if (!segmentsJson.startsWith("ERREUR") && !segmentsJson.startsWith("erreur HTTP")) {
            for (String objet : objets(segmentsJson)) {
                etat.segments.add(new SegmentVue(
                        (int) nombre(objet, "coord_a_x"),
                        (int) nombre(objet, "coord_a_y"),
                        (int) nombre(objet, "coord_b_x"),
                        (int) nombre(objet, "coord_b_y")));
            }
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
                        nombre(objet, "position_x"),
                        nombre(objet, "position_y"),
                        champ(objet, "state"),
                        nombre(objet, "speed"),
                        champ(objet, "type")));
            }
        }

        etat.message = "Serveur " + SERVEUR + "   |   config " + etat.largeur + " x " + etat.hauteur
                + "   |   " + etat.segments.size() + " segment(s)"
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

    private static int lireDimension(String json, String champPrincipal, String champCompatibilite) {
        int valeur = (int) nombre(json, champPrincipal);
        if (valeur <= 0) {
            valeur = (int) nombre(json, champCompatibilite);
        }
        return valeur;
    }

    private static boolean estALaBase(RobotVue robot) {
        return Math.abs(robot.x()) < 0.001 && Math.abs(robot.y()) < 0.001;
    }

    private static final class EtatGrille {
        int largeur = 10;
        int hauteur = 10;
        String message = "Chargement...";
        List<SegmentVue> segments = new ArrayList<>();
        List<SemaphoreVue> semaphores = new ArrayList<>();
        List<RobotVue> robots = new ArrayList<>();
    }

    private record SegmentVue(int ax, int ay, int bx, int by) {
    }

    private record SemaphoreVue(String nom, int x, int y, String etat) {
    }

    private record RobotVue(String nom, double x, double y, String etat, double vitesse, String type) {
        boolean estVolant() {
            return type != null && type.equalsIgnoreCase("volant");
        }
    }
}
