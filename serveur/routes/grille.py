from uuid import uuid4
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
# Couche stockage : tout le SQL est defini dans stockage/*
from stockage.config import lire_config, definir_grille
from stockage.segment import lire_segment, remplacer_segments
from stockage.semaphore import lire_semaphore

router = APIRouter(prefix="/api", tags=["Grille"])


def creer_grille(name):
    """Genere les segments d'une grille rectangulaire a partir de la config
    (nombre_x x nombre_y) puis les enregistre via la couche stockage.

    Pour chaque noeud (x, y) on cree :
      - un segment horizontal vers (x+1, y) si possible ;
      - un segment vertical vers (x, y+1) si possible.
    """
    config = lire_config()
    if not config:
        return None
    nombre_x = config["nombre_x"]
    nombre_y = config["nombre_y"]
    id_grille = str(uuid4())

    segments = []
    for y in range(nombre_y):
        for x in range(nombre_x):
            if x + 1 < nombre_x:
                segments.append((str(uuid4()), x, y, x + 1, y))
            if y + 1 < nombre_y:
                segments.append((str(uuid4()), x, y, x, y + 1))

    definir_grille(config["id"], id_grille, name)
    remplacer_segments(segments)
    return {
        "grille_id": id_grille,
        "name": name,
        "nombre_x": nombre_x,
        "nombre_y": nombre_y,
        "segments": len(segments),
    }


def lire_grille():
    config = lire_config()
    if not config or not config.get("grille_id"):
        return None
    nombre_x = config["nombre_x"]
    nombre_y = config["nombre_y"]
    segments = lire_segment()
    semaphores = lire_semaphore()

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
# Routes
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
