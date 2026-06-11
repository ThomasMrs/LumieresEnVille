package fr.lumieresenville.robots;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GraphicsEnvironment;
import java.awt.RenderingHints;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import javax.swing.Timer;

public class ApercuGrilleRobots {

    private static final String SERVEUR = "http://192.168.1.14:8000";
    private static final HttpClient HTTP = HttpClient.newHttpClient();

    public static void main(String[] args) {
        lancer();
    }

    public static void lancer() {
        if (GraphicsEnvironment.isHeadless()) {
            System.out.println("Apercu graphique indisponible : environnement sans interface graphique.");
            return;
        }

        SwingUtilities.invokeLater(() -> {
            GrillePanel panel = new GrillePanel();
            JFrame fenetre = new JFrame("Apercu temporaire - Robots et grille");
            fenetre.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            fenetre.setContentPane(panel);
            fenetre.pack();
            fenetre.setLocationRelativeTo(null);
            fenetre.setVisible(true);

            AtomicBoolean chargementEnCours = new AtomicBoolean(false);
            Timer timer = new Timer(500, e -> {
                if (!chargementEnCours.compareAndSet(false, true)) {
                    return;
                }
                Thread thread = new Thread(() -> {
                    try {
                        EtatGrille etat = lireEtatGrille();
                        SwingUtilities.invokeLater(() -> panel.setEtat(etat));
                    } finally {
                        chargementEnCours.set(false);
                    }
                }, "apercu-grille-refresh");
                thread.setDaemon(true);
                thread.start();
            });
            timer.setInitialDelay(0);
            timer.start();
        });
    }

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

        etat.message = "Serveur: " + SERVEUR + " | "
                + etat.largeur + "x" + etat.hauteur + " | "
                + etat.semaphores.size() + " semaphore(s) | "
                + etat.robots.size() + " robot(s) | "
                + LocalTime.now().withNano(0);
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

    private static final class GrillePanel extends JPanel {
        private static final int MARGE = 48;
        private static final int INFO_HAUTEUR = 80;
        private EtatGrille etat = new EtatGrille();

        GrillePanel() {
            setPreferredSize(new Dimension(760, 640));
            setBackground(new Color(245, 247, 250));
            setFont(new Font("Arial", Font.PLAIN, 13));
        }

        void setEtat(EtatGrille etat) {
            this.etat = etat;
            repaint();
        }

        @Override
        protected void paintComponent(Graphics graphics) {
            super.paintComponent(graphics);
            Graphics2D g = (Graphics2D) graphics.create();
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            dessinerEntete(g);

            int largeurDisponible = getWidth() - (MARGE * 2);
            int hauteurDisponible = getHeight() - (MARGE * 2) - INFO_HAUTEUR;
            int taille = Math.max(20, Math.min(largeurDisponible / etat.largeur, hauteurDisponible / etat.hauteur));
            int origineX = (getWidth() - taille * etat.largeur) / 2;
            int origineY = MARGE + INFO_HAUTEUR / 2;

            dessinerGrille(g, origineX, origineY, taille);
            dessinerBase(g, origineX, origineY, taille);
            dessinerSemaphores(g, origineX, origineY, taille);
            dessinerRobots(g, origineX, origineY, taille);
            dessinerLegende(g);

            g.dispose();
        }

        private void dessinerEntete(Graphics2D g) {
            g.setColor(new Color(31, 41, 55));
            g.setFont(getFont().deriveFont(Font.BOLD, 18f));
            g.drawString("Apercu temporaire de la grille", MARGE, 32);
            g.setFont(getFont());
            g.setColor(new Color(75, 85, 99));
            g.drawString(etat.message, MARGE, 54);
        }

        private void dessinerGrille(Graphics2D g, int ox, int oy, int taille) {
            g.setStroke(new BasicStroke(1f));
            for (int y = 0; y < etat.hauteur; y++) {
                for (int x = 0; x < etat.largeur; x++) {
                    int px = ox + x * taille;
                    int py = oy + y * taille;
                    g.setColor(Color.WHITE);
                    g.fillRect(px, py, taille, taille);
                    g.setColor(new Color(203, 213, 225));
                    g.drawRect(px, py, taille, taille);
                    g.setColor(new Color(148, 163, 184));
                    g.setFont(getFont().deriveFont(10f));
                    g.drawString(x + "," + y, px + 4, py + 13);
                }
            }
        }

        private void dessinerBase(Graphics2D g, int ox, int oy, int taille) {
            int px = ox;
            int py = oy;
            g.setColor(new Color(219, 234, 254));
            g.fillRect(px + 2, py + 2, taille - 3, taille - 3);
            g.setColor(new Color(37, 99, 235));
            g.setStroke(new BasicStroke(2f));
            g.drawRect(px + 3, py + 3, taille - 6, taille - 6);
            texteCentre(g, "BASE", px, py, taille, new Color(30, 64, 175), 11f);
        }

        private void dessinerSemaphores(Graphics2D g, int ox, int oy, int taille) {
            for (SemaphoreVue semaphore : etat.semaphores) {
                int px = ox + semaphore.x() * taille;
                int py = oy + semaphore.y() * taille;
                int marge = Math.max(5, taille / 7);
                g.setColor(new Color(187, 247, 208));
                g.fillRoundRect(px + marge, py + marge, taille - 2 * marge, taille - 2 * marge, 10, 10);
                g.setColor(new Color(22, 101, 52));
                g.setStroke(new BasicStroke(2f));
                g.drawRoundRect(px + marge, py + marge, taille - 2 * marge, taille - 2 * marge, 10, 10);
                texteCentre(g, "S", px, py - taille / 10, taille, new Color(20, 83, 45), 18f);
                texteCentre(g, semaphore.nom(), px, py + taille / 5, taille, new Color(20, 83, 45), 10f);
            }
        }

        private void dessinerRobots(Graphics2D g, int ox, int oy, int taille) {
            for (RobotVue robot : etat.robots) {
                int px = ox + robot.x() * taille;
                int py = oy + robot.y() * taille;
                int diametre = Math.max(18, taille / 2);
                int rx = px + (taille - diametre) / 2;
                int ry = py + (taille - diametre) / 2;

                g.setColor(robot.etat().equalsIgnoreCase("Occupied")
                        ? new Color(251, 146, 60)
                        : new Color(56, 189, 248));
                g.fillOval(rx, ry, diametre, diametre);
                g.setColor(new Color(15, 23, 42));
                g.setStroke(new BasicStroke(2f));
                g.drawOval(rx, ry, diametre, diametre);
                texteCentre(g, "R", px, py - 1, taille, new Color(15, 23, 42), 16f);
                texteCentre(g, robot.nom(), px, py + taille / 3, taille, new Color(15, 23, 42), 10f);
            }
        }

        private void dessinerLegende(Graphics2D g) {
            int y = getHeight() - 28;
            g.setFont(getFont());
            g.setColor(new Color(37, 99, 235));
            g.drawString("BASE: depart (0,0)", MARGE, y);
            g.setColor(new Color(22, 101, 52));
            g.drawString("S: semaphore", MARGE + 160, y);
            g.setColor(new Color(234, 88, 12));
            g.drawString("R orange: robot occupe", MARGE + 280, y);
            g.setColor(new Color(2, 132, 199));
            g.drawString("R bleu: robot disponible", MARGE + 450, y);
        }

        private void texteCentre(Graphics2D g, String texte, int x, int y, int taille, Color couleur, float taillePolice) {
            if (texte == null || texte.isBlank()) {
                return;
            }
            String affichage = texte.length() > 12 ? texte.substring(0, 12) : texte;
            g.setFont(getFont().deriveFont(Font.BOLD, taillePolice));
            FontMetrics fm = g.getFontMetrics();
            int tx = x + (taille - fm.stringWidth(affichage)) / 2;
            int ty = y + (taille + fm.getAscent() - fm.getDescent()) / 2;
            g.setColor(couleur);
            g.drawString(affichage, tx, ty);
        }
    }
}
