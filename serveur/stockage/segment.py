from uuid import uuid4
from stockage.db import get_connection


def ajouter_segment(coord_a_x, coord_a_y, coord_b_x, coord_b_y):
    id_segment = str(uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO segment (id, coord_a_x, coord_a_y, coord_b_x, coord_b_y) "
        "VALUES (?, ?, ?, ?, ?)",
        (id_segment, coord_a_x, coord_a_y, coord_b_x, coord_b_y),
    )
    conn.commit()
    conn.close()
    return {"id": id_segment, "status": "ok"}


def lire_segment():
    conn = get_connection()
    lignes = conn.execute(
        "SELECT * FROM segment ORDER BY coord_a_y, coord_a_x"
    ).fetchall()
    conn.close()
    return [dict(ligne) for ligne in lignes]


def supprimer_segments():
    conn = get_connection()
    conn.execute("DELETE FROM segment")
    conn.commit()
    conn.close()


def modifier_segment(id_segment, **champs):
    if not champs:
        return
    conn = get_connection()
    sets = ", ".join(f"{cle} = ?" for cle in champs)
    valeurs = list(champs.values()) + [id_segment]
    conn.execute(f"UPDATE segment SET {sets} WHERE id = ?", valeurs)
    conn.commit()
    conn.close()


def remplacer_segments(segments):
    """Supprime tous les segments puis insere la liste fournie.

    segments : liste de tuples (id, coord_a_x, coord_a_y, coord_b_x, coord_b_y).
    """
    conn = get_connection()
    conn.execute("DELETE FROM segment")
    conn.executemany(
        "INSERT INTO segment (id, coord_a_x, coord_a_y, coord_b_x, coord_b_y) "
        "VALUES (?, ?, ?, ?, ?)",
        segments,
    )
    conn.commit()
    conn.close()
