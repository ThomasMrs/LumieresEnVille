import sqlite3
from uuid import uuid4
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from database import DB_PATH
from gestion import valider_id

router = APIRouter(prefix="/api", tags=["Shape"])

def ajouter_shape(name, image):
    id_shape = str(uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO shape (id, name, image) VALUES (?, ?, ?)",
        (id_shape, name, image),
    )
    conn.commit()
    conn.close()
    return {"id": id_shape, "status": "ok"}


def lire_shape():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shape")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats


def supprimer_shapes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shape")
    conn.commit()
    conn.close()


def modifier_shape(id_shape, **champs):
    if not champs:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sets = ", ".join(f"{k} = ?" for k in champs)
    vals = list(champs.values()) + [id_shape]
    cursor.execute(f"UPDATE shape SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()

# =======================
# Route
# =======================

@router.get("/list_shapes")
def read_shapes():
    return lire_shape()


@router.get("/shape/{id}")
def read_one_shape(id: str):
    if not valider_id("shape", id):
        return HTMLResponse(status_code=404, content="Shape introuvable")
    for s in lire_shape():
        if s["id"] == id:
            return s


@router.post("/add_shape")
def add_shape(name: str, image: str):
    return ajouter_shape(name, image)


@router.put("/update_shape/{id}")
def update_shape(id: str, name: str | None = None, image: str | None = None):
    if not valider_id("shape", id):
        return HTMLResponse(status_code=404, content="Shape introuvable")
    champs = {}
    if name is not None:
        champs["name"] = name
    if image is not None:
        champs["image"] = image
    modifier_shape(id, **champs)
    return {"id": id, "status": "updated"}


@router.delete("/delete_shapes")
def delete_shapes():
    supprimer_shapes()
    return {"status": "deleted"}
