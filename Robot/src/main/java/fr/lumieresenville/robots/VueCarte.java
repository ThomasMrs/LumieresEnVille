package fr.lumieresenville.robots;

import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.shape.Rectangle;
import javafx.scene.text.Text;

import java.util.List;

/**
 * Affichage graphique simple : la base, les routes, les sémaphores et les robots,
 * dessinés sous forme de formes (cercles, lignes, rectangle) sur un plan.
 */
public class VueCarte {

    private static final double RAYON_SEMAPHORE = 18;
    private static final double RAYON_ROBOT = 10;

    /**
     * Construit le plan : routes, base, sémaphores puis robots (dans cet ordre,
     * pour que les robots soient dessinés par-dessus le reste).
     */
    public static Pane construire(double baseX, double baseY,
                                  List<Semaphore> semaphores, List<Robot> robots) {
        Pane plan = new Pane();
        plan.setStyle("-fx-background-color: #eef2f5;");

        // 1) Les routes : une ligne de la base vers chaque sémaphore
        for (Semaphore s : semaphores) {
            Line route = new Line(baseX, baseY, s.getX(), s.getY());
            route.setStroke(Color.LIGHTGRAY);
            route.setStrokeWidth(4);
            plan.getChildren().add(route);
        }

        // 2) La base (un carré gris)
        Rectangle base = new Rectangle(baseX - 25, baseY - 25, 50, 50);
        base.setFill(Color.DIMGRAY);
        plan.getChildren().addAll(base, texte("Base", baseX - 14, baseY + 42));

        // 3) Les sémaphores (cercles bleus + nom)
        for (Semaphore s : semaphores) {
            Circle point = new Circle(s.getX(), s.getY(), RAYON_SEMAPHORE);
            point.setFill(Color.STEELBLUE);
            point.setStroke(Color.DARKSLATEGRAY);
            plan.getChildren().addAll(point, texte(s.getNom(), s.getX() - 30, s.getY() - 24));
        }

        // 4) Les robots (cercles colorés selon l'état + nom)
        for (Robot r : robots) {
            Circle point = new Circle(r.getX(), r.getY(), RAYON_ROBOT);
            point.setFill(couleurEtat(r.getEtat()));
            point.setStroke(Color.BLACK);
            plan.getChildren().addAll(point, texte(r.getNom(), r.getX() + 12, r.getY() + 4));
        }

        return plan;
    }

    /** Couleur d'un robot selon son état. */
    private static Color couleurEtat(EtatRobot etat) {
        return switch (etat) {
            case DISPONIBLE  -> Color.LIMEGREEN;
            case EN_MISSION  -> Color.ORANGE;
            case RETOUR_BASE -> Color.CORNFLOWERBLUE;
        };
    }

    /** Petit utilitaire pour créer un texte positionné. */
    private static Text texte(String contenu, double x, double y) {
        return new Text(x, y, contenu);
    }
}
