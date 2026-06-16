from stockage.db import existe_id
from stockage.config import lire_config

ETATS_SEMAPHORE_ROBOT = {"Available", "Occupied", "Disabled"}
ETATS_MISSION = {"Awaiting", "Pending_robot", "Pending_semaphore", "Done"}
TYPE_SEMAPHORE = {"Ascii", "Tracant", "Helice"}


def valider_id(table, id_verifier):
    """Verifie qu'un ID existe dans la table donnee. Retourne True/False.

    Le SQL est delegue a la couche stockage (stockage.db.existe_id).
    """
    return existe_id(table, id_verifier)


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
    """Verifie que le type de semaphore correspond a Ascii, Tracant ou Helice.
    Retourne True si valide, False sinon."""
    return type_semaphore in TYPE_SEMAPHORE


def valider_coordonnees(coord_x, coord_y):
    """Verifie que les coordonnees sont dans les limites de la grille.
    Retourne True si valide, False sinon """
    config = lire_config()
    if not config:
        return False
    nombre_x = config["nombre_x"]
    nombre_y = config["nombre_y"]
    # Grille centree horizontalement sur x = 0 (colonnes negatives possibles).
    x_min = -(nombre_x // 2)
    # La base est en (0, 0). La vraie grille est au-dessus : y de 1 a nombre_y.
    if coord_x == 0 and coord_y == 0:
        return True
    return x_min <= coord_x < x_min + nombre_x and 1 <= coord_y <= nombre_y
