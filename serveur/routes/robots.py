import sqlite3
import uuid
from fastapi import APIRouter

from routes.missions import lire_missions

router = APIRouter(prefix="/api", tags=["Robot"])


# --- Accès base de données ---

def ajouter_robots(name, state, speed, position_x, position_y):
    id_robots = str(uuid.uuid4())
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO robot (id, name, state, speed, position_x, position_y) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (id_robots, name, state, speed, position_x, position_y),
    )
    conn.commit()
    conn.close()


def lire_robots():
    conn = sqlite3.connect("lumieres.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM robot")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats


def supprimer_robots():
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM robot")
    conn.commit()
    conn.close()


def modifier_robots(id_robots, name, state, speed, position_x, position_y):
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE robot SET name = ?, state = ?, speed = ?, "
        "position_x = ?, position_y = ? WHERE id = ?",
        (name, state, speed, position_x, position_y, id_robots),
    )
    conn.commit()
    conn.close()


# --- Routes ---

@router.get("/list_robots")
def read_robots():
    return lire_robots()


@router.get("/robot/{id}")
def read_one_robot(id: str):
    for r in lire_robots():
        if r["id"] == id:
            return r
    return {}


@router.get("/robot/{id}/mission")
def read_robot_missions(id: str):
    return [m for m in lire_missions() if m["robot_id"] == id]


@router.post("/add_robot")
def add_robot(name: str, state: str, speed: float, position_x: float, position_y: float):
    return ajouter_robots(name, state, speed, position_x, position_y)


@router.put("/update_robot/{id}")
def update_robot(id: str, name: str, state: str, speed: float, position_x: float, position_y: float):
    return modifier_robots(id, name, state, speed, position_x, position_y)


@router.delete("/delete_robots")
def delete_robots():
    return supprimer_robots()