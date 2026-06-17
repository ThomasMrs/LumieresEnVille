from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from gestion import valider_id, valider_coordonnees
from stockage.segment import (
    ajouter_segment,
    lire_segment,
    supprimer_segments,
    modifier_segment,
)

router = APIRouter(prefix="/api", tags=["Segment"])

# =======================
# Routes
# =======================

@router.get("/list_segment")
def read_segment():
    return lire_segment()


@router.get("/segment/{id}")
def read_one_segment(id: str):
    if not valider_id("segment", id):
        return HTMLResponse(status_code=404, content="Segment introuvable")
    for s in lire_segment():
        if s["id"] == id:
            return s


@router.post("/add_segment")
def add_segment(coord_a_x: int, coord_a_y: int, coord_b_x: int, coord_b_y: int):
    if not valider_coordonnees(coord_a_x, coord_a_y):
        return HTMLResponse(status_code=400, content="400 - Point A hors limites de la grille")
    if not valider_coordonnees(coord_b_x, coord_b_y):
        return HTMLResponse(status_code=400, content="400 - Point B hors limites de la grille")
    return ajouter_segment(coord_a_x, coord_a_y, coord_b_x, coord_b_y)


@router.put("/update_segment/{id}")
def update_segment(id: str, coord_a_x: int | None = None, coord_a_y: int | None = None,
                   coord_b_x: int | None = None, coord_b_y: int | None = None):
    if not valider_id("segment", id):
        return HTMLResponse(status_code=404, content="Segment introuvable")
    if coord_a_x is not None or coord_a_y is not None:
        check_x = coord_a_x if coord_a_x is not None else 0
        check_y = coord_a_y if coord_a_y is not None else 0
        if not valider_coordonnees(check_x, check_y):
            return HTMLResponse(status_code=400, content="400 - Point A hors limites de la grille")
    if coord_b_x is not None or coord_b_y is not None:
        check_x = coord_b_x if coord_b_x is not None else 0
        check_y = coord_b_y if coord_b_y is not None else 0
        if not valider_coordonnees(check_x, check_y):
            return HTMLResponse(status_code=400, content="400 - Point B hors limites de la grille")
    champs = {}
    if coord_a_x is not None:
        champs["coord_a_x"] = coord_a_x
    if coord_a_y is not None:
        champs["coord_a_y"] = coord_a_y
    if coord_b_x is not None:
        champs["coord_b_x"] = coord_b_x
    if coord_b_y is not None:
        champs["coord_b_y"] = coord_b_y
    modifier_segment(id, **champs)
    return {"id": id, "status": "updated"}


@router.delete("/delete_segments")
def delete_segments():
    supprimer_segments()
    return {"status": "deleted"}
