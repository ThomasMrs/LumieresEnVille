package fr.lumieresenville.robots;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

// Calcule le chemin d'un robot sur les routes et le fait avancer case par case.
public class Grille {

    // Pause entre deux cases
    private static final long DELAI_PAS_MS = 700;

    private Grille() {
    }

    // Deplace le robot de sa position actuelle jusqu'a (destinationX, destinationY).
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

        // Sinon : plus court chemin en suivant les segments 
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

    // Robot volant trajet direct vers l'arrivee
    private static void deplacerVolant(Robot robot, Point depart, Point arrivee) throws Exception {
        System.out.println("[" + robot.getNom() + "] deplacement volant -> depart=" + depart
                + ", destination=" + arrivee + ", vitesse=" + robot.getVitesse() + " case(s)/s");
        glisserVers(robot, arrivee.x(), arrivee.y());
    }

    private static void glisserVers(Robot robot, double cibleX, double cibleY) throws Exception {
        if (Thread.currentThread().isInterrupted()) {
            throw new InterruptedException("deplacement interrompu pour " + robot.getNom());
        }
        robot.setPosition(cibleX, cibleY);                 
        System.out.println("[" + robot.getNom() + "] -> (" + (int) Math.round(cibleX) + ", " + (int) Math.round(cibleY) + ")");
        AppRobots.modifierRobot(robot);
        Thread.sleep(DELAI_PAS_MS);  
    }

    // lire dimmenssion depuis serveur
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

            // Chaque objet JSON {coord_a_x, coord_a_y, coord_b_x, coord_b_y} devient un Segment.
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

    // Verifie qu'une case est dans la grille : x centre sur 0, y de 1 a hauteur ; (0;0) = base.
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

    // Plus court chemin entre depart et arrivee en suivant les segments
    private static List<Point> calculerChemin(Point depart, Point arrivee, List<Segment> segments) throws Exception {
        if (depart.equals(arrivee)) {
            return List.of(depart);
        }

        ArrayDeque<Point> file = new ArrayDeque<>();       // cases a explorer (FIFO)
        Set<Point> visites = new HashSet<>();              // cases deja vues (evite les boucles)
        Map<Point, Point> precedent = new HashMap<>();     // pour chaque case : d'ou on y est arrive

        file.add(depart);
        visites.add(depart);

        while (!file.isEmpty()) {
            Point courant = file.removeFirst();            // la plus ancienne case -> chemin le plus court
            for (Point voisin : voisins(courant, segments)) {
                if (!visites.add(voisin)) {                // deja visitee -> on saute
                    continue;
                }
                precedent.put(voisin, courant);
                if (voisin.equals(arrivee)) {              // arrivee atteinte
                    return reconstruireChemin(depart, arrivee, precedent);
                }
                file.addLast(voisin);
            }
        }

        throw new Exception("aucun chemin par segments entre " + depart + " et " + arrivee);
    }

    // Renvoie les cases reliees a 'point' par un segment (ses voisins dans le graphe).
    private static List<Point> voisins(Point point, List<Segment> segments) {
        List<Point> voisins = new ArrayList<>();
        for (Segment segment : segments) {
            Point a = new Point(segment.ax(), segment.ay());
            Point b = new Point(segment.bx(), segment.by());
            if (a.equals(point)) {                         // une extremite = point -> l'autre est voisine
                voisins.add(b);
            } else if (b.equals(point)) {
                voisins.add(a);
            }
        }
        return voisins;
    }

    // Remonte la map 'precedent' de l'arrivee au depart, puis remet dans l'ordre depart -> arrivee.
    private static List<Point> reconstruireChemin(Point depart, Point arrivee, Map<Point, Point> precedent) {
        List<Point> chemin = new ArrayList<>();
        Point courant = arrivee;
        chemin.add(courant);
        while (!courant.equals(depart)) {
            courant = precedent.get(courant);
            chemin.add(courant);
        }
        Collections.reverse(chemin);                       // l'ordre etait arrivee -> depart, on l'inverse
        return chemin;
    }


    // Decoupe un tableau JSON en objets {...} en comptant les accolades (mini-parseur maison).
    private static List<String> objets(String json) {
        List<String> liste = new ArrayList<>();
        int profondeur = 0;
        int debut = -1;
        for (int i = 0; i < json.length(); i++) {
            char c = json.charAt(i);
            if (c == '{') {
                if (profondeur == 0) {
                    debut = i;                             // debut d'un objet de premier niveau
                }
                profondeur++;
            } else if (c == '}') {
                profondeur--;
                if (profondeur == 0 && debut >= 0) {
                    liste.add(json.substring(debut, i + 1)); // objet complet
                }
            }
        }
        return liste;
    }

    // Extrait la valeur du champ "nom": valeur (avec ou sans guillemets) ; "" si absent ou null.
    private static String champ(String objet, String nom) {
        int i = objet.indexOf("\"" + nom + "\"");
        if (i < 0) {
            return "";
        }
        i = objet.indexOf(':', i) + 1;                     // on se place apres le ':'
        while (i < objet.length() && objet.charAt(i) == ' ') {
            i++;                                           // on saute les espaces
        }
        if (i >= objet.length()) {
            return "";
        }
        if (objet.charAt(i) == '"') {                      // valeur entre guillemets
            return objet.substring(i + 1, objet.indexOf('"', i + 1));
        }
        int fin = i;                                       // valeur sans guillemets (nombre, bool...)
        while (fin < objet.length() && objet.charAt(fin) != ',' && objet.charAt(fin) != '}') {
            fin++;
        }
        String valeur = objet.substring(i, fin).trim();
        return valeur.equals("null") ? "" : valeur;
    }

    // Comme champ(...) mais convertit la valeur en nombre (double).
    private static double nombre(String objet, String nom) {
        String valeur = champ(objet, nom);
        return valeur.isBlank() ? 0 : Double.parseDouble(valeur);
    }

    // Lit une dimension 
    private static int lireDimension(String json, String champPrincipal, String champCompatibilite) {
        int valeur = (int) nombre(json, champPrincipal);
        if (valeur <= 0) {
            valeur = (int) nombre(json, champCompatibilite);
        }
        return valeur;
    }

    // La grille lue depuis le serveur 
    private record EtatGrille(int largeur, int hauteur, List<Segment> segments) {
    }

    // Une route entre deux points
    private record Segment(int ax, int ay, int bx, int by) {
    }

    // Une case de la grille affichage des positions
    private record Point(int x, int y) {
        @Override
        public String toString() {
            return "(" + x + ";" + y + ")";
        }
    }
}
