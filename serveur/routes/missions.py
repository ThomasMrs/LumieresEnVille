import sqlite3
import uuid
from fastapi import APIRouter
from database import DB_PATH

router = APIRouter(prefix="/api", tags=["Mission"])


# --- Accès base de données ---

def ajouter_missions(name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id):
    id_missions = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mission (id, name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (id_missions, name, semaphore_id, robot_id, state, start_date, end_date, team, time, shape_id),
    )
    conn.commit()
    conn.close()


def lire_missions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mission")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats


def supprimer_missions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mission")
    conn.commit()
    conn.close()


def modifier_missions(id_mission, **champs):
    if not champs:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sets = ", ".join(f"{k} = ?" for k in champs)
    vals = list(champs.values()) + [id_mission]
    cursor.execute(f"UPDATE mission SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()


# --- Routes ---

@router.get("/list_missions")
def read_missions():
    return lire_missions()


@router.post("/add_mission")
def add_mission(semaphore_id: str, shape_id: str, team: str,
                name: str | None = None, robot_id: str | None = None,
                start_date: str = "", end_date: str = "", time: str = ""):
    return ajouter_missions(name, semaphore_id, robot_id, "pending", start_date, end_date, team, time, shape_id)


@router.put("/update_mission/{id}")
def update_mission(id: str, name: str | None = None, semaphore_id: str | None = None,
                   robot_id: str | None = None, shape_id: str | None = None,
                   state: str | None = None, start_date: str | None = None,
                   end_date: str | None = None, team: str | None = None,
                   time: str | None = None):
    champs = {}
    if name is not None:
        champs["name"] = name
    if semaphore_id is not None:
        champs["semaphore_id"] = semaphore_id
    if robot_id is not None:
        champs["robot_id"] = robot_id
    if state is not None:
        champs["state"] = state
    if start_date is not None:
        champs["start_date"] = start_date
    if end_date is not None:
        champs["end_date"] = end_date
    if team is not None:
        champs["team"] = team
    if shape_id is not None:
        champs["shape_id"] = shape_id
    if time is not None:
        champs["time"] = time
    return modifier_missions(id, **champs)


@router.delete("/delete_missions")
def delete_missions():
    return supprimer_missions()
