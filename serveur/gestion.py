import sqlite3
from database import DB_PATH

def valider_id(table, id_verifier):
    """Verifie qu'un ID existe dans la table donnee. Retourne True/False."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM {table} WHERE id = ?", (id_verifier,))
    resultat = cursor.fetchone()
    conn.close()
    return resultat is not None

ETATS_SEMAPHORE_ROBOT = {"Available", "Occupied", "Disabled"}
ETATS_MISSION = {"Pending", "In progress", "Done"}

def valider_etat(state, type_entite):
    """Verifie que l'etat est valide.
    type_entite = 'semaphore', 'robot' ou 'mission'.
    Retourne True si valide, False sinon.
    """
    if type_entite in ("semaphore", "robot"):
        return state in ETATS_SEMAPHORE_ROBOT
    elif type_entite == "mission":
        return state in ETATS_MISSION
    return False
