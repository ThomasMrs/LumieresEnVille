from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from gestion import (
    valider_id, valider_etat, valider_type_semaphore, valider_coordonnees,
    construire_champs,
)
from stockage.semaphore import (
    ajouter_semaphore,
    lire_semaphore,
    supprimer_semaphores,
    modifier_semaphore,
)

router = APIRouter(prefix="/api", tags=["Semaphore"])


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
        return HTMLResponse(status_code=404, content="404 - Semaphore introuvable")
    if state is not None and not valider_etat(state, "semaphore"):
        return HTMLResponse(status_code=400, content="400 - Etat invalide (Available | Occupied | Disabled)")
    if type is not None and not valider_type_semaphore(type):
        return HTMLResponse(status_code=400, content="400 - Type invalide (table | helice | caractere)")
    if coord_x is not None or coord_y is not None:
        check_x = coord_x if coord_x is not None else 0
        check_y = coord_y if coord_y is not None else 0
        if not valider_coordonnees(check_x, check_y):
            return HTMLResponse(status_code=400, content="400 - Coordonnees hors limites de la grille")
    champs = construire_champs(name=name, state=state, duration=duration, type=type,
                               coord_x=coord_x, coord_y=coord_y)
    try:
        modifier_semaphore(id, **champs)
    except Exception as e:
        return HTMLResponse(status_code=500, content=f"500 - Echec de la modification : {e}")
    return {"id": id, "status": "updated"}


@router.delete("/delete_semaphores")
def delete_semaphores():
    supprimer_semaphores()
    return {"status": "deleted"}
