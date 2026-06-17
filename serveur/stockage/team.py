from uuid import uuid4
from stockage.db import get_connection


def ajouter_equipe(name, ip, allowed):
    id_equipe = str(uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO team (id, name, ip, allowed) VALUES (?, ?, ?, ?)",
        (id_equipe, name, ip, allowed),
    )
    conn.commit()
    conn.close()
    return {"id": id_equipe, "status": "ok"}


def lire_equipe():
    conn = get_connection()
    lignes = conn.execute("SELECT * FROM team").fetchall()
    conn.close()
    return [dict(ligne) for ligne in lignes]


def auth_equipe():
    """Renvoie uniquement les equipes autorisees (allowed = 1)."""
    conn = get_connection()
    lignes = conn.execute("SELECT * FROM team WHERE allowed = 1").fetchall()
    conn.close()
    return [dict(ligne) for ligne in lignes]


def supprimer_equipes():
    conn = get_connection()
    conn.execute("DELETE FROM team")
    conn.commit()
    conn.close()


def modifier_equipes(id_equipe, **champs):
    if not champs:
        return
    conn = get_connection()
    sets = ", ".join(f"{cle} = ?" for cle in champs)
    valeurs = list(champs.values()) + [id_equipe]
    conn.execute(f"UPDATE team SET {sets} WHERE id = ?", valeurs)
    conn.commit()
    conn.close()
