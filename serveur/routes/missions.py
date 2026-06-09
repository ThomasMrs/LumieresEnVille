import sqlite3
import uuid
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Mission"])


# --- Accès base de données ---

def ajouter_missions(name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id):
    id_missions = str(uuid.uuid4())
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mission (id, name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (id_missions, name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id),
    )
    conn.commit()
    conn.close()


def lire_missions():
    conn = sqlite3.connect("lumieres.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mission")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats


def supprimer_missions():
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mission")
    conn.commit()
    conn.close()


def modifier_missions(id_mission, name, semaphore_id, robot_id, state, start_date, end_date, team):
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE mission SET name = ?, semaphore_id = ?, robot_id = ?, state = ?, "
        "start_date = ?, end_date = ?, team = ? WHERE id = ?",
        (name, semaphore_id, robot_id, state, start_date, end_date, team, id_mission),
    )
    conn.commit()
    conn.close()

# --- Routes ---

@router.get("/list_missions")
def read_missions():
    return lire_missions()


@router.post("/add_mission")
def add_mission(name: str, semaphore_id: str, team: str, time: int, shape_id: str, start_date: str | None = None,
                state: str = "pending", end_date: str | None = None, robot_id: str | None = None):
    return ajouter_missions(name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id)


@router.put("/update_mission/{id}")
def update_mission(id: str, name: str, semaphore_id: str, robot_id: str, state: str,
                   start_date: str, end_date: str, team: str):
    return modifier_missions(id, name, semaphore_id, robot_id, state, start_date, end_date, team)


@router.delete("/delete_missions")
def delete_missions():
    return supprimer_missions()