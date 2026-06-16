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

    private static final int PAS_ANIMATION_PAR_CASE = 20;

    private Grille() {
    }

    // Deplace le robot
    public static void deplacer(Robot robot, double destinationX, double destinationY) throws Exception {
        EtatGrille etatGrille = lireEtatGrille(!robot.estVolant());
        Point depart = new Point((int) Math.round(robot.getX()), (int) Math.round(robot.getY()));
        Point arrivee = new Point((int) Math.round(destinationX), (int) Math.round(destinationY));

        verifierPositionDansGrille(depart, etatGrille);
        verifierPositionDansGrille(arrivee, etatGrille);
        if (robot.estVolant()) {
            deplacerVolant(robot, depart, arrivee);
            return;
        }

        List<Point> chemin = calculerChemin(depart, arrivee, etatGrille.segments());
        System.out.println("[" + robot.getNom() + "] deplacement -> depart=" + depart
                + ", destination=" + arrivee
                + ", vitesse=" + robot.getVitesse() + " case(s)/s"
                + ", segments=" + etatGrille.segments().size()
                + ", pas=" + Math.max(0, chemin.size() - 1));

        for (int i = 1; i < chemin.size(); i++) {
            Point point = chemin.get(i);
            glisserVers(robot, point.x(), point.y());
        }
    }

    private static void deplacerVolant(Robot robot, Point depart, Point arrivee) throws Exception {
        double distance = Math.hypot(arrivee.x() - depart.x(), arrivee.y() - depart.y());
        int pas = Math.max(1, (int) Math.ceil(distance * PAS_ANIMATION_PAR_CASE));
        System.out.println("[" + robot.getNom() + "] deplacement volant -> depart=" + depart
                + ", destination=" + arrivee
                + ", vitesse=" + robot.getVitesse() + " case(s)/s"
                + ", pas=" + pas);
        glisserVers(robot, arrivee.x(), arrivee.y());
    }

    // Glisse entre deux points en envoyant plusieurs positions intermediaires au serveur.
    private static void glisserVers(Robot robot, double cibleX, double cibleY) throws Exception {
        double departX = robot.getX();
        double departY = robot.getY();
        double deltaX = cibleX - departX;
        double deltaY = cibleY - departY;
        double distance = Math.hypot(deltaX, deltaY);
        if (distance == 0) {
            return;
        }

        int pas = Math.max(1, (int) Math.ceil(distance * PAS_ANIMATION_PAR_CASE));
        long delaiMs = delaiParPas(robot, distance, pas);
        System.out.println("[" + robot.getNom() + "] glisse -> (" + coord(departX) + ";" + coord(departY)
                + ") vers (" + coord(cibleX) + ";" + coord(cibleY) + ") en " + pas + " position(s)");

        for (int i = 1; i <= pas; i++) {
            if (Thread.currentThread().isInterrupted()) {
                throw new InterruptedException("deplacement interrompu pour " + robot.getNom());
            }

            double ratio = i / (double) pas;
            robot.setPosition(departX + deltaX * ratio, departY + deltaY * ratio);
            AppRobots.modifierRobot(robot);

            if (i < pas) {
                Thread.sleep(delaiMs);
            }
        }
    }

    private static EtatGrille lireEtatGrille(boolean chargerSegments) throws Exception {
        String configJson = AppRobots.get("/api/get_config");
        if (configJson.startsWith("ERREUR") || configJson.startsWith("erreur HTTP") || configJson.equals("OK")) {
            throw new Exception("configuration introuvable : " + configJson);
        }

        int largeur = lireDimension(configJson, "nombre_x", "nbr_x");
        int hauteur = lireDimension(configJson, "nombre_y", "nbr_y");
        if (largeur <= 0 || hauteur <= 0) {
            throw new Exception("configuration invalide : dimensions inconnues");
        }

        List<Segment> segments = new ArrayList<>();
        if (chargerSegments) {
            String segmentsJson = AppRobots.get("/api/list_segment");
            if (segmentsJson.startsWith("ERREUR") || segmentsJson.startsWith("erreur HTTP")) {
                throw new Exception("segments introuvables : " + segmentsJson);
            }

            for (String objet : objets(segmentsJson)) {
                segments.add(new Segment(
                        (int) nombre(objet, "coord_a_x"),
                        (int) nombre(objet, "coord_a_y"),
                        (int) nombre(objet, "coord_b_x"),
                        (int) nombre(objet, "coord_b_y")));
            }
            if (segments.isEmpty()) {
                throw new Exception("aucun segment disponible pour deplacer le robot");
            }
        }

        return new EtatGrille(largeur, hauteur, segments);
    }

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

    private static long delaiParPas(Robot robot, double distance, int pas) {
        double vitesse = robot.getVitesse();
        if (vitesse <= 0) {
            vitesse = 1.0;
        }
        long delaiTotalMs = Math.max(1, Math.round(distance * 1000.0 / vitesse));
        return Math.max(1, Math.round(delaiTotalMs / (double) pas));
    }

    private static String coord(double valeur) {
        return String.format(java.util.Locale.US, "%.2f", valeur);
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

    private record EtatGrille(int largeur, int hauteur, List<Segment> segments) {
    }

    private record Segment(int ax, int ay, int bx, int by) {
    }

    private record Point(int x, int y) {
        @Override
        public String toString() {
            return "(" + x + ";" + y + ")";
        }
    }
}
