import sqlite3
import uuid
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Team"])

# --- Accès base de données ---

def ajouter_equipe(name, ip, allowed):
    id_equipe = str(uuid.uuid4())
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO team (id, name, ip, allowed) VALUES (?, ?, ?, ?)",
        (id_equipe, name, ip, allowed),
    )
    conn.commit()
    conn.close()


def lire_equipe():
    conn = sqlite3.connect("lumieres.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM team")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats


def auth_equipe():
    """Retourne uniquement les équipes autorisées à se connecter."""
    conn = sqlite3.connect("lumieres.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM team WHERE allowed = 1")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats


def supprimer_equipes():
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM team")
    conn.commit()
    conn.close()


def modifier_equipes(id_equipe, name, ip, allowed):
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE team SET name = ?, ip = ?, allowed = ? WHERE id = ?",
        (name, ip, allowed, id_equipe),
    )
    conn.commit()
    conn.close()


# --- Routes ---

@router.get("/list_teams")
def read_teams():
    return lire_equipe()


@router.post("/add_team")
def add_team(name: str, ip: str, allowed: bool):
    return ajouter_equipe(name, ip, allowed)


@router.put("/update_team/{id}")
def update_team(id: str, name: str, ip: str, allowed: bool):
    return modifier_equipes(id, name, ip, allowed)


@router.delete("/delete_teams")
def delete_teams():
    return supprimer_equipes()


# Liste des objets autorisés à se connecter (cahier des charges)
@router.get("/list_teams_allowed")
def read_teams_allowed():
    return auth_equipe()