package fr.lumieresenville.robots;

/** Les états possibles d'un robot. */
public enum EtatRobot {
    DISPONIBLE,   // à la base, prêt à recevoir une mission
    EN_MISSION,   // en route vers un sémaphore
    RETOUR_BASE   // revient à sa base
}
