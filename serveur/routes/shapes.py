import sqlite3
import uuid

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Shape"])


# --- Accès base de données ---

def ajouter_shape(name, image):
    id_shape = str(uuid.uuid4())
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO shape (id, name, image) VALUES (?, ?, ?)",
        (id_shape, name, image),
    )
    conn.commit()
    conn.close()


def lire_shape():
    conn = sqlite3.connect("lumieres.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shape")
    resultats = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultats


def supprimer_shapes():
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shape")
    conn.commit()
    conn.close()


def modifier_shape(id_shape, name, image):
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE shape SET name = ?, image = ? WHERE id = ?",
        (name, image, id_shape),
    )
    conn.commit()
    conn.close()


# --- Routes ---

@router.get("/list_shapes")
def read_shapes():
    return lire_shape()

@router.get("/shape/{id}")
def read_one_shape(id: str):
    for s in lire_shape():
        if s["id"] == id:
            return s
    return {}

@router.post("/add_shape")
def add_shape(name: str, image: str):
    return ajouter_shape(name, image)

@router.put("/update_shape/{id}")
def update_shape(id: str, name: str, image: str):
    return modifier_shape(id, name, image)

@router.delete("/delete_shapes")
def delete_shapes():
    return supprimer_shapes()