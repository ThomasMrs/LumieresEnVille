from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from gestion import valider_id, valider_etat
# Couche stockage : tout le SQL est defini dans stockage/mission.py
from stockage.mission import (
    ajouter_missions,
    lire_missions,
    supprimer_missions,
    modifier_missions,
)

router = APIRouter(prefix="/api", tags=["Mission"])

# =======================
# Routes
# =======================

@router.get("/list_missions")
def read_missions():
    return lire_missions()


@router.get("/get_missions")
def get_missions(team: str):
    return [m for m in lire_missions() if m["team"] == team]


@router.get("/missions/available")
def get_available_missions(team: str | None = None):
    """Renvoie les missions qu'un robot disponible peut prendre :
    etat 'Awaiting' et aucun robot encore assigne.
    On peut filtrer par equipe avec le parametre 'team'.
    """
    disponibles = [
        m for m in lire_missions()
        if m["state"] == "Awaiting" and not m["robot_id"]
    ]
    if team:
        disponibles = [m for m in disponibles if m["team"] == team]
    return disponibles


@router.post("/add_mission")
def add_mission(semaphore_id: str, shape_id: str, team: str,
                name: str | None = None, robot_id: str | None = None,
                start_date: str = "", end_date: str = "", time: str = ""):
    if not valider_id("semaphore", semaphore_id):
        return HTMLResponse(status_code=404, content="Semaphore introuvable")
    if not valider_id("shape", shape_id):
        return HTMLResponse(status_code=404, content="Shape introuvable")
    if robot_id and not valider_id("robot", robot_id):
        return HTMLResponse(status_code=404, content="Robot introuvable")
    id_mission = ajouter_missions(name, semaphore_id, robot_id, "Awaiting", start_date, end_date, team, time, shape_id)
    return {"id": id_mission, "status": "ok"}


@router.put("/update_mission/{id}")
def update_mission(id: str, name: str | None = None, semaphore_id: str | None = None,
                   robot_id: str | None = None, shape_id: str | None = None,
                   state: str | None = None, start_date: str | None = None,
                   end_date: str | None = None, team: str | None = None,
                   time: str | None = None):
    if not valider_id("mission", id):
        return HTMLResponse(status_code=404, content="Mission introuvable")
    if state is not None and not valider_etat(state, "mission"):
        return HTMLResponse(status_code=400, content="Etat invalide (Awaiting | Pending_robot | Pending_semaphore | Done)")
    if semaphore_id and not valider_id("semaphore", semaphore_id):
        return HTMLResponse(status_code=404, content="Semaphore introuvable")
    if shape_id and not valider_id("shape", shape_id):
        return HTMLResponse(status_code=404, content="Shape introuvable")
    if robot_id and not valider_id("robot", robot_id):
        return HTMLResponse(status_code=404, content="Robot introuvable")
    champs = {}
    if name is not None:
        champs["name"] = name
    if semaphore_id is not None:
        champs["semaphore_id"] = semaphore_id
    if robot_id is not None:
        champs["robot_id"] = robot_id
    if state is not None:
        champs["state"] = state
    if start_date is not None:
        champs["start_date"] = start_date
    if end_date is not None:
        champs["end_date"] = end_date
    if team is not None:
        champs["team"] = team
    if shape_id is not None:
        champs["shape_id"] = shape_id
    if time is not None:
        champs["time"] = time
    modifier_missions(id, **champs)
    return {"id": id, "status": "updated"}


@router.delete("/delete_missions")
def delete_missions():
    supprimer_missions()
    return {"status": "deleted"}
