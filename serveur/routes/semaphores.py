import sqlite3
from uuid import uuid4
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from database import DB_PATH
from gestion import valider_id, valider_etat, valider_type_semaphore, valider_coordonnees

router = APIRouter(prefix="/api", tags=["Semaphore"])


def ajouter_semaphore(name, duration, type, coord_x, coord_y):
    id_semaphore = str(uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO semaphore (id, name, duration, type, coord_x, coord_y) VALUES (?, ?, ?, ?, ?, ?)",
        (id_semaphore, name, duration, type, coord_x, coord_y),
    )
    conn.commit()
    conn.close()
    return {"id": id_semaphore, "status": "ok"}


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

# =======================
# Route
# =======================

@router.get("/list_semaphore")
def read_semaphore():
    return lire_semaphore()


@router.get("/semaphore/{id}")
def read_one_semaphore(id: str):
    if not valider_id("semaphore", id):
        return HTMLResponse(status_code=404, content="Semaphore introuvable")
    for s in lire_semaphore():
        if s["id"] == id:
            return s


@router.post("/add_semaphore")
def add_semaphore(name: str, duration: int, type: str, coord_x: int, coord_y: int):
    if not valider_type_semaphore(type):
        return HTMLResponse(status_code=400, content="400 - Type invalide (Ascii | Helice | Tracant)")
    if not valider_coordonnees(coord_x, coord_y):
        return HTMLResponse(status_code=400, content="400 - Coordonnees hors limites de la grille")
    return ajouter_semaphore(name, duration, type, coord_x, coord_y)


@router.put("/update_semaphore/{id}")
def update_semaphore(id: str, name: str | None = None, state: str | None = None,
                     duration: int | None = None, type: str | None = None,
                     coord_x: int | None = None, coord_y: int | None = None):
    if not valider_id("semaphore", id):
        return HTMLResponse(status_code=404, content="Semaphore introuvable")
    if state is not None and not valider_etat(state, "semaphore"):
        return HTMLResponse(status_code=400, content="Etat invalide (Available | Occupied | Disabled)")
    if type is not None and not valider_type_semaphore(type):
        return HTMLResponse(status_code=400, content="400 - Type invalide (Ascii | Helice | Tracant)")
    if coord_x is not None or coord_y is not None:
        check_x = coord_x if coord_x is not None else 0
        check_y = coord_y if coord_y is not None else 0
        if not valider_coordonnees(check_x, check_y):
            return HTMLResponse(status_code=400, content="400 - Coordonnees hors limites de la grille")
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
    modifier_semaphore(id, **champs)
    return {"id": id, "status": "updated"}


@router.delete("/delete_semaphores")
def delete_semaphores():
    supprimer_semaphores()
    return {"status": "deleted"}
