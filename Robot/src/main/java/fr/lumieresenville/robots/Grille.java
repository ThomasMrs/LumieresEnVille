package fr.lumieresenville.robots;

public class Grille {

    private Grille() {
    }
//deplacement du robot vers une destination en utilisant un thread pour simuler le mouvement progressif et respecter la vitesse du robot.
    public static void deplacer(Robot robot, double destinationX, double destinationY) throws Exception {
        Exception[] erreur = new Exception[1];
        Thread threadDeplacement = new Thread(() -> {
            try {
                deplacerDansThread(robot, destinationX, destinationY);
            } catch (Exception e) {
                erreur[0] = e;
            }
        }, "deplacement-" + robot.getNom());

        threadDeplacement.start();
        threadDeplacement.join();

        if (erreur[0] != null) {
            throw erreur[0];
        }
    }

// La méthode deplacerDansThread effectue le déplacement du robot en vérifiant d'abord que la destination est valide,
//  puis en mettant à jour la position du robot progressivement jusqu'à atteindre la destination. Elle utilise des pauses pour simuler la vitesse du robot.
    private static void deplacerDansThread(Robot robot, double destinationX, double destinationY) throws Exception {
        int cibleX = (int) Math.round(destinationX);
        int cibleY = (int) Math.round(destinationY);
        int x = (int) Math.round(robot.getX());
        int y = (int) Math.round(robot.getY());

        verifierPositionDansGrille(cibleX, cibleY);
        System.out.println("Deplacement robot -> depart=(" + x + ", " + y + ")"
                + ", destination=(" + cibleX + ", " + cibleY + ")"
                + ", vitesse=" + robot.getVitesse() + " case(s)/s"
                + ", thread=" + Thread.currentThread().getName());

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
