import sqlite3
from fastapi import APIRouter
from database import DB_PATH

router = APIRouter(prefix="/api", tags=["Config"])


# --- Accès base de données ---

def ajouter_config(grille, nbr_semaphore, nbr_robot):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO config (id, grille, nbr_semaphore, nbr_robot) VALUES (1, ?, ?, ?)",
        (grille, nbr_semaphore, nbr_robot),
    )
    conn.commit()
    conn.close()


def lire_config():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM config WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}


def modifier_config(**champs):
    if not champs:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sets = ", ".join(f"{k} = ?" for k in champs)
    vals = list(champs.values())
    cursor.execute(f"UPDATE config SET {sets} WHERE id = 1", vals)
    conn.commit()
    conn.close()


# --- Routes ---

@router.get("/add_config")
def add_config(grille: str, nbr_semaphore: int, nbr_robot: int):
    return ajouter_config(grille, nbr_semaphore, nbr_robot)


@router.get("/get_config")
def get_config():
    return lire_config()


@router.get("/update_config")
def update_config(grille: str | None = None, nbr_semaphore: int | None = None,
                  nbr_robot: int | None = None):
    champs = {}
    if grille is not None:
        champs["grille"] = grille
    if nbr_semaphore is not None:
        champs["nbr_semaphore"] = nbr_semaphore
    if nbr_robot is not None:
        champs["nbr_robot"] = nbr_robot
    return modifier_config(**champs)
