package fr.lumieresenville.robots;          // le package (dossier logique)

// Une mission : aller au semaphore indique pour le reveiller (l'allumer).
// (Le robot ne transmet pas le symbole : c'est le semaphore qui le lira sur le serveur.)
public class Mission {

    private final String semaphore;          // nom du semaphore a allumer (ne change pas)
    private final double x;                  // position X (horizontale) du semaphore
    private final double y;                  // position Y (verticale) du semaphore

    // Constructeur : on fournit toutes les infos au moment de la creation
    public Mission(String semaphore, double x, double y) {
        this.semaphore = semaphore;          // on enregistre le nom du semaphore
        this.x = x;                          // on enregistre la position X
        this.y = y;                          // on enregistre la position Y
    }

    public String getSemaphore() { return semaphore; }   // lire le nom du semaphore 
    public double getX()         { return x; }           // lire la position X
    public double getY()         { return y; }           // lire la position Y
}
