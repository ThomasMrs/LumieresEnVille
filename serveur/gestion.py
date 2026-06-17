from stockage.db import existe_id
from stockage.config import lire_config

ETATS_SEMAPHORE_ROBOT = {"Available", "Occupied", "Disabled"}
ETATS_MISSION = {"Awaiting", "Pending_robot", "Pending_semaphore", "Done"}
TYPE_SEMAPHORE = {"table", "helice", "caractere"}
TYPE_ROBOT = {"Roulant","Volant","Sautant"}


def valider_id(table, id_verifier):
    return existe_id(table, id_verifier)


def valider_etat(state, type_entite):
    if type_entite in ("semaphore", "robot"):
        return state in ETATS_SEMAPHORE_ROBOT
    elif type_entite == "mission":
        return state in ETATS_MISSION
    return False


def valider_type_semaphore(type_semaphore):
    return type_semaphore in TYPE_SEMAPHORE


def valider_type_robot(type_robot):
    return type_robot in TYPE_ROBOT


def valider_coordonnees(coord_x, coord_y):
    # base en (0,0), la grille s'etend au dessus (y >= 1)
    config = lire_config()
    if not config:
        return False
    nombre_x = config["nombre_x"]
    nombre_y = config["nombre_y"]
    x_min = -(nombre_x // 2)

    if coord_x == 0 and coord_y == 0:
        return True
    return x_min <= coord_x < x_min + nombre_x and 1 <= coord_y <= nombre_y


def construire_champs(**champs):
    # ne garde que les champs reellement fournis
    return {cle: valeur for cle, valeur in champs.items() if valeur is not None}
