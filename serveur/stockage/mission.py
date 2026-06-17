from uuid import uuid4
from stockage.db import get_connection


def ajouter_missions(name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id):
    id_missions = str(uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO mission "
        "(id, name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (id_missions, name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id),
    )
    conn.commit()
    conn.close()
    return id_missions


def lire_missions():
    conn = get_connection()
    lignes = conn.execute("SELECT * FROM mission").fetchall()
    conn.close()
    return [dict(ligne) for ligne in lignes]


def supprimer_missions():
    conn = get_connection()
    conn.execute("DELETE FROM mission")
    conn.commit()
    conn.close()


def modifier_missions(id_mission, **champs):
    if not champs:
        return
    conn = get_connection()
    sets = ", ".join(f"{cle} = ?" for cle in champs)
    valeurs = list(champs.values()) + [id_mission]
    conn.execute(f"UPDATE mission SET {sets} WHERE id = ?", valeurs)
    conn.commit()
    conn.close()
