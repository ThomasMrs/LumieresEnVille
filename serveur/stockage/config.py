from uuid import uuid4
from stockage.db import get_connection


def ajouter_config(nombre_x, nombre_y, nombre_semaphore, nombre_robot):
    """Cree la configuration. Il n'y a qu'une seule config a la fois :
    on supprime l'ancienne avant d'inserer la nouvelle."""
    id_config = str(uuid4())
    conn = get_connection()
    conn.execute("DELETE FROM config")
    conn.execute(
        "INSERT INTO config (id, nombre_x, nombre_y, nombre_semaphore, nombre_robot) "
        "VALUES (?, ?, ?, ?, ?)",
        (id_config, nombre_x, nombre_y, nombre_semaphore, nombre_robot),
    )
    conn.commit()
    conn.close()
    return {"id": id_config, "status": "ok"}


def lire_config():
    conn = get_connection()
    ligne = conn.execute("SELECT * FROM config LIMIT 1").fetchone()
    conn.close()
    return dict(ligne) if ligne else {}


def modifier_config(id_config, **champs):
    if not champs:
        return
    conn = get_connection()
    sets = ", ".join(f"{cle} = ?" for cle in champs)
    valeurs = list(champs.values()) + [id_config]
    conn.execute(f"UPDATE config SET {sets} WHERE id = ?", valeurs)
    conn.commit()
    conn.close()


def definir_grille(config_id, grille_id, grille_name):
    """Associe une grille (id + nom) a la configuration existante."""
    conn = get_connection()
    conn.execute(
        "UPDATE config SET grille_id = ?, grille_name = ? WHERE id = ?",
        (grille_id, grille_name, config_id),
    )
    conn.commit()
    conn.close()
