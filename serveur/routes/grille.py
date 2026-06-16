from uuid import uuid4
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
# Couche stockage : tout le SQL est defini dans stockage/*
from stockage.config import lire_config, definir_grille
from stockage.segment import lire_segment, remplacer_segments
from stockage.semaphore import lire_semaphore
from routes import segment

router = APIRouter(prefix="/api")

# Les segments font partie de la grille : on rattache leur router ici
# (le prefixe "/api" du router grille s'applique => /api/list_segment, etc.)
# Le tag "Grille" est mis sur chaque route grille individuellement pour ne pas
# polluer les routes segment (qui gardent uniquement le tag "Segment").
router.include_router(segment.router)


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

    # Grille centree horizontalement sur x = 0 (ex: nombre_x=5 -> -2,-1,0,1,2).
    x_min = -(nombre_x // 2)
    x_max = x_min + nombre_x  # borne exclusive

    segments = []
    # Base en (0, 0) reliee par un segment vertical au bas de la grille (0, 1).
    segments.append((str(uuid4()), 0, 0, 0, 1))
    # Vraie grille : y va de 1 a nombre_y (au-dessus de la base).
    for y in range(1, nombre_y + 1):
        for x in range(x_min, x_max):
            if x + 1 < x_max:
                segments.append((str(uuid4()), x, y, x + 1, y))
            if y + 1 <= nombre_y:
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

    # Memes bornes que creer_grille : grille centree horizontalement sur x = 0.
    x_min = -(nombre_x // 2)
    x_max = x_min + nombre_x  # borne exclusive

    def construire_noeud(x, y):
        noeud = {"x": x, "y": y, "semaphore": None}
        for s in semaphores:
            if s["coord_x"] == x and s["coord_y"] == y:
                noeud["semaphore"] = s
        return noeud

    noeuds = []
    # Base en (0, 0), puis la vraie grille au-dessus (y de 1 a nombre_y).
    noeuds.append(construire_noeud(0, 0))
    for y in range(1, nombre_y + 1):
        for x in range(x_min, x_max):
            noeuds.append(construire_noeud(x, y))
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

@router.post("/create_grille", tags=["Grille"])
def create_grille(name: str):
    resultat = creer_grille(name)
    if resultat is None:
        return HTMLResponse(status_code=404, content="Config introuvable, ajoutez une config d'abord")
    return resultat


@router.get("/get_grille", tags=["Grille"])
def get_grille():
    grille = lire_grille()
    if grille is None:
        return HTMLResponse(status_code=404, content="Grille introuvable")
    return grille
