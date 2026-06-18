package fr.lumieresenville.robots;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Grille {

    //Empecher la creation d'un objet Grille
    private Grille() {
    }

    //Deplacer un robot vers une destination
    public static void deplacer(Robot robot, double destinationX, double destinationY) throws Exception {
        deplacer(robot, destinationX, destinationY, false);
    }

    public static void deplacerRetour(Robot robot, double destinationX, double destinationY) throws Exception {
        deplacer(robot, destinationX, destinationY, true);
    }

    private static void deplacer(Robot robot, double destinationX, double destinationY, boolean autreChemin) throws Exception {
        EtatGrille etatGrille = lireEtatGrille();
        Point depart = new Point((int) Math.round(robot.getX()), (int) Math.round(robot.getY()));
        Point arrivee = new Point((int) Math.round(destinationX), (int) Math.round(destinationY));

        verifierPositionDansGrille(depart, etatGrille);
        verifierPositionDansGrille(arrivee, etatGrille);
//calcule chemin 

    // private static List<Point> reconstruireChemin(Point depart, Point arrivee, Map<Point, Point> precedent) {
    //     List<Point> chemin = new ArrayList<>();
    //     Point courant = arrivee;
    //     chemin.add(courant);
    //     while (!courant.equals(depart)) {
    //         courant = precedent.get(courant);
    //         chemin.add(courant);
    //     }
    //     Collections.reverse(chemin);
    //     return chemin;
    // }

    
        List<Segment> segments = etatGrille.segments();
        if (autreChemin) {
            segments = new ArrayList<>(segments);
            Collections.reverse(segments);
        }


        List<Point> chemin = calculerChemin(depart, arrivee, segments);
        System.out.println("[" + robot.getNom() + "] deplacement -> depart=" + depart
                + ", destination=" + arrivee
                + ", vitesse=" + robot.getVitesse() + " case(s)/s"
                + ", segments=" + segments.size()
                + ", pas=" + Math.max(0, chemin.size() - 1));

        for (int i = 1; i < chemin.size(); i++) {
            Point point = chemin.get(i);
            avancerVers(robot, point.x(), point.y());
        }
    }

    // Faire avancer le robot d'un point
    // Met a jour la position, l'envoie au serveur, puis respecte la vitesse.
    private static void avancerVers(Robot robot, int x, int y) throws Exception {
        if (Thread.currentThread().isInterrupted()) {
            throw new InterruptedException("deplacement interrompu pour " + robot.getNom());
        }
        robot.setPosition(x, y);
        System.out.println("[" + robot.getNom() + "] avance -> (" + x + ", " + y + ")");
        AppRobots.modifierRobot(robot);
        attendreSelonVitesse(robot);
    }

    //Lire la configuration et les segments de la grille
    private static EtatGrille lireEtatGrille() throws Exception {
        String configJson = AppRobots.get("/api/get_config");
        if (configJson.startsWith("ERREUR") || configJson.startsWith("erreur HTTP") || configJson.equals("OK")) {
            throw new Exception("configuration introuvable : " + configJson);
        }

        int largeur = (int) JsonMini.nombre(configJson, "nombre_x");
        int hauteur = (int) JsonMini.nombre(configJson, "nombre_y");
        if (largeur <= 0 || hauteur <= 0) {
            throw new Exception("configuration invalide : dimensions inconnues");
        }

        String segmentsJson = AppRobots.get("/api/list_segment");
        if (segmentsJson.startsWith("ERREUR") || segmentsJson.startsWith("erreur HTTP")) {
            throw new Exception("segments introuvables : " + segmentsJson);
        }

        List<Segment> segments = new ArrayList<>();
        for (String objet : JsonMini.objets(segmentsJson)) {
            segments.add(new Segment(
                    (int) JsonMini.nombre(objet, "coord_a_x"),
                    (int) JsonMini.nombre(objet, "coord_a_y"),
                    (int) JsonMini.nombre(objet, "coord_b_x"),
                    (int) JsonMini.nombre(objet, "coord_b_y")));
        }
        if (segments.isEmpty()) {
            throw new Exception("aucun segment disponible pour deplacer le robot");
        }

        return new EtatGrille(largeur, hauteur, segments);
    }

    // Verifier qu'un point est dans la grille
    private static void verifierPositionDansGrille(Point point, EtatGrille etatGrille) throws Exception {
        if (point.x() == 0 && point.y() == 0) {
            return;
        }

        int xmin = -(etatGrille.largeur() / 2); 
        int xmaxExclus = xmin + etatGrille.largeur();
        if (point.x() < xmin || point.x() >= xmaxExclus || point.y() < 1 || point.y() > etatGrille.hauteur()) {
            throw new Exception("position hors grille " + point
                    + " pour x[" + xmin + ".." + (xmaxExclus - 1) + "] y[1.." + etatGrille.hauteur() + "]"
                    + " ou base (0;0)");
        }
    }

    // Calculer le chemin le plus court entre deux points 
    private static List<Point> calculerChemin(Point depart, Point arrivee, List<Segment> segments) throws Exception {
        if (depart.equals(arrivee)) {
            return List.of(depart);
        }

        ArrayDeque<Point> file = new ArrayDeque<>();
        Set<Point> visites = new HashSet<>();
        Map<Point, Point> precedent = new HashMap<>();

        file.add(depart);
        visites.add(depart);

        while (!file.isEmpty()) {
            Point courant = file.removeFirst();
            for (Point voisin : voisins(courant, segments)) {
                if (!visites.add(voisin)) {
                    continue;
                }
                precedent.put(voisin, courant);
                if (voisin.equals(arrivee)) {
                    return reconstruireChemin(depart, arrivee, precedent);
                }
                file.addLast(voisin);
            }
        }

        throw new Exception("aucun chemin par segments entre " + depart + " et " + arrivee);
    }

    //  Trouver les points voisins accessibles depuis un point
    private static List<Point> voisins(Point point, List<Segment> segments) {
        List<Point> voisins = new ArrayList<>();
        for (Segment segment : segments) {
            Point a = new Point(segment.ax(), segment.ay());
            Point b = new Point(segment.bx(), segment.by());
            if (a.equals(point)) {
                voisins.add(b);
            } else if (b.equals(point)) {
                voisins.add(a);
            }
        }
        return voisins;
    }

    // Reconstruire le chemin apres le calcul 
    private static List<Point> reconstruireChemin(Point depart, Point arrivee, Map<Point, Point> precedent) {
        List<Point> chemin = new ArrayList<>();
        Point courant = arrivee;
        chemin.add(courant);
        while (!courant.equals(depart)) {
            courant = precedent.get(courant);
            chemin.add(courant);
        }
        Collections.reverse(chemin);
        return chemin;
    }

    //  Attendre selon la vitesse du robot 
    private static void attendreSelonVitesse(Robot robot) throws InterruptedException {
        double vitesse = robot.getVitesse();
        if (vitesse <= 0) {
            vitesse = 1.0;
        }
        long delaiMs = Math.max(100, Math.round(1000.0 / vitesse));
        Thread.sleep(delaiMs);
    }

    // === Donnees internes de l'etat de la grille ===
    private record EtatGrille(int largeur, int hauteur, List<Segment> segments) {
    }

    // === Donnees internes d'un segment de grille ===
    private record Segment(int ax, int ay, int bx, int by) {
    }

    // === Donnees internes d'un point de grille ===
    private record Point(int x, int y) {
        // === Afficher un point sous forme lisible ===
        @Override
        public String toString() {
            return "(" + x + ";" + y + ")";
        }
    }
}
