import sqlite3
import uuid
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Semaphore"])


# --- Accès base de données ---

def ajouter_semaphore(name, state, duration, type_semaphore):
    id_semaphore = str(uuid.uuid4())
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO semaphore (id, name, state, duration, type_semaphore) VALUES (?, ?, ?, ?, ?)",
        (id_semaphore, name, state, duration, type_semaphore),
    )
    conn.commit()
    conn.close()


def lire_semaphore():
    conn = sqlite3.connect("lumieres.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM semaphore")
    resultat = [dict(ligne) for ligne in cursor.fetchall()]
    conn.close()
    return resultat


def supprimer_semaphores():
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM semaphore")
    conn.commit()
    conn.close()


def modifier_semaphore(id_semaphore, name, state, duration):
    conn = sqlite3.connect("lumieres.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE semaphore SET name = ?, state = ?, duration = ? WHERE id = ?",
        (name, state, duration, id_semaphore),
    )
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
def add_semaphore(name: str, state: str, type_semaphore : str,duration: int | None = None):
    return ajouter_semaphore(name, state, duration, type_semaphore)


@router.put("/update_semaphore/{id}")
def update_semaphore(id: str, name: str, state: str, duration: int):
    return modifier_semaphore(id, name, state, duration)


@router.delete("/delete_semaphores")
def delete_semaphores():
    return supprimer_semaphores()