from uuid import uuid4
from stockage.db import get_connection


def ajouter_semaphore(name, duration, type, coord_x, coord_y):
    id_semaphore = str(uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO semaphore (id, name, duration, type, coord_x, coord_y) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (id_semaphore, name, duration, type, coord_x, coord_y),
    )
    conn.commit()
    conn.close()
    return {"id": id_semaphore, "status": "ok"}


def lire_semaphore():
    conn = get_connection()
    lignes = conn.execute("SELECT * FROM semaphore").fetchall()
    conn.close()
    return [dict(ligne) for ligne in lignes]


def supprimer_semaphores():
    conn = get_connection()
    conn.execute("DELETE FROM semaphore")
    conn.commit()
    conn.close()


def modifier_semaphore(id_semaphore, **champs):
    if not champs:
        return
    conn = get_connection()
    sets = ", ".join(f"{cle} = ?" for cle in champs)
    valeurs = list(champs.values()) + [id_semaphore]
    conn.execute(f"UPDATE semaphore SET {sets} WHERE id = ?", valeurs)
    conn.commit()
    conn.close()
