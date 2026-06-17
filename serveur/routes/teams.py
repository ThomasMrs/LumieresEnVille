from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from gestion import valider_id
from stockage.team import (
    ajouter_equipe,
    lire_equipe,
    auth_equipe,
    supprimer_equipes,
    modifier_equipes,
)

router = APIRouter(prefix="/api", tags=["Team"])

# =======================
# Routes
# =======================

@router.get("/list_teams")
def read_teams():
    return lire_equipe()


@router.post("/add_team")
def add_team(name: str, ip: str | None = None, allowed: bool = False):
    return ajouter_equipe(name, ip, allowed)


@router.put("/update_team/{id}")
def update_team(id: str, name: str | None = None, ip: str | None = None,
                allowed: bool | None = None):
    if not valider_id("team", id):
        return HTMLResponse(status_code=404, content="Team introuvable")
    champs = {}
    if name is not None:
        champs["name"] = name
    if ip is not None:
        champs["ip"] = ip
    if allowed is not None:
        champs["allowed"] = allowed
    modifier_equipes(id, **champs)
    return {"id": id, "status": "updated"}


@router.delete("/delete_teams")
def delete_teams():
    supprimer_equipes()
    return {"status": "deleted"}


@router.get("/list_teams_allowed")
def read_teams_allowed():
    return auth_equipe()
