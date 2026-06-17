from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from gestion import valider_id, valider_etat, construire_champs
from stockage.mission import (
    ajouter_missions,
    lire_missions,
    supprimer_missions,
    modifier_missions,
)

router = APIRouter(prefix="/api", tags=["Mission"])

@router.get("/list_missions")
def read_missions():
    return lire_missions()


@router.get("/get_missions")
def get_missions(team: str):
    return [m for m in lire_missions() if m["team"] == team]

@router.get("/list_missions_by_team")
def list_missions_by_team(team: str):
    """Renvoie les missions creees par le controleur de cette team"""
    return [m for m in lire_missions() if m["team"] == team]


@router.get("/missions/available")
def get_available_missions(team: str | None = None):
    """Renvoie les missions qu'un robot disponible peut prendre :
    etat 'Awaiting' et aucun robot encore assigne
    On peut filtrer par equipe avec le parametre 'team'
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
                start_date: str = "", end_date: str = "", time: str = "",
                color_r: int = 0, color_g: int = 0, color_b: int = 0):
    if not valider_id("semaphore", semaphore_id):
        return HTMLResponse(status_code=404, content="Semaphore introuvable")
    if not valider_id("shape", shape_id):
        return HTMLResponse(status_code=404, content="Shape introuvable")
    if robot_id and not valider_id("robot", robot_id):
        return HTMLResponse(status_code=404, content="Robot introuvable")
    id_mission = ajouter_missions(name, semaphore_id, robot_id, "Awaiting", start_date, end_date,
                                  team, time, shape_id, color_r, color_g, color_b)
    return {"id": id_mission, "status": "ok"}


@router.put("/update_mission/{id}")
def update_mission(id: str, name: str | None = None, semaphore_id: str | None = None,
                   robot_id: str | None = None, shape_id: str | None = None,
                   state: str | None = None, start_date: str | None = None,
                   end_date: str | None = None, team: str | None = None,
                   time: str | None = None, color_r: int | None = None,
                   color_g: int | None = None, color_b: int | None = None):
    if not valider_id("mission", id):
        return HTMLResponse(status_code=404, content="404 - Mission introuvable")
    if state is not None and not valider_etat(state, "mission"):
        return HTMLResponse(status_code=400,
            content="400 - Etat invalide (Awaiting | Pending_robot | Pending_semaphore | Done)")
    if semaphore_id and not valider_id("semaphore", semaphore_id):
        return HTMLResponse(status_code=404, content="404 - Semaphore introuvable")
    if shape_id and not valider_id("shape", shape_id):
        return HTMLResponse(status_code=404, content="404 - Shape introuvable")
    if robot_id and not valider_id("robot", robot_id):
        return HTMLResponse(status_code=404, content="404 - Robot introuvable")
    champs = construire_champs(name=name, semaphore_id=semaphore_id, robot_id=robot_id,
                               state=state, start_date=start_date, end_date=end_date,
                               team=team, shape_id=shape_id, time=time,
                               color_r=color_r, color_g=color_g, color_b=color_b)
    try:
        modifier_missions(id, **champs)
    except Exception as e:
        return HTMLResponse(status_code=500, content=f"500 - Echec de la modification : {e}")
    return {"id": id, "status": "updated"}


@router.delete("/delete_missions")
def delete_missions():
    supprimer_missions()
    return {"status": "deleted"}
