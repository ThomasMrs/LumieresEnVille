package fr.lumieresenville.robots;

public class Grille {

    private Grille() {
    }

    public static void deplacer(Robot robot, double destinationX, double destinationY) throws Exception {
        int cibleX = (int) Math.round(destinationX);
        int cibleY = (int) Math.round(destinationY);
        int x = (int) Math.round(robot.getX());
        int y = (int) Math.round(robot.getY());

        verifierPositionDansGrille(cibleX, cibleY);
        System.out.println("Deplacement robot -> depart=(" + x + ", " + y + ")"
                + ", destination=(" + cibleX + ", " + cibleY + ")"
                + ", vitesse=" + robot.getVitesse() + " case(s)/s");

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

            robot.setPosition(x, y);
            System.out.println("Robot avance -> (" + x + ", " + y + ")");
            System.out.println("PUT robot      : " + AppRobots.modifierRobot(robot));
            attendreSelonVitesse(robot);
        }
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
        if (x < 0 || y < 0 || x >= largeur || y >= hauteur) {
            System.out.println("Attention : destination hors grille (" + x + ", " + y
                    + ") pour une grille " + largeur + "x" + hauteur + ".");
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
