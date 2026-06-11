import sqlite3
from uuid import uuid4
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from database import DB_PATH
from routes.config import lire_config

router = APIRouter(prefix="/api", tags=["Grille"])


def creer_grille(name):
    config = lire_config()
    if not config:
        return None
    nombre_x = config["nombre_x"]
    nombre_y = config["nombre_y"]
    id_grille = str(uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE config SET grille_id = ?, grille_name = ? WHERE id = ?", (id_grille, name, config["id"]))
    cursor.execute("DELETE FROM segment")
    segments = []
    for y in range(nombre_y):
        for x in range(nombre_x):
            if x + 1 < nombre_x:
                segments.append((str(uuid4()), x, y, x + 1, y))
            if y + 1 < nombre_y:
                segments.append((str(uuid4()), x, y, x, y + 1))
    cursor.executemany(
        "INSERT INTO segment (id, coord_a_x, coord_a_y, coord_b_x, coord_b_y) VALUES (?, ?, ?, ?, ?)",
        segments,
    )
    conn.commit()
    conn.close()
    return {"grille_id": id_grille, "name": name, "nombre_x": nombre_x, "nombre_y": nombre_y, "segments": len(segments)}


def lire_grille():
    config = lire_config()
    if not config or not config.get("grille_id"):
        return None
    nombre_x = config["nombre_x"]
    nombre_y = config["nombre_y"]
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM segment ORDER BY coord_a_y, coord_a_x")
    segments = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM semaphore")
    semaphores = [dict(row) for row in cursor.fetchall()]
    conn.close()
    noeuds = []
    for y in range(nombre_y):
        for x in range(nombre_x):
            noeud = {"x": x, "y": y, "semaphore": None}
            for s in semaphores:
                if s["coord_x"] == x and s["coord_y"] == y:
                    noeud["semaphore"] = s
            noeuds.append(noeud)
    return {
        "grille_id": config["grille_id"],
        "name": config["grille_name"],
        "nombre_x": nombre_x,
        "nombre_y": nombre_y,
        "noeuds": noeuds,
        "segments": segments,
    }

# =======================
# Route
# =======================

@router.post("/create_grille")
def create_grille(name: str):
    resultat = creer_grille(name)
    if resultat is None:
        return HTMLResponse(status_code=404, content="Config introuvable, ajoutez une config d'abord")
    return resultat


@router.get("/get_grille")
def get_grille():
    grille = lire_grille()
    if grille is None:
        return HTMLResponse(status_code=404, content="Grille introuvable")
    return grille
