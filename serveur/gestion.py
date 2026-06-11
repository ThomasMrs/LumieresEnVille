import sqlite3
from database import DB_PATH

ETATS_SEMAPHORE_ROBOT = {"Available", "Occupied", "Disabled"}
ETATS_MISSION = {"Awaiting", "Pending_robot","Pending_semaphore","Done"}
TYPE_SEMAPHORE = {"Ascii","Tracant","Helice"}

def valider_id(table, id_verifier):
    """Verifie qu'un ID existe dans la table donnee. Retourne True/False."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM {table} WHERE id = ?", (id_verifier,))
    resultat = cursor.fetchone()
    conn.close()
    return resultat is not None

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

def valider_type_semaphore(type_semaphore):
    """Verifie que le type de semaphore
    correspond a Led, Tracant ou Helice.
    Retourne True si valide, False sinon."""
    return type_semaphore in TYPE_SEMAPHORE


def valider_coordonnees(coord_x, coord_y):
    """Verifie que les coordonnees sont dans les limites de la grille.
    Retourne True si valide, False sinon."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_x, nombre_y FROM config LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    return 0 <= coord_x < row["nombre_x"] and 0 <= coord_y < row["nombre_y"]