from uuid import uuid4
from stockage.db import get_connection


def ajouter_robots(**champs):
    id_robots = str(uuid4())
    champs["id"] = id_robots
    conn = get_connection()
    colonnes = ", ".join(champs.keys())
    valeurs_pos = ", ".join("?" * len(champs))
    conn.execute(
        f"INSERT INTO robot ({colonnes}) VALUES ({valeurs_pos})",
        list(champs.values()),
    )
    conn.commit()
    conn.close()
    return id_robots


def lire_robots():
    conn = get_connection()
    lignes = conn.execute("SELECT * FROM robot").fetchall()
    conn.close()
    return [dict(ligne) for ligne in lignes]


def supprimer_robots():
    conn = get_connection()
    conn.execute("DELETE FROM robot")
    conn.commit()
    conn.close()


def modifier_robots(id_robots, **champs):
    if not champs:
        return
    conn = get_connection()
    sets = ", ".join(f"{cle} = ?" for cle in champs)
    valeurs = list(champs.values()) + [id_robots]
    conn.execute(f"UPDATE robot SET {sets} WHERE id = ?", valeurs)
    conn.commit()
    conn.close()
