import sqlite3
import uuid
from fastapi import APIRouter
from database import DB_PATH

router = APIRouter(prefix="/api", tags=["Semaphore"])


# --- Accès base de données ---

def ajouter_semaphore(name, duration, type, coord_x, coord_y):
    id_semaphore = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO semaphore (id, name, duration, type, coord_x, coord_y) VALUES (?, ?, ?, ?, ?, ?)",
        (id_semaphore, name, duration, type, coord_x, coord_y),
    )
    conn.commit()
    conn.close()


def lire_semaphore():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM semaphore")
    resultat = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultat


def supprimer_semaphores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM semaphore")
    conn.commit()
    conn.close()


def modifier_semaphore(id_semaphore, **champs):
    if not champs:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sets = ", ".join(f"{k} = ?" for k in champs)
    vals = list(champs.values()) + [id_semaphore]
    cursor.execute(f"UPDATE semaphore SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()


# --- Routes ---

@router.get("/list_semaphore")
def read_semaphore():
    return lire_semaphore()


@router.get("/semaphore/{id}")
def read_one_semaphore(id: str):
    for s in lire_semaphore():
        if s["id"] == id:
            return s
    return {}


@router.post("/add_semaphore")
def add_semaphore(name: str, duration: int, type: str, coord_x: str = "", coord_y: str = ""):
    return ajouter_semaphore(name, duration, type, coord_x, coord_y)


@router.put("/update_semaphore/{id}")
def update_semaphore(id: str, name: str | None = None, state: str | None = None,
                     duration: int | None = None, type: str | None = None,
                     coord_x: str | None = None, coord_y: str | None = None):
    champs = {}
    if name is not None:
        champs["name"] = name
    if state is not None:
        champs["state"] = state
    if duration is not None:
        champs["duration"] = duration
    if type is not None:
        champs["type"] = type
    if coord_x is not None:
        champs["coord_x"] = coord_x
    if coord_y is not None:
        champs["coord_y"] = coord_y
    return modifier_semaphore(id, **champs)


@router.delete("/delete_semaphores")
def delete_semaphores():
    return supprimer_semaphores()
