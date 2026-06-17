from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from gestion import valider_id, valider_etat
from stockage.robot import (
    ajouter_robots,
    lire_robots,
    supprimer_robots,
    modifier_robots,
)
from stockage.mission import lire_missions

router = APIRouter(prefix="/api", tags=["Robot"])

# =======================
# Routes
# =======================

@router.get("/list_robots")
def read_robots():
    return lire_robots()


@router.get("/robot/{id}")
def read_one_robot(id: str):
    if not id:
        return HTMLResponse(status_code=400, content="400 - ID manquant")
    if not valider_id("robot", id):
        return HTMLResponse(status_code=404, content="404 - Robot introuvable")
    for r in lire_robots():
        if r["id"] == id:
            return r
    return HTMLResponse(status_code=500, content="500 - Erreur interne")


@router.get("/robot/{id}/mission")
def read_robot_missions(id: str):
    if not valider_id("robot", id):
        return HTMLResponse(status_code=404, content="Robot introuvable")
    return [m for m in lire_missions() if m["robot_id"] == id]


@router.post("/add_robot")
def add_robot(name: str | None = None, speed: int | None = None,
              position_x: int | None = None, position_y: int | None = None):
    champs = {}
    if name is not None:
        champs["name"] = name
    if speed is not None:
        champs["speed"] = speed
    if position_x is not None:
        champs["position_x"] = position_x
    if position_y is not None:
        champs["position_y"] = position_y
    id_robot = ajouter_robots(**champs)
    return {"id": id_robot, "status": "ok"}


@router.put("/update_robot/{id}")
def update_robot(id: str, name: str | None = None, state: str | None = None,
                 speed: int | None = None, position_x: int | None = None,
                 position_y: int | None = None):
    if not valider_id("robot", id):
        return HTMLResponse(status_code=404, content="Robot introuvable")
    if state is not None and not valider_etat(state, "robot"):
        return HTMLResponse(status_code=400, content="Etat invalide (Available | Occupied | Disabled)")
    champs = {}
    if name is not None:
        champs["name"] = name
    if state is not None:
        champs["state"] = state
    if speed is not None:
        champs["speed"] = speed
    if position_x is not None:
        champs["position_x"] = position_x
    if position_y is not None:
        champs["position_y"] = position_y
    modifier_robots(id, **champs)
    return {"id": id, "status": "updated"}


@router.delete("/delete_robots")
def delete_robots():
    supprimer_robots()
    return {"status": "deleted"}
