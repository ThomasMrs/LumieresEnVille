from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from gestion import (
    valider_id, valider_etat, valider_type_semaphore, valider_coordonnees,
    ETATS_SEMAPHORE_ROBOT, TYPE_SEMAPHORE,
)
from stockage.config import lire_config
from stockage.semaphore import (
    ajouter_semaphore,
    lire_semaphore,
    supprimer_semaphores,
    modifier_semaphore,
)

router = APIRouter(prefix="/api", tags=["Semaphore"])

# =======================
# Routes
# =======================

@router.get("/list_semaphore")
def read_semaphore():
    return lire_semaphore()


@router.get("/semaphore/{id}")
def read_one_semaphore(id: str):
    if not valider_id("semaphore", id):
        return HTMLResponse(status_code=404, content="Semaphore introuvable")
    for s in lire_semaphore():
        if s["id"] == id:
            return s

@router.post("/add_semaphore")
def add_semaphore(name: str, duration: int, type: str, coord_x: int, coord_y: int):
    if not valider_type_semaphore(type):
        return HTMLResponse(status_code=400, content="400 - Type invalide (table | helice | caractere)")
    if not valider_coordonnees(coord_x, coord_y):
        return HTMLResponse(status_code=400, content="400 - Coordonnees hors limites de la grille")
    return ajouter_semaphore(name, duration, type, coord_x, coord_y)

@router.put("/update_semaphore/{id}")
def update_semaphore(id: str, name: str | None = None, state: str | None = None,
                     duration: int | None = None, type: str | None = None,
                     coord_x: int | None = None, coord_y: int | None = None):
    if not valider_id("semaphore", id):
        return HTMLResponse(status_code=404,
            content=f"404 - Semaphore introuvable : aucun semaphore avec id='{id}'. "
                    f"Verifiez l'id via GET /api/list_semaphore.")
    if state is not None and not valider_etat(state, "semaphore"):
        return HTMLResponse(status_code=400,
            content=f"400 - Etat invalide : recu state='{state}'. "
                    f"Attendu l'un de {sorted(ETATS_SEMAPHORE_ROBOT)} (sensible a la casse).")
    if type is not None and not valider_type_semaphore(type):
        return HTMLResponse(status_code=400,
            content=f"400 - Type invalide : recu type='{type}'. "
                    f"Attendu l'un de {sorted(TYPE_SEMAPHORE)} (sensible a la casse, minuscules).")
    if coord_x is not None or coord_y is not None:
        check_x = coord_x if coord_x is not None else 0
        check_y = coord_y if coord_y is not None else 0
        if not valider_coordonnees(check_x, check_y):
            config = lire_config()
            if not config:
                return HTMLResponse(status_code=400,
                    content="400 - Coordonnees invalides : aucune config/grille definie. "
                            "Creez d'abord une grille (POST /api/create_grille).")
            nx, ny = config["nombre_x"], config["nombre_y"]
            x_min = -(nx // 2)
            x_max = x_min + nx - 1
            return HTMLResponse(status_code=400,
                content=f"400 - Coordonnees hors limites : recu (x={check_x}, y={check_y}). "
                        f"Attendu x dans [{x_min}, {x_max}] et y dans [1, {ny}], "
                        f"ou la base (0, 0). Grille {nx}x{ny} centree sur x=0.")
    champs = {}
    if name is not None:
        champs["name"] = name
    if state is not None:
        champs["state"] = state
    if duration is not None:
        champs["duration"] = duration
    if type is not None:
        champs["type"] = type
    if coord_x is not None:
        champs["coord_x"] = coord_x
    if coord_y is not None:
        champs["coord_y"] = coord_y
    try:
        modifier_semaphore(id, **champs)
    except Exception as e:
        return HTMLResponse(status_code=500,
            content=f"500 - Echec de la modification : {e.__class__.__name__}: {e}. "
                    f"Champs envoyes : {champs}.")
    return {"id": id, "status": "updated"}


@router.delete("/delete_semaphores")
def delete_semaphores():
    supprimer_semaphores()
    return {"status": "deleted"}
