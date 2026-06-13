from uuid import uuid4
from stockage.db import get_connection


def ajouter_shape(name, image):
    id_shape = str(uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO shape (id, name, image) VALUES (?, ?, ?)",
        (id_shape, name, image),
    )
    conn.commit()
    conn.close()
    return {"id": id_shape, "status": "ok"}


def lire_shape():
    conn = get_connection()
    lignes = conn.execute("SELECT * FROM shape").fetchall()
    conn.close()
    return [dict(ligne) for ligne in lignes]


def supprimer_shapes():
    conn = get_connection()
    conn.execute("DELETE FROM shape")
    conn.commit()
    conn.close()


def modifier_shape(id_shape, **champs):
    if not champs:
        return
    conn = get_connection()
    sets = ", ".join(f"{cle} = ?" for cle in champs)
    valeurs = list(champs.values()) + [id_shape]
    conn.execute(f"UPDATE shape SET {sets} WHERE id = ?", valeurs)
    conn.commit()
    conn.close()
