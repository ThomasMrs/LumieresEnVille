package fr.lumieresenville.robots;          // le package (dossier logique)

// Une mission : aller au semaphore indique et y afficher un symbole.
public class Mission {

    private final String semaphore;          // nom du semaphore a allumer (ne change pas)
    private final String symbole;            // caractere a afficher (ex. "A")
    private final double x;                  // position X (horizontale) du semaphore
    private final double y;                  // position Y (verticale) du semaphore

    // Constructeur : on fournit toutes les infos au moment de la creation
    public Mission(String semaphore, String symbole, double x, double y) {
        this.semaphore = semaphore;          // on enregistre le nom du semaphore
        this.symbole = symbole;              // on enregistre le symbole
        this.x = x;                          // on enregistre la position X
        this.y = y;                          // on enregistre la position Y
    }

    public String getSemaphore() { return semaphore; }   // lire le nom du semaphore
    public String getSymbole()   { return symbole; }     // lire le symbole
    public double getX()         { return x; }           // lire la position X
    public double getY()         { return y; }           // lire la position Y
}
