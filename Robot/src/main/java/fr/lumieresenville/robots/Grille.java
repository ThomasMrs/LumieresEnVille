package fr.lumieresenville.robots;

public class Grille {

    private Grille() {
    }

    // Deplace le robot
    public static void deplacer(Robot robot, double destinationX, double destinationY) throws Exception {
        int cibleX = (int) Math.round(destinationX);
        int cibleY = (int) Math.round(destinationY);
        int x = (int) Math.round(robot.getX());
        int y = (int) Math.round(robot.getY());

        verifierPositionDansGrille(cibleX, cibleY);

        // Il n'y a pas de routes en y = 0 (seulement la base) : pour quitter la base (0;0)
        // on monte d'abord sur le maillage en (0;1). Au retour, le deplacement en x ramene
        // d'abord sur la colonne 0, donc la descente se fait naturellement par (0;1) -> (0;0).
        if (x == 0 && y == 0 && !(cibleX == 0 && cibleY == 0)) {
            y = 1;
            avancerVers(robot, x, y);
        }

        while (x != cibleX || y != cibleY) {
            if (x < cibleX) {
                x++;
            } else if (x > cibleX) {
                x--;
            } else if (y < cibleY) {
                y++;
            } else {
                y--;
            }
            avancerVers(robot, x, y);
        }
    }

    // Un pas elementaire : met a jour la position, l'envoie au serveur, puis respecte la vitesse.
    private static void avancerVers(Robot robot, int x, int y) throws Exception {
        if (Thread.currentThread().isInterrupted()) {
            throw new InterruptedException("deplacement interrompu pour " + robot.getNom());
        }
        robot.setPosition(x, y);
        System.out.println("[" + robot.getNom() + "] avance -> (" + x + ", " + y + ")");
        AppRobots.modifierRobot(robot);
        attendreSelonVitesse(robot);
    }

    private static void verifierPositionDansGrille(int x, int y) throws Exception {
        String grilleJson = AppRobots.get("/api/get_grille");
        if (grilleJson.startsWith("ERREUR") || grilleJson.startsWith("erreur HTTP")) {
            System.out.println("Grille non verifiee : " + grilleJson);
            return;
        }

        int largeur = (int) AppRobots.nombre(grilleJson, "nombre_x");
        int hauteur = (int) AppRobots.nombre(grilleJson, "nombre_y");
        if (largeur <= 0 || hauteur <= 0) {
            System.out.println("Grille non verifiee : dimensions inconnues.");
            return;
        }
        // Grille centree sur x = 0 : x va de xmin a xmax ; y de 0 a hauteur-1
        int xmin = -(largeur / 2);
        int xmax = xmin + largeur - 1;
        if (x < xmin || x > xmax || y < 0 || y >= hauteur) {
            System.out.println("Attention : destination hors grille (" + x + ", " + y
                    + ") pour une grille x[" + xmin + ".." + xmax + "] y[0.." + (hauteur - 1) + "].");
        }
    }

    private static void attendreSelonVitesse(Robot robot) throws InterruptedException {
        double vitesse = robot.getVitesse();
        if (vitesse <= 0) {
            vitesse = 1.0;
        }
        long delaiMs = Math.max(100, Math.round(1000.0 / vitesse));
        Thread.sleep(delaiMs);
    }
}
