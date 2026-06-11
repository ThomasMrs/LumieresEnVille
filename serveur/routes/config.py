import sqlite3
from uuid import uuid4
from fastapi import APIRouter
from database import DB_PATH

router = APIRouter(prefix="/api", tags=["Config"])


def ajouter_config(nombre_x, nombre_y, nombre_semaphore, nombre_robot):
    id_config = str(uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM config")
    cursor.execute(
        "INSERT INTO config (id, nombre_x, nombre_y, nombre_semaphore, nombre_robot) VALUES (?, ?, ?, ?, ?)",
        (id_config, nombre_x, nombre_y, nombre_semaphore, nombre_robot),
    )
    conn.commit()
    conn.close()
    return {"id": id_config, "status": "ok"}


def lire_config():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM config LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}


def modifier_config(id_config, **champs):
    if not champs:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sets = ", ".join(f"{k} = ?" for k in champs)
    vals = list(champs.values()) + [id_config]
    cursor.execute(f"UPDATE config SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()

# =======================
# Route
# =======================

@router.post("/add_config")
def add_config(nombre_x: int, nombre_y: int, nombre_semaphore: int, nombre_robot: int):
    return ajouter_config(nombre_x, nombre_y, nombre_semaphore, nombre_robot)


@router.get("/get_config")
def get_config():
    return lire_config()


@router.put("/update_config")
def update_config(nombre_x: int | None = None, nombre_y: int | None = None,
                  nombre_semaphore: int | None = None, nombre_robot: int | None = None):
    config = lire_config()
    if not config:
        return {"status": "error", "detail": "Config introuvable"}
    champs = {}
    if nombre_x is not None:
        champs["nombre_x"] = nombre_x
    if nombre_y is not None:
        champs["nombre_y"] = nombre_y
    if nombre_semaphore is not None:
        champs["nombre_semaphore"] = nombre_semaphore
    if nombre_robot is not None:
        champs["nombre_robot"] = nombre_robot
    modifier_config(config["id"], **champs)
    return {"id": config["id"], "status": "updated"}
